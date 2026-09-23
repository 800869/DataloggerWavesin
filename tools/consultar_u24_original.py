import os
import time
import select
import termios
import binascii

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

def hx(data):
    return binascii.hexlify(data).decode('ascii').upper()

unit = bytes.fromhex('076351302B9C')
fd = os.open('/dev/ttyS4', os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
old = termios.tcgetattr(fd)
received = False

try:
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
    print('Consulta A2 directa a U24:', hx(request))
    os.write(fd, request)

    pending = b''
    deadline = time.monotonic() + 20

    while time.monotonic() < deadline:
        if not select.select([fd], [], [], 0.2)[0]:
            continue

        chunk = os.read(fd, 1024)
        if not chunk:
            continue

        print('RX:', hx(chunk))
        pending += chunk

        while len(pending) >= 3:
            start = pending.find(b'\x02')
            if start < 0:
                pending = b''
                break

            pending = pending[start:]
            length = pending[1]

            if length < 4:
                pending = pending[1:]
                continue

            total = length + 2
            if len(pending) < total:
                break

            packet = pending[:total]
            pending = pending[total:]
            check = packet[-3] | (packet[-2] << 8)

            if packet[-1] != 3 or crc(packet[1:-3]) != check:
                print('Trama descartada: formato o CRC incorrecto')
                continue

            command = packet[2]
            data = packet[3:-3]
            print('VALIDA comando=%02X datos=%s' % (command, hx(data)))

            if command == 0x06:
                print('Acuse de la base; no confirma lectura de U24.')

            if command == 0x00:
                print('Error comunicado por la base:', hx(data))

            if command == 0x30 and data[:6] == unit:
                payload = data[6:]
                print('MENSAJE DE U24:', hx(payload))

                if payload[:1] == b'\xb2' and len(payload) > 1:
                    received = True
                    print('RESPUESTA B2 CON DATOS: %d bytes adicionales' %
                          (len(payload) - 1))

    if not received:
        print('No se recibio una respuesta B2 con datos en 20 segundos.')

finally:
    termios.tcsetattr(fd, termios.TCSANOW, old)
    os.close(fd)
    print('Prueba terminada; puerto cerrado.')
