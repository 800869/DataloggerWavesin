"""Configuracion explicita; nunca activa automaticamente equipos recuperados."""
import json
import math
from pathlib import Path
import re


def load_config(path):
    path = Path(path).resolve()
    cfg = json.loads(path.read_text(encoding='utf-8-sig'))
    if cfg.get('mode') not in ('simulation', 'ssh'):
        raise ValueError('mode debe ser simulation o ssh')
    for key, default, minimum in [('interval', 600, 1), ('timeout', 15, 1),
                                  ('stale_after', 1200, 1), ('retry_delay', 30, 1)]:
        cfg.setdefault(key, default)
        if not isinstance(cfg[key], (float, int)) or not math.isfinite(cfg[key]) or cfg[key] < minimum:
            raise ValueError('Tiempo invalido: ' + key)
    if cfg['stale_after'] < cfg['interval']:
        raise ValueError('stale_after debe ser >= interval')
    cfg.setdefault('bind', '127.0.0.1')
    cfg.setdefault('port', 1502)
    cfg.setdefault('slave_id', 1)
    for key, limit in [('port', 65535), ('slave_id', 247)]:
        if type(cfg[key]) is not int or not 1 <= cfg[key] <= limit:
            raise ValueError('Fuera de rango: ' + key)
    units = cfg.get('units', [])
    if not units or len(units) > 24:
        raise ValueError('Configurar entre 1 y 24 unidades')
    slots, ids = set(), set()
    for unit in units:
        slot = unit['slot']
        if type(slot) is not int or not 1 <= slot <= 24 or slot in slots:
            raise ValueError('Slot debe ser unico, 1..24')
        slots.add(slot)
        radio_id = unit['radio_id'].upper()
        if not re.fullmatch('[0-9A-F]{12}', radio_id) or radio_id in ids:
            raise ValueError('Direccion radio invalida o duplicada')
        unit['radio_id'] = radio_id
        ids.add(radio_id)
        unit.setdefault('enabled', False)
        unit.setdefault('direct_confirmed', False)
        if type(unit['enabled']) is not bool or type(unit['direct_confirmed']) is not bool:
            raise ValueError('enabled y direct_confirmed deben ser booleanos')
        unit.setdefault('profile', 4)
        unit.setdefault('di_mask', 0)
        unit.setdefault('rs485_mask', 0)
        for key, limit in [('profile', 65535), ('di_mask', 1023), ('rs485_mask', 262143)]:
            if type(unit[key]) is not int or not 0 <= unit[key] <= limit:
                raise ValueError('Campo invalido: ' + key)
        if cfg['mode'] == 'ssh' and unit['enabled'] and not unit['direct_confirmed']:
            raise ValueError('Ruta directa pendiente de validar: slot %d' % slot)
    if cfg['mode'] == 'ssh':
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.@-]*', cfg.get('ssh_target', '')):
            raise ValueError('Configurar ssh_target: alias SSH o usuario@host')
        if not any(u['enabled'] for u in units):
            raise ValueError('No hay unidades habilitadas')
        if sum(u['enabled'] for u in units) * (cfg['timeout'] + 7) + 15 > cfg['interval']:
            raise ValueError('La ronda maxima excede interval; reducir timeout o unidades')
    for key, default in [('database', '../data/database/adquisicion.sqlite'),
                         ('log_dir', '../logs/acquisition')]:
        cfg[key] = (path.parent / cfg.get(key, default)).resolve()
    return cfg
