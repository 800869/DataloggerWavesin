"""Ultima lectura transaccional y muestras; los historicos anteriores no se abren."""
import json
import sqlite3
import threading
import time

STRIDE = 96


def words(value):
    value = min(0xFFFFFFFF, max(0, int(value)))
    return [value >> 16, value & 65535]


class State:
    def __init__(self, cfg, clock=time.time):
        self.cfg, self.clock = cfg, clock
        self.lock = threading.RLock()
        self.units = {u['slot']: u for u in cfg['units']}
        self.last = {}
        self.errors = {}
        self.counts = {slot: [0, 0] for slot in self.units}
        cfg['database'].parent.mkdir(parents=True, exist_ok=True)
        if cfg['database'].exists():
            # No convertir por accidente la base historica u otra SQLite.
            probe = sqlite3.connect(cfg['database'].as_uri() + '?mode=ro', uri=True)
            try:
                tables = {row[0] for row in probe.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
                if tables - {'samples', 'latest'}:
                    raise ValueError('La base contiene tablas ajenas a adquisicion; no se modifica')
            finally:
                probe.close()
        self.db = sqlite3.connect(str(cfg['database']), check_same_thread=False, timeout=5)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS samples ('
                        'id INTEGER PRIMARY KEY, slot INTEGER, radio TEXT, simulated INTEGER,'
                        'received REAL, payload TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS latest ('
                        'slot INTEGER PRIMARY KEY, radio TEXT, simulated INTEGER,'
                        'received REAL, payload TEXT)')
        self.db.commit()
        for slot, radio, sim, received, payload in self.db.execute('SELECT * FROM latest'):
            unit = self.units.get(slot)
            if unit and unit['radio_id'] == radio and sim == (cfg['mode'] == 'simulation'):
                self.last[slot] = (received, json.loads(payload))
                self.errors[slot] = 5  # Restaurado: requiere nueva lectura.

    def update(self, slot, payload):
        timestamp = payload.get('received_at', self.clock())
        unit = self.units[slot]
        data = json.dumps(payload, separators=(',', ':'))
        row = (slot, unit['radio_id'], int(self.cfg['mode'] == 'simulation'), timestamp, data)
        with self.lock:
            # Si falla disco/commit, no publicar la lectura como persistida.
            with self.db:
                self.db.execute('INSERT INTO samples(slot,radio,simulated,received,payload) VALUES (?,?,?,?,?)', row)
                self.db.execute('INSERT OR REPLACE INTO latest VALUES (?,?,?,?,?)', row)
            self.last[slot] = (timestamp, payload)
            self.errors[slot] = 0
            self.counts[slot][0] = min(65535, self.counts[slot][0] + 1)

    def error(self, slot, code=1):
        with self.lock:
            self.errors[slot] = code
            self.counts[slot][1] = min(65535, self.counts[slot][1] + 1)

    def registers(self):
        result = [0] * (24 * STRIDE)
        now = self.clock()
        with self.lock:
            for slot, unit in self.units.items():
                block = [0] * STRIDE
                block[24:32] = [int(self.cfg['mode'] == 'simulation'), 1, unit['profile'],
                                unit['di_mask'], *words(unit['rs485_mask']), 0, 0]
                block[22:24] = self.counts[slot]
                block[71] = self.errors.get(slot, 0)
                if slot not in self.last:
                    block[20:22] = [0 if unit['enabled'] else 3, 65535]
                    block[72:74] = [65535, 65535]
                else:
                    timestamp, payload = self.last[slot]
                    age = max(0, now - timestamp)
                    bad = self.errors.get(slot, 0) or age > self.cfg['stale_after'] or now < timestamp
                    block[20:22] = [3 if not unit['enabled'] else (2 if bad else 1), min(65535, int(age))]
                    for i, value in enumerate(payload['di']):
                        block[i * 2:i * 2 + 2] = words(value)
                    for i, value in enumerate(payload['rs485']):
                        block[32 + i * 2:34 + i * 2] = words(value)
                    block[68:70] = payload['analog']
                    block[70] = payload['status_raw']
                    block[72:74] = words(age)
                    block[74:76] = words(timestamp)
                result[(slot - 1) * STRIDE:slot * STRIDE] = block
        return result

    def close(self):
        self.db.close()
