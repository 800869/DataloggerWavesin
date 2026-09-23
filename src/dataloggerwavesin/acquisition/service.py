"""Coordinador PC: un ciclo cada 600 s, reintentos acotados, TCP independiente."""
import argparse
import logging
from logging.handlers import RotatingFileHandler
import signal
import sqlite3
import threading
import time

from .collector import collect, synthetic
from .config import load_config
from .modbus import ModbusServer
from .state import State
from .instance import InstanceLock

LOG = logging.getLogger('acquisition')


def cycle(cfg, state, step, reader=collect):
    enabled = [u for u in cfg['units'] if u['enabled']]
    try:
        results = ({u['slot']: synthetic(u['slot'], step) for u in enabled}
                   if cfg['mode'] == 'simulation' else reader(cfg))
    except OSError:
        LOG.exception('SSH no disponible')
        results = {}
    good = 0
    for unit in enabled:
        slot = unit['slot']
        if results.get(slot) is None:
            state.error(slot, 1)
            LOG.warning('Sin lectura valida: slot %d', slot)
        else:
            try:
                state.update(slot, results[slot])
                good += 1
                LOG.info('Lectura persistida: slot %d', slot)
            except sqlite3.Error:
                state.error(slot, 4)
                LOG.exception('No se pudo persistir slot %d', slot)
    return good


def acquisition_loop(cfg, state, stop):
    step, backoff = 0, cfg['retry_delay']
    while not stop.is_set():
        start = time.monotonic()
        good = cycle(cfg, state, step)
        step += 1
        if good:
            backoff = cfg['retry_delay']
            delay = max(1, cfg['interval'] - (time.monotonic() - start))
        else:
            delay = min(backoff, cfg['interval'])
            backoff = min(backoff * 2, cfg['interval'])
        stop.wait(delay)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--check', action='store_true', help='Valida sin SSH ni escrituras')
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.check:
        print('Configuracion valida; modo=%s; unidades=%d' % (cfg['mode'], len(cfg['units'])))
        return 0
    cfg['log_dir'].mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                        handlers=[logging.StreamHandler(), RotatingFileHandler(
                            cfg['log_dir'] / 'acquisition.log', maxBytes=2_000_000,
                            backupCount=5, encoding='utf-8')])
    instance = InstanceLock(cfg['database'].with_suffix('.lock'))
    try:
        state = State(cfg)
    except Exception:
        instance.close()
        raise
    stop = threading.Event()
    # Bind antes del lector: una segunda instancia no llega a usar SSH/radio.
    try:
        server = ModbusServer((cfg['bind'], cfg['port']), state, cfg['slave_id'])
    except Exception:
        state.close()
        instance.close()
        raise
    worker = threading.Thread(target=acquisition_loop, args=(cfg, state, stop), daemon=True)
    tcp = threading.Thread(target=server.serve_forever, daemon=True)
    def terminate(signum, frame):
        stop.set()
    for name in ('SIGTERM', 'SIGINT', 'SIGBREAK'):
        if hasattr(signal, name):
            signal.signal(getattr(signal, name), terminate)
    LOG.info('Arranque modo=%s TCP=%s:%d intervalo=%ss', cfg['mode'], cfg['bind'], cfg['port'], cfg['interval'])
    tcp.start()
    worker.start()
    try:
        while not stop.wait(1):
            if not worker.is_alive() or not tcp.is_alive():
                raise RuntimeError('Hilo de servicio detenido; supervisor debe reiniciar')
    finally:
        stop.set()
        # collect tiene limite total; esperar preserva la transaccion en curso.
        worker.join()
        server.shutdown()
        server.server_close()
        tcp.join()
        state.close()
        instance.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
