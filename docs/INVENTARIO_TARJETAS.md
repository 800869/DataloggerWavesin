# Inventario y capacidad: evidencia y limites

## Fuentes revisadas

- `data/raw/extraido/home/actemium/apps/xthreeconpi/config/units.txt`: 24 filas.
- `docs/private/INFORME_BEAGLEBONE.md`: sistema Java y perfiles historicos.
- Manual ViewGest, pagina impresa 40 (pagina 41 del PDF), indexacion MicroRTU:
  DI 1..10, analogicas 1..2, RS485 1..18. Es capacidad de indexacion del sistema,
  no una ficha electrica que garantice todos esos bornes en cada placa.
- `data/processed/java_estatico/classes_eUnit.txt`, `processInstantTcp`: B2 usa
  eLog tipo 24 independientemente del tipo de historico.
- `classes_eLog.txt`, rama 24: diez uint32, dos uint16 y dieciocho uint32.
- Ensayos aportados por el usuario: U24 DI1 y DI2; U13 confirmada como segunda
  tarjeta disponible con expansion RS485. U13 no tiene aun una captura B2 validada.

## Configuracion recuperada

| Unidad | Tipo historico | Analizador | Canales RS configurados | Repetidores | Base Modbus nueva |
|---|---:|---|---:|---:|---:|
| U01 | 7 | Si | 10 | 2 | 0 |
| U02 | 7 | Si | 8 | 2 | 96 |
| U03 | 7 | Si | 10 | 2 | 192 |
| U04 | 7 | Si | 8 | 0 | 288 |
| U05 | 6 | Si | 2 | 1 | 384 |
| U06 | 7 | Si | 8 | 0 | 480 |
| U07 | 7 | Si | 10 | 3 | 576 |
| U08 | 7 | Si | 10 | 3 | 672 |
| U09 | 7 | Si | 10 | 3 | 768 |
| U10 | 7 | Si | 10 | 3 | 864 |
| U11 | 6 | Si | 4 | 1 | 960 |
| U12 | 6 | Si | 4 | 2 | 1056 |
| U13 | 6 | Si | 4 | 1 | 1152 |
| U14 | 6 | Si | 2 | 2 | 1248 |
| U15 | 4 | No | 0 | 1 | 1344 |
| U16 | 4 | No | 0 | 3 | 1440 |
| U17 | 4 | No | 0 | 3 | 1536 |
| U18 | 4 | No | 0 | 0 | 1632 |
| U19 | 4 | No | 0 | 1 | 1728 |
| U20 | 4 | No | 0 | 2 | 1824 |
| U21 | 4 | No | 0 | 2 | 1920 |
| U22 | 4 | No | 0 | 2 | 2016 |
| U23 | 4 | No | 0 | 2 | 2112 |
| U24 | 4 | No | 0 | 1 | 2208 |

Totales: **10 tipo 4, 5 tipo 6, 9 tipo 7; 14 analizadores habilitados y 100
canales RS configurados**. `false` en units.txt deshabilita el analizador, NO
la remota. Las 24 tienen historicos. La configuracion no prueba que hoy esten
instaladas o accesibles las 24.

La estructura de lectura reserva por remota 10 DI, 2 analogicas brutas y 18 RS
brutos: 240 / 48 / 432 campos para 24 remotas. Son limites del mapa propuesto,
NO 432 puntos RS instalados ni una certificacion de capacidad fisica.

U13 tiene cuatro canales configurados: esclavo 2 direcciones 53 y 55 y esclavo
3 direcciones 53 y 55; cada entrada pide dos palabras, conversion 0. No se
conoce aun el modelo del analizador ni su escala/unidad. U24 no habilita
analizador. Ambas tenian U06 como repetidor configurado; solo U24 ha respondido
por consulta directa. No se alteran esas rutas en la copia original.

Los perfiles historicos 4/6/7 almacenan subconjuntos (4 contadores DI / 4 RS /
12 RS respectivamente). No aplicar esos offsets al B2 instantaneo. El nuevo
lector exige B2 de exactamente 131 bytes; una variante se rechaza y conserva
el ultimo valor con calidad de fallo.

## Decodificacion instantanea

Offsets desde el byte B2, contando B2 como 0:

| Bytes | Campo |
|---|---|
| 0 | B2 |
| 1..10 | Cabecera/reloj; se conserva en raw, no se usa para frescura |
| 11..12 | Estado bruto, mapa de bits desconocido |
| 13..14 | Campo bruto que Java escala por 5/4096; no se expone como magnitud fisica |
| 15..54 | 10 contadores uint32 big-endian |
| 55..58 | 2 campos uint16 analogicos brutos |
| 59..130 | 18 campos uint32 RS brutos |

DI1/DI2 de U24 tienen asociacion de campo respaldada; DI3..DI10 requieren ensayo.
Cinco maniobras de DI1 dieron cuatro incrementos en una prueba: no se certifica
un pulso por cierre ni antirrebote. Un contador no equivale a un estado ON/OFF.
Los ceros RS de una tarjeta sin analizador no son lecturas validas.

## Trabajo pendiente de campo

1. Capturar B2 de U13 por A2 y verificar longitud, CRC e identidad.
2. Comparar sus DI y sus cuatro canales RS con entradas/analizadores conocidos.
3. Confirmar formato, escala, signo y cadencia de actualizacion interna RS.
4. Validar las rutas Wavenis con repetidores antes de habilitar las otras 22.
5. Ensayar reinicio Beagle, perdida/restablecimiento de red y reinicio PC.

No se implementan escrituras de reloj, configuracion Modbus de las remotas,
resets GPIO, ACK especulativos, borrado ni descarga de historicos de campo.

## Ampliacion documental

La revision visual de las fotos confirma en U13 la expansion STM-X3-2AI-RS485-1,
con dos AI seleccionables 0?10 V / 4?20 mA y rotulo Modbus RTU. El inventario
de equipos/canales, limites y evidencias esta en [DISPOSITIVOS_Y_SENALES.md](DISPOSITIVOS_Y_SENALES.md).
