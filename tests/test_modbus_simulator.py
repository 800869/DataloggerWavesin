"""Simulacion local: diez canales, fallo, recuperacion y lectura TCP."""
from pathlib import Path
import socket
import struct
import sys
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from simulador_modbus import Simulation, ModbusServer
from puente_u24_modbus import recv_exact


class SimulatorTests(unittest.TestCase):
    def test_failure_preserves_values_and_recovers(self):
        now = [0]
        state = Simulation(clock=lambda: now[0])
        state.tick(0)
        self.assertEqual(state.counters, tuple(i * 100000 for i in range(1, 11)))
        now[0] = 20
        state.tick(20, failed=True)
        self.assertEqual(state.counters[0], 100000)
        self.assertEqual(state.registers()[20:], [2, 20, 1, 1, 1])
        state.tick(30)
        self.assertEqual(state.counters, tuple(i * 100030 for i in range(1, 11)))
        self.assertEqual(state.registers()[20:], [1, 0, 2, 1, 1])

    def test_tcp_reads_all_simulated_channels_and_source(self):
        state = Simulation()
        state.tick(7)
        server = ModbusServer(('127.0.0.1', 0), state)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with socket.create_connection(server.server_address, timeout=2) as client:
                client.sendall(bytes.fromhex('000100000006010300000019'))
                header = recv_exact(client, 7)
                self.assertEqual(header, bytes.fromhex('00010000003501'))
                response = recv_exact(client, 52)
                self.assertEqual(response[:2], bytes([3, 50]))
                self.assertEqual(struct.unpack('>10I', response[2:42]), state.counters)
                self.assertEqual(response[-2:], b'\x00\x01')
        finally:
            server.shutdown()
            server.server_close()
            worker.join()
