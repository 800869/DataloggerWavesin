"""Perfil instantaneo B2 reconstruido de eLog(tipo 24), sin conversion fisica."""
import struct


def decode_b2(payload):
    if len(payload) != 131 or payload[0] != 0xB2:
        raise ValueError('Respuesta fuera del perfil B2 de 131 bytes')
    return {
        'di': list(struct.unpack('>10I', payload[15:55])),
        'analog': list(struct.unpack('>2H', payload[55:59])),
        'rs485': list(struct.unpack('>18I', payload[59:131])),
        'status_raw': struct.unpack('>H', payload[11:13])[0],
        'raw': payload.hex(),
    }
