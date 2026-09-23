"""Servidor local de datos FICTICIOS para probar Modbus Poll sin hardware."""
import argparse
import math
import threading
import time

from puente_u24_modbus import ModbusServer, Readings


class Simulation(Readings):
    def registers(self):
        # Mantiene 0..23 del puente; 24 identifica datos ficticios.
        return super().registers() + [1]

    def tick(self, step, failed=False):
        if failed:
            self.error()
        else:
            self.update(tuple(((i + 1) * (100000 + step)) & 0xFFFFFFFF
                              for i in range(10)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=1502)
    parser.add_argument('--interval', type=float, default=1.0)
    parser.add_argument('--fault-cycle', action='store_true',
                        help='Cada 30 pasos: 20 con datos y 10 con fallo simulado')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Puerto fuera de rango')
    if not math.isfinite(args.interval) or args.interval <= 0:
        parser.error('Intervalo debe ser finito y mayor que cero')
    readings = Simulation()
    readings.tick(0)
    server = ModbusServer((args.bind, args.port), readings)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    print('SIMULACION: DATOS FICTICIOS, sin acceso a radio ni BeagleBone.', flush=True)
    print('Modbus TCP %s:%d | Slave ID 1 | FC03/04 | direcciones 0..24' %
          (args.bind, args.port), flush=True)
    print('DI1..DI10: uint32 big-endian, 0..19. Registro 24=1: simulacion.', flush=True)
    print('Ctrl+C para terminar.', flush=True)
    step = 0
    try:
        while True:
            time.sleep(args.interval)
            step += 1
            failed = args.fault_cycle and step % 30 >= 20
            readings.tick(step, failed)
            print('SIMULACION paso=%d estado=%d DI1=%d' %
                  (step, readings.registers()[20], readings.counters[0]), flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
        worker.join()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
