#!/usr/bin/env python3
"""Puente de banco U24 A2 -> Modbus TCP, Python 3.5+, sin paquetes externos.

Ejecutable independiente para enviar por stdin/SSH. No instala servicios ni
escribe archivos. Java debe estar detenido: este proceso utiliza la radio.
FC03/FC04: diez contadores DI1..DI10 en 0..19; diagnostico en 20..23.
La asociacion fisica de DI3..DI10 es provisional. Ver docs/MODBUS_TCP.md.
"""
import argparse
import binascii
import errno
import glob
import math
import os
import select
import signal
import socket
import socketserver
import struct
import subprocess
import threading
import time


def crc(data):
    value = 0
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ (0x8408 if value & 1 else 0)
    return value


def frame(command, data=b''):
    body = bytes([len(data) + 4, command]) + data
    check = crc(body)
    return b'\xff\x02' + body + bytes([check & 255, check >> 8, 3])


def extract_packets(pending):
    """Conserva fragmentos y acepta tramas con CRC correcto, sin enviar ACK."""
    packets = []
    while pending:
        start = pending.find(b'\x02')
        if start < 0:
            return packets, b''
        pending = pending[start:]
        if len(pending) < 2:
            break
        length = pending[1]
        if length < 4:
            pending = pending[1:]
            continue
        total = length + 2
        if len(pending) < total:
            break
        packet = pending[:total]
        check = packet[-3] | (packet[-2] << 8)
        if packet[-1] != 3 or crc(packet[1:-3]) != check:
            pending = pending[1:]
            continue
        packets.append((packet[2], packet[3:-3]))
        pending = pending[total:]
    return packets, pending


def decode_counters(command, data, unit):
    # Solo el perfil B2 observado en U24: 130 bytes tras B2.
    if command != 0x30 or data[:6] != unit:
        return None
    payload = data[6:]
    if len(payload) != 131 or payload[0] != 0xB2:
        return None
    return struct.unpack('>10I', payload[15:55])


class Readings(object):
    def __init__(self, stale_after=30.0, clock=time.monotonic):
        self.lock = threading.Lock()
        self.clock = clock
        self.stale_after = stale_after
        self.counters = (0,) * 10
        self.last_ok = None
        self.failed = False
        self.successes = 0
        self.failures = 0

    def update(self, counters):
        if len(counters) != 10 or any(n < 0 or n > 0xFFFFFFFF for n in counters):
            raise ValueError('Se requieren diez contadores uint32')
        with self.lock:
            self.counters = tuple(counters)
            self.last_ok = self.clock()
            self.failed = False
            self.successes = min(65535, self.successes + 1)

    def error(self):
        with self.lock:
            self.failed = True
            self.failures = min(65535, self.failures + 1)

    def registers(self):
        with self.lock:
            if self.last_ok is None:
                status, age = 0, 65535
            else:
                elapsed = max(0.0, self.clock() - self.last_ok)
                status = 2 if self.failed or elapsed > self.stale_after else 1
                age = min(65535, int(elapsed))
            words = []
            for value in self.counters:
                words.extend((value >> 16, value & 65535))
            return words + [status, age, self.successes, self.failures]


def modbus_response(pdu, registers):
    function = pdu[0]
    if function not in (3, 4):
        return bytes([function | 0x80, 1])
    if len(pdu) != 5:
        return bytes([function | 0x80, 3])
    address, count = struct.unpack('>HH', pdu[1:])
    if not 1 <= count <= 125:
        return bytes([function | 0x80, 3])
    if address + count > len(registers):
        return bytes([function | 0x80, 2])
    values = registers[address:address + count]
    return bytes([function, count * 2]) + struct.pack('>' + 'H' * count, *values)


def recv_exact(sock, count):
    chunks = []
    while count:
        chunk = sock.recv(count)
        if not chunk:
            return None
        chunks.append(chunk)
        count -= len(chunk)
    return b''.join(chunks)


class ModbusHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(10)
        try:
            while True:
                header = recv_exact(self.request, 7)
                if header is None:
                    return
                transaction, protocol, length, unit_id = struct.unpack('>HHHB', header)
                if protocol != 0 or not 2 <= length <= 254:
                    return
                pdu = recv_exact(self.request, length - 1)
                if pdu is None:
                    return
                if unit_id != self.server.unit_id:
                    response = bytes([pdu[0] | 0x80, 11])
                else:
                    response = modbus_response(pdu, self.server.readings.registers())
                self.request.sendall(struct.pack('>HHHB', transaction, 0,
                                                len(response) + 1, unit_id) + response)
        except (OSError, socket.timeout):
            return


class ModbusServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, readings, unit_id=1):
        self.readings = readings
        self.unit_id = unit_id
        socketserver.TCPServer.__init__(self, address, ModbusHandler)


def check_radio_available(port):
    result = subprocess.check_output(
        ['systemctl', 'show', 'xthreeconpi.service', '--no-pager', '-p', 'MainPID'],
        universal_newlines=True, timeout=5).strip()
    if result != 'MainPID=0':
        raise RuntimeError('Detenga xthreeconpi antes de usar la radio: ' + result)
    resolved = os.path.realpath(port)
    for link in glob.glob('/proc/[0-9]*/fd/*'):
        try:
            target = os.readlink(link)
        except OSError:
            continue
        if target.startswith('/') and os.path.realpath(target) == resolved:
            raise RuntimeError('Puerto ocupado: ' + link + ' -> ' + target)


def query_u24(port, unit, timeout, stop):
    # Importados aqui para poder probar el protocolo en Windows sin radio.
    import fcntl
    import termios

    check_radio_available(port)
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    old = None
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        old = termios.tcgetattr(fd)
        cfg = termios.tcgetattr(fd)
        cfg[0] = 0
        cfg[1] = 0
        cfg[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        cfg[3] = 0
        cfg[4] = termios.B9600
        cfg[5] = termios.B9600
        cfg[6][termios.VMIN] = 0
        cfg[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, cfg)
        request = frame(0x22, unit + b'\xa2')
        if os.write(fd, request) != len(request):
            raise OSError('Envio A2 incompleto')
        deadline = time.monotonic() + timeout
        pending = b''
        while not stop.is_set() and time.monotonic() < deadline:
            if not select.select([fd], [], [], 0.2)[0]:
                continue
            try:
                chunk = os.read(fd, 1024)
            except OSError as error:
                if error.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                    continue
                raise
            if not chunk:
                continue
            packets, pending = extract_packets(pending + chunk)
            for command, data in packets:
                counters = decode_counters(command, data, unit)
                if counters is not None:
                    return counters
        if not stop.is_set():
            raise TimeoutError('Sin respuesta B2 valida de la unidad en %.1f s' % timeout)
        return None
    finally:
        try:
            if old is not None:
                termios.tcsetattr(fd, termios.TCSANOW, old)
        finally:
            os.close(fd)


def report(message, stop):
    try:
        print(message, flush=True)
    except OSError:
        # El terminal SSH se ha cerrado: no dejar una adquisicion huerfana.
        stop.set()


def poll_radio(args, unit, readings, stop):
    while not stop.is_set():
        try:
            counters = query_u24(args.serial, unit, args.timeout, stop)
            if counters is not None:
                readings.update(counters)
                report('U24 OK: ' + ' '.join(
                    'DI%d=%d' % (index + 1, value)
                    for index, value in enumerate(counters)), stop)
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            if not stop.is_set():
                readings.error()
                report('RADIO ERROR: %s; se conservan los ultimos valores.' % error, stop)
        stop.wait(args.interval)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit', required=True, help='Direccion radio de U24: 12 digitos hex')
    parser.add_argument('--bind', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=502)
    parser.add_argument('--slave-id', type=int, default=1)
    parser.add_argument('--serial', default='/dev/ttyS4')
    parser.add_argument('--interval', type=float, default=5.0,
                        help='Segundos de espera entre consultas de radio')
    parser.add_argument('--timeout', type=float, default=20.0)
    parser.add_argument('--stale-after', type=float, default=30.0)
    args = parser.parse_args()
    try:
        unit = binascii.unhexlify(args.unit)
    except (binascii.Error, ValueError):
        parser.error('--unit debe contener 12 digitos hexadecimales')
    if len(unit) != 6:
        parser.error('--unit debe contener 12 digitos hexadecimales')
    if not 1 <= args.port <= 65535 or not 1 <= args.slave_id <= 247:
        parser.error('Puerto o Slave ID fuera de rango')
    if any(not math.isfinite(n) or n <= 0 for n in
           (args.interval, args.timeout, args.stale_after)):
        parser.error('Los tiempos deben ser finitos y mayores que cero')
    if os.name != 'posix':
        parser.error('La adquisicion se ejecuta en Linux/BeagleBone, no en Windows')
    stop = threading.Event()
    readings = Readings(args.stale_after)
    worker = None
    watchdog = None
    server = None

    def interrupted(signum, unused_frame):
        raise KeyboardInterrupt()

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGHUP, interrupted)
    try:
        check_radio_available(args.serial)
        server = ModbusServer((args.bind, args.port), readings, args.slave_id)
        print('Modbus TCP escuchando en %s:%d; Slave ID=%d; FC03/04; registros 0..23' %
              (args.bind, args.port, args.slave_id), flush=True)
        print('Estado 0=sin datos, 1=ultima lectura valida, 2=fallo o datos antiguos.', flush=True)
        print('DI1..DI10: contadores uint32 en 0..19, palabra alta primero. '
              'DI3..DI10 pendientes de confirmar en bornes.', flush=True)
        worker = threading.Thread(target=poll_radio, args=(args, unit, readings, stop))
        worker.daemon = True
        worker.start()
        parent = os.getppid()

        def watch_session():
            while not stop.wait(1.0):
                if os.getppid() != parent or not worker.is_alive():
                    stop.set()
                    break
            server.shutdown()

        watchdog = threading.Thread(target=watch_session)
        watchdog.daemon = True
        watchdog.start()
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print('Parando puente...', flush=True)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print('No se puede arrancar: %s' % error, flush=True)
        return 1
    finally:
        stop.set()
        if worker is not None:
            worker.join(args.timeout + 6)
        if watchdog is not None:
            watchdog.join(2)
        if server is not None:
            server.server_close()
        report('Puente detenido. No se ha arrancado Java automaticamente.', stop)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
