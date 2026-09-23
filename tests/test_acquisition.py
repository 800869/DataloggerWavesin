"""Recuperacion, aislamiento, perfil B2 y mapa completo sin hardware."""
import ast
import copy
import json
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from dataloggerwavesin.acquisition import collector
from dataloggerwavesin.acquisition.config import load_config
from dataloggerwavesin.acquisition.instance import InstanceLock
from dataloggerwavesin.acquisition.modbus import ModbusServer, recv_exact
from dataloggerwavesin.acquisition.protocol import decode_b2
from dataloggerwavesin.acquisition.service import cycle
from dataloggerwavesin.acquisition import service
from dataloggerwavesin.acquisition.state import State, STRIDE


def payload():
    raw = bytearray(131)
    raw[0] = 0xB2
    struct.pack_into('>H', raw, 11, 123)
    struct.pack_into('>10I', raw, 15, *[100000 + i for i in range(10)])
    struct.pack_into('>2H', raw, 55, 4000, 4095)
    struct.pack_into('>18I', raw, 59, *[0xFFFFFFFF - i for i in range(18)])
    return bytes(raw)


class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.cfg = load_config(ROOT / 'config/simulacion_flota.json')
        self.cfg['database'] = Path(tmp.name) / 'runtime.sqlite'
        self.now = [10000]

    def state(self):
        state = State(self.cfg, clock=lambda: self.now[0])
        self.addCleanup(state.close)
        return state

    def test_profile_offsets(self):
        sample = decode_b2(payload())
        self.assertEqual(sample['di'], list(range(100000, 100010)))
        self.assertEqual(sample['rs485'], [0xFFFFFFFF - i for i in range(18)])
        self.assertEqual(sample['analog'], [4000, 4095])
        self.assertEqual(sample['status_raw'], 123)
        for invalid in (payload()[:-1], b'\xb1' + payload()[1:]):
            with self.assertRaises(ValueError):
                decode_b2(invalid)

    def test_restart_stale_failure_recovery_and_mode_isolation(self):
        state = State(self.cfg, clock=lambda: self.now[0])
        state.update(24, decode_b2(payload()))
        state.close()
        state = self.state()
        offset = 23 * STRIDE
        self.assertEqual(state.registers()[offset + 20], 2)
        self.assertEqual(state.registers()[offset:offset + 2], [1, 34464])
        state.update(24, decode_b2(payload()))
        self.assertEqual(state.registers()[offset + 20], 1)
        self.now[0] += 1201
        self.assertEqual(state.registers()[offset + 20], 2)
        state.error(24)
        self.assertEqual(state.registers()[offset:offset + 2], [1, 34464])
        self.cfg = copy.deepcopy(self.cfg)
        self.cfg['mode'] = 'ssh'
        real = self.state()
        self.assertEqual(real.registers()[offset + 20], 0)
        self.assertEqual(real.registers()[offset:offset + 2], [0, 0])

    def test_clock_backwards_is_not_healthy(self):
        state = self.state()
        state.update(1, decode_b2(payload()))
        self.now[0] -= 1
        self.assertEqual(state.registers()[20], 2)

    def test_24_units_tcp_distinct_blocks(self):
        state = self.state()
        self.assertEqual(cycle(self.cfg, state, 9), 24)
        server = ModbusServer(('127.0.0.1', 0), state)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with socket.create_connection(server.server_address, timeout=2) as client:
                for slot in range(1, 25):
                    client.sendall(struct.pack('>HHHBBHH', slot, 0, 6, 1, 3, (slot - 1) * STRIDE, 76))
                    h = recv_exact(client, 7)
                    response = recv_exact(client, struct.unpack('>HHHB', h)[2] - 1)
                    self.assertEqual(struct.unpack('>I', response[2:6])[0], slot * 100000 + 9)
                    self.assertEqual(struct.unpack('>I', response[66:70])[0], slot * 1000000 + 9)
                    self.assertEqual(response[50:52], b'\x00\x01')
        finally:
            server.shutdown()
            server.server_close()
            worker.join()

    def test_ssh_partial_timeout_and_identity_check(self):
        self.cfg['ssh_target'] = 'beaglebone-test'
        item = dict(slot=1, radio_id=self.cfg['units'][0]['radio_id'], raw=payload().hex(), elapsed=1)
        output = (json.dumps(item) + '\n').encode()
        with patch.object(collector.subprocess, 'run', side_effect=subprocess.TimeoutExpired('ssh', 3, output=output)):
            result = collector.collect(self.cfg)
        self.assertEqual(result[1]['di'][0], 100000)
        item['radio_id'] = 'FFFFFFFFFFFF'
        with patch.object(collector.subprocess, 'run', return_value=subprocess.CompletedProcess('ssh', 0, json.dumps(item).encode())):
            self.assertEqual(collector.collect(self.cfg), {})
        item['radio_id'] = self.cfg['units'][0]['radio_id']
        del item['elapsed']
        with patch.object(collector.subprocess, 'run', return_value=subprocess.CompletedProcess('ssh', 0, json.dumps(item).encode())):
            self.assertEqual(collector.collect(self.cfg), {})

    def test_retry_backoff_then_normal_interval(self):
        class Stop:
            delays = []
            def is_set(self):
                return len(self.delays) >= 4
            def wait(self, delay):
                self.delays.append(delay)
        stop = Stop()
        with patch.object(service, 'cycle', side_effect=[0, 0, 24, 0]), \
                patch.object(service.time, 'monotonic', return_value=100):
            service.acquisition_loop(self.cfg, None, stop)
        self.assertEqual(stop.delays, [30, 60, 600, 30])

    def test_database_failure_keeps_previous_value(self):
        import sqlite3
        state = self.state()
        cycle(self.cfg, state, 1)
        with patch.object(state, 'update', side_effect=sqlite3.OperationalError('disk full')), \
                self.assertLogs('acquisition', level='ERROR'):
            self.assertEqual(cycle(self.cfg, state, 9), 0)
        self.assertEqual(state.registers()[:2], [1, 34465])
        self.assertEqual(state.registers()[20], 2)
        self.assertEqual(state.registers()[71], 4)

    def test_does_not_modify_foreign_database(self):
        import sqlite3
        db = sqlite3.connect(self.cfg['database'])
        db.execute('create table lecturas(valor integer)')
        db.commit()
        db.close()
        before = self.cfg['database'].read_bytes()
        with self.assertRaises(ValueError):
            State(self.cfg)
        self.assertEqual(self.cfg['database'].read_bytes(), before)

    def test_full_process_restart_tcp_and_sqlite_integrity(self):
        import sqlite3
        cfg = json.loads((ROOT / 'config/simulacion_flota.json').read_text())
        cfg['database'] = str(self.cfg['database'])
        cfg['log_dir'] = str(self.cfg['database'].parent / 'logs')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            cfg['port'] = sock.getsockname()[1]
        path = self.cfg['database'].parent / 'process.json'
        path.write_text(json.dumps(cfg))
        for _ in range(2):
            proc = subprocess.Popen([sys.executable, str(ROOT / 'scripts/adquisicion.py'),
                                     '--config', str(path)], cwd=path.parent,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                deadline = time.monotonic() + 8
                while True:
                    try:
                        with socket.create_connection(('127.0.0.1', cfg['port']), timeout=1) as client:
                            client.sendall(struct.pack('>HHHBBHH', 1, 0, 6, 1, 3, 2208, 25))
                            header = recv_exact(client, 7)
                            data = recv_exact(client, struct.unpack('>HHHB', header)[2] - 1)
                            values = struct.unpack('>25H', data[2:])
                            if values[20] == 1:
                                self.assertEqual(values[24], 1)
                                self.assertEqual((values[0] << 16) + values[1], 2400000)
                                break
                    except OSError:
                        pass
                    if time.monotonic() > deadline or proc.poll() is not None:
                        self.fail('El proceso no publica datos')
                    time.sleep(0.05)
            finally:
                proc.kill()  # Corte forzado solo del proceso de prueba.
                proc.wait(timeout=5)
            db = sqlite3.connect(self.cfg['database'])
            try:
                self.assertEqual(db.execute('pragma integrity_check').fetchone()[0], 'ok')
            finally:
                db.close()

    def test_fault_does_not_zero_counters(self):
        state = self.state()
        cycle(self.cfg, state, 1)
        self.cfg['mode'] = 'ssh'
        with self.assertLogs('acquisition', level='WARNING'):
            self.assertEqual(cycle(self.cfg, state, 2, reader=lambda cfg: {}), 0)
        self.assertEqual(state.registers()[:2], [1, 34465])
        self.assertEqual(state.registers()[20], 2)

    def test_instance_lock(self):
        path = self.cfg['database'].with_suffix('.lock')
        lock = InstanceLock(path)
        try:
            with self.assertRaises(RuntimeError):
                InstanceLock(path)
        finally:
            lock.close()
        InstanceLock(path).close()

    def test_radio_agent_35_and_no_remote_mutations(self):
        source = (ROOT / 'src/dataloggerwavesin/acquisition/radio_agent.py').read_text()
        ast.parse(source, feature_version=(3, 5))
        self.assertNotIn('systemctl stop', source)
        self.assertNotIn('systemctl disable', source)
        self.assertIn("frame(0x22, unit + b'\\xa2')", source)

    def test_validation_rejects_unconfirmed_routes_and_duplicates(self):
        cfg = json.loads((ROOT / 'config/adquisicion.example.json').read_text())
        p = self.cfg['database'].parent / 'test.json'
        cfg['units'][0]['direct_confirmed'] = False
        p.write_text(json.dumps(cfg))
        with self.assertRaises(ValueError):
            load_config(p)
        cfg['mode'] = 'simulation'
        cfg['units'].append(cfg['units'][0])
        p.write_text(json.dumps(cfg))
        with self.assertRaises(ValueError):
            load_config(p)
