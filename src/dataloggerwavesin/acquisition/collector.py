"""Una ronda SSH acotada; no copia archivos ni cambia servicios remotos."""
import base64
import json
from pathlib import Path
import subprocess
import time
import math

from .protocol import decode_b2


def ssh_command(target):
    return ['ssh', '-T', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
            '-o', 'ConnectionAttempts=1', '-o', 'ServerAliveInterval=15',
            '-o', 'ServerAliveCountMax=2', '-o', 'StrictHostKeyChecking=yes',
            target, 'python3 -u -']


def collect(cfg):
    remote = {'timeout': cfg['timeout'], 'units': cfg['units']}
    encoded = base64.b64encode(json.dumps(remote).encode()).decode('ascii')
    source = Path(__file__).with_name('radio_agent.py').read_text(encoding='utf-8')
    source += '\nimport base64\nrun_batch(json.loads(base64.b64decode(%r).decode()))\n' % encoded
    timeout = sum(u['enabled'] for u in cfg['units']) * (cfg['timeout'] + 7) + 15
    # TimeoutExpired conserva salida parcial; run termina y espera al SSH local.
    started = time.time()
    try:
        completed = subprocess.run(ssh_command(cfg['ssh_target']), input=source.encode(),
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   timeout=timeout, check=False)
        output = completed.stdout
    except subprocess.TimeoutExpired as error:
        output = error.stdout or b''
    expected = {u['slot']: u for u in cfg['units'] if u['enabled']}
    results = {}
    for line in output.splitlines():
        try:
            item = json.loads(line)
            slot = item['slot']
            if slot not in expected or item['radio_id'] != expected[slot]['radio_id']:
                continue
            if slot in results:
                results[slot] = None  # No aceptar respuestas duplicadas ambiguas.
                continue
            decoded = decode_b2(bytes.fromhex(item['raw'])) if item.get('raw') else None
            if decoded is not None:
                elapsed = float(item['elapsed'])
                if not math.isfinite(elapsed) or not 0 <= elapsed <= timeout:
                    results[slot] = None
                    continue
                # Estimacion conservadora: no rejuvenecer las primeras lecturas
                # mientras esperamos al resto de la ronda. No usa reloj Beagle.
                decoded['received_at'] = min(time.time(), started + elapsed)
            results[slot] = decoded
        except (ValueError, KeyError, TypeError):
            continue
    return results


def synthetic(slot, step):
    return {'di': [slot * 100000 + i * 1000 + step for i in range(10)],
            'rs485': [slot * 1000000 + i * 1000 + step for i in range(18)],
            'analog': [1000, 2000], 'status_raw': 0, 'raw': 'SIMULATION'}
