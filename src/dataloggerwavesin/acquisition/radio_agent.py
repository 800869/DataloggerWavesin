"""Agente serie Python 3.5; solo A2. Se transmite por stdin, sin instalar archivos."""
import binascii
import errno
import glob
import os
import select
import signal
import subprocess
import threading
import time
import json

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
                if command == 0x30 and data[:6] == unit and len(data[6:]) == 131 and data[6] == 0xB2:
                    return binascii.hexlify(data[6:]).decode('ascii')
        if not stop.is_set():
            raise TimeoutError('Sin respuesta B2 valida de la unidad en %.1f s' % timeout)
        return None
    finally:
        try:
            if old is not None:
                termios.tcsetattr(fd, termios.TCSANOW, old)
        finally:
            os.close(fd)


def run_batch(config):
    def interrupted(signum, frame):
        raise KeyboardInterrupt()
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, interrupted)
    stop = threading.Event()
    started = time.monotonic()
    for unit in config['units']:
        if not unit['enabled']:
            continue
        try:
            raw = query_u24('/dev/ttyS4', binascii.unhexlify(unit['radio_id']),
                            config['timeout'], stop)
            result = {'slot': unit['slot'], 'radio_id': unit['radio_id'], 'raw': raw,
                      'elapsed': time.monotonic() - started}
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            result = {'slot': unit['slot'], 'radio_id': unit['radio_id'], 'error': type(error).__name__}
        try:
            print(json.dumps(result), flush=True)
        except OSError:
            return
