"""Pruebas de radio sintetica y Modbus TCP real por loopback; sin hardware."""
import ast
import importlib.util
from pathlib import Path
import socket
import struct
import sys
import threading
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tools/puente_u24_modbus.py'
spec = importlib.util.spec_from_file_location('bridge', SCRIPT)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
UNIT = bytes.fromhex('001122334455')


def radio_packet(unit=UNIT, counters=None):
    payload = bytearray(131)
    payload[0] = 0xB2
    if counters is None:
        counters = (0x12345678, 5) + (0,) * 8
    struct.pack_into('>10I', payload, 15, *counters)
    return bridge.frame(0x30, unit + payload)


class RadioTests(unittest.TestCase):
    def test_python35_syntax_and_crc_reference(self):
        ast.parse(SCRIPT.read_text(encoding='utf-8'), feature_version=(3, 5))
        self.assertEqual(bridge.crc(b'123456789'), 0x2189)
        self.assertEqual(bridge.frame(0x50, b'\x05').hex(), 'ff02055005e7bd03')

    def test_fragmented_reply_byte_by_byte(self):
        pending = b''
        decoded = []
        for value in radio_packet():
            packets, pending = bridge.extract_packets(pending + bytes([value]))
            decoded.extend(packets)
        self.assertEqual(len(decoded), 1)
        self.assertEqual(bridge.decode_counters(*decoded[0], UNIT),
                         (0x12345678, 5) + (0,) * 8)
        self.assertEqual(pending, b'')

    def test_corrupt_packet_wrong_unit_and_wrong_profile(self):
        raw = bytearray(radio_packet())
        raw[-3] ^= 1
        packets, pending = bridge.extract_packets(bytes(raw))
        self.assertEqual(packets, [])
        packets, pending = bridge.extract_packets(radio_packet())
        self.assertIsNone(bridge.decode_counters(*packets[0], b'\xff' * 6))
        self.assertIsNone(bridge.decode_counters(0x30, UNIT + b'\xb2', UNIT))
        self.assertIsNone(bridge.decode_counters(0x06, b'', UNIT))

    def test_noise_and_multiple_packets(self):
        packets, pending = bridge.extract_packets(b'noise' + radio_packet() + radio_packet())
        self.assertEqual(len(packets), 2)
        self.assertEqual(pending, b'')

    def test_serial_query_restores_port_and_sends_only_a2(self):
        termios = MagicMock()
        termios.CS8, termios.CREAD, termios.CLOCAL = 48, 128, 2048
        termios.B9600, termios.VMIN, termios.VTIME, termios.TCSANOW = 13, 0, 1, 0
        old = [1, 2, 3, 4, 5, 6, [1, 2]]
        termios.tcgetattr.side_effect = [old, [1, 2, 3, 4, 5, 6, [1, 2]]]
        raw = radio_packet()
        request = bridge.frame(0x22, UNIT + b'\xa2')
        with patch.dict(sys.modules, {'termios': termios, 'fcntl': MagicMock()}), \
                patch.object(bridge, 'check_radio_available') as available, \
                patch.object(bridge.os, 'O_NOCTTY', 256, create=True), \
                patch.object(bridge.os, 'O_NONBLOCK', 2048, create=True), \
                patch.object(bridge.os, 'open', return_value=77), \
                patch.object(bridge.os, 'write', return_value=len(request)) as write, \
                patch.object(bridge.os, 'read', side_effect=[raw[:47], raw[47:95], raw[95:]]), \
                patch.object(bridge.os, 'close') as close, \
                patch.object(bridge.select, 'select', return_value=([77], [], [])):
            result = bridge.query_u24('/dev/ttyS4', UNIT, 20, threading.Event())
        self.assertEqual(result, (0x12345678, 5) + (0,) * 8)
        available.assert_called_once_with('/dev/ttyS4')
        write.assert_called_once_with(77, request)
        close.assert_called_once_with(77)
        self.assertEqual(termios.tcsetattr.call_args_list[-1].args, (77, 0, old))


class DataTests(unittest.TestCase):
    def test_quality_age_failure_and_recovery(self):
        now = [100.0]
        state = bridge.Readings(30, clock=lambda: now[0])
        self.assertEqual(state.registers()[20:], [0, 65535, 0, 0])
        state.update((0x12345678, 5) + (0,) * 8)
        self.assertEqual(state.registers()[:4], [0x1234, 0x5678, 0, 5])
        self.assertEqual(state.registers()[20:], [1, 0, 1, 0])
        now[0] += 31
        self.assertEqual(state.registers()[20:22], [2, 31])
        state.error()
        self.assertEqual(state.registers()[:4], [0x1234, 0x5678, 0, 5])
        state.update((7,) * 10)
        self.assertEqual(state.registers()[20:], [1, 0, 2, 1])
        state.error()
        self.assertEqual(state.registers()[20:], [2, 0, 2, 2])


class TcpTests(unittest.TestCase):
    def setUp(self):
        self.readings = bridge.Readings()
        self.readings.update((0x12345678, 5) + (0,) * 8)
        self.server = bridge.ModbusServer(('127.0.0.1', 0), self.readings)
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={'poll_interval': 0.01}, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def connect(self):
        return socket.create_connection(self.server.server_address, timeout=2)

    def response(self, client):
        header = bridge.recv_exact(client, 7)
        self.assertIsNotNone(header)
        transaction, protocol, length, unit = struct.unpack('>HHHB', header)
        return (transaction, protocol, unit,
                bridge.recv_exact(client, length - 1))

    def test_read_holding_registers_wire_response(self):
        with self.connect() as client:
            client.sendall(bytes.fromhex('123400000006010300000004'))
            self.assertEqual(self.response(client),
                             (0x1234, 0, 1, bytes.fromhex('03081234567800000005')))

    def test_split_requests_and_two_messages_in_one_tcp_send(self):
        with self.connect() as client:
            request = bytes.fromhex('000100000006010300000004')
            client.sendall(request[:3])
            client.sendall(request[3:8])
            client.sendall(request[8:])
            self.assertEqual(self.response(client)[0], 1)
            request2 = bytes.fromhex('000200000006010400020002')
            client.sendall(request + request2)
            self.assertEqual(self.response(client)[0], 1)
            self.assertEqual(self.response(client), (2, 0, 1, bytes.fromhex('040400000005')))

    def test_writes_ranges_counts_and_unit_id(self):
        requests = [
            ('000100000006010600000063', '8601'),
            ('000100000006010300170002', '8302'),
            ('000100000006010300000000', '8303'),
            ('00010000000601030000007e', '8303'),
            ('000100000003010300', '8303'),
            ('000100000006020300000002', '830b'),
        ]
        with self.connect() as client:
            for request, expected in requests:
                client.sendall(bytes.fromhex(request))
                self.assertEqual(self.response(client)[3], bytes.fromhex(expected))
        self.assertEqual(self.readings.registers()[0:4], [0x1234, 0x5678, 0, 5])

    def test_invalid_mbap_closes_connection(self):
        for request in ['000100010006010300000004', '00010000000101',
                        '0001000000ff01']:
            with self.connect() as client:
                client.sendall(bytes.fromhex(request))
                try:
                    self.assertEqual(client.recv(1), b'')
                except ConnectionResetError:
                    pass

    def test_live_changes_are_visible_without_reconnect(self):
        with self.connect() as client:
            request = bytes.fromhex('000100000006010300000004')
            client.sendall(request)
            self.response(client)
            self.readings.update((9, 10) + (0,) * 8)
            client.sendall(request)
            self.assertEqual(self.response(client)[3], bytes.fromhex('0308000000090000000a'))

    def test_all_ten_counters_from_fragmented_radio_to_tcp(self):
        # Valores diferentes y >65535 para detectar cruces y orden de palabras.
        expected = tuple((index + 1) * 65536 + 100 + index for index in range(10))
        raw = radio_packet(counters=expected)
        pending = b''
        decoded = []
        for offset in range(0, len(raw), 7):
            packets, pending = bridge.extract_packets(pending + raw[offset:offset + 7])
            decoded.extend(packets)
        self.assertEqual(len(decoded), 1)
        counters = bridge.decode_counters(*decoded[0], UNIT)
        self.readings.update(counters)
        with self.connect() as client:
            client.sendall(bytes.fromhex('000100000006010300000014'))
            response = self.response(client)[3]
            self.assertEqual(response[:2], bytes([3, 40]))
            self.assertEqual(struct.unpack('>10I', response[2:]), expected)
            for index in range(10):
                request = struct.pack('>HHHBBHH', index + 2, 0, 6, 1, 3, index * 2, 2)
                client.sendall(request)
                response = self.response(client)[3]
                self.assertEqual(response[:2], bytes([3, 4]))
                self.assertEqual(struct.unpack('>I', response[2:])[0], expected[index])


if __name__ == '__main__':
    unittest.main()
