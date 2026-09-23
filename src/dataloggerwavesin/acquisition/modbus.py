"""Modbus TCP de solo lectura, clientes limitados y timeout por socket."""
import socket
import socketserver
import struct
import threading

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
    request_queue_size = 16
    daemon_threads = True

    def __init__(self, address, readings, unit_id=1):
        self.slots = threading.BoundedSemaphore(16)
        self.readings = readings
        self.unit_id = unit_id
        socketserver.TCPServer.__init__(self, address, ModbusHandler)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()
