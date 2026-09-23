# Adquisicion PC y mapa Modbus v1

## Operacion

Entrada: `scripts/adquisicion.py --config config/adquisicion.local.json`.
El CMD Iniciar_adquisicion selecciona el interprete como el visor. `--check`
valida sin SSH, sin abrir puertos y sin crear la base. JSON privado ignorado;
los ejemplos publicos no contienen credenciales. La opcion `enabled` habilita
la consulta, independiente del flag analyzer de units.txt original.

Una ronda abre SSH con BatchMode, validacion estricta de host, timeout de conexion
10 s y keepalive 15 s / 2 fallos. Envia el agente Python por stdin. Cada unidad
habilitada recibe una A2 directa; se exige identidad, CRC y perfil B2 exacto.
No se implementan aun rutas con repetidores: `direct_confirmed` es obligatorio
para habilitar una unidad real, aunque exista una ruta historica en el inventario.
No sustituir ese campo por true sin la prueba de campo correspondiente.

Timeout configurado: 15 s/unidad. Presupuesto SSH: N*(timeout+7)+15; 24 unidades
suponen 543 s, menor que 600 s. Es presupuesto de software, no garantia RF.
Una sesion por ronda simplifica recuperar reinicios y no deja agentes residentes
entre rondas. La salida parcial se aprovecha incluso si expira el timeout local.
No hay ACK, configuracion de repetidores, ajustes de reloj ni consultas historicas.

El PC recibe el conjunto al terminar la ronda. Cada lectura conserva una estimacion
conservadora de instante (inicio PC + tiempo monotono del agente); el retraso de
conexion hace que parezca ligeramente mas antigua, nunca usa el reloj Beagle.
Hasta que termina la ronda se sirven los datos anteriores. Stale: 1200 s.
Fallo de una unidad mantiene sus valores y permite actualizar las otras.
Fallo de todas: espera 30, 60, 120, 240, 480, 600 s entre intentos.
Tras una ronda con algun exito vuelve al intervalo ordinario de 600 s.

## Direccionamiento estable

Un solo Slave/Unit ID=1. Funcion 03 y 04, solo lectura. Escrituras devuelven
excepcion 01. Direcciones fuera de rango: 02; cantidades invalidas: 03; otro
Unit ID: 0B. Limite por peticion: 125 registros. No pedir las 24 unidades juntas.

**Base de Uxx = (xx - 1) * 96**. 24 bloques: registros 0..2303. Un slot nunca
se compacta al deshabilitar una unidad. El nombre Uxx corresponde a slot xx.
U13 base 1152; U24 base 2208. Todos los uint32: palabra alta, palabra baja;
bytes de red big-endian. Sin escalas, sin flotantes y sin reinterpretar negativos.

| Offset desde base | Cantidad | Tipo | Significado |
|---|---:|---|---|
| 0..19 | 20 | 10 uint32 | Contadores DI1..DI10 |
| 20 | 1 | uint16 | 0 sin datos, 1 lectura reciente, 2 fallo/antigua, 3 deshabilitada |
| 21 | 1 | uint16 | Edad segundos, saturada a 65535; sin datos=65535 |
| 22 | 1 | uint16 | Exitos desde arranque, saturado |
| 23 | 1 | uint16 | Fallos desde arranque, saturado |
| 24 | 1 | uint16 | Origen: 0 real, 1 simulacion |
| 25 | 1 | uint16 | Version del mapa: 1 |
| 26 | 1 | uint16 | Tipo historico configurado (4/6/7) |
| 27 | 1 | bits | DI asociados/validados; bit 0=DI1 |
| 28..29 | 2 | uint32 bits | RS validados; bit 0=RS1 |
| 30..31 | 2 | reservado | Cero |
| 32..67 | 36 | 18 uint32 | Campos RS1..RS18 brutos, sin escala |
| 68..69 | 2 | 2 uint16 | Campos analogicos brutos |
| 70 | 1 | uint16 | Estado de remota bruto, bits pendientes |
| 71 | 1 | uint16 | 0 sin error, 1 fallo adquisicion, 4 persistencia, 5 restaurado |
| 72..73 | 2 | uint32 | Edad completa, sin datos=0xFFFFFFFF |
| 74..75 | 2 | uint32 | Epoch UTC estimado de recepcion |
| 76..95 | 20 | reservado | Cero |

Bloques sin configurar quedan a cero y version=0. No usar su estado como calidad
valida. En unidades habilitadas interpretar valores solo con estado=1, origen
esperado y bit de canal validado. Estado 1 prueba recepcion B2, NO que el equipo
RS haya actualizado realmente el campo: falta identificar calidad interna RS.
Las mascaras se configuran solo tras ensayos; en la simulacion todos los bits se
activan para ejercitar el mapa. En la configuracion privada U24 tiene DI mask=3,
U13 RS mask=0. No se cambian automaticamente en runtime.

## Modbus Poll

Conectar TCP/IP, puerto 1502, Slave ID 1. Definir funcion 03, direccion base,
cantidad 20 y scan 1000 ms. Seleccionar TODAS las celdas y Display -> 32-bit
Unsigned -> Big-endian, sin swap. Los 20 registros contienen diez valores.
La celda de la segunda palabra puede verse como --. Un numero negativo en una
palabra suelta suele indicar visualizacion signed16, no un contador negativo.
En la captura aportada, las palabras 3 y 4482 forman 201090; las palabras
4 y -26045 (39491 sin signo) forman 301635. Son exactamente 2 y 3 veces
100545, como genera el simulador simple: la captura respalda mezcla de formatos.
Para diagnostico usar otra ventana, base+20, cantidad 10, unsigned16 (las mascaras
RS de 28..29 se combinan como uint32 si se quieren leer numericamente).
RS: base+32, cantidad 36, unsigned32 big-endian. Analogicas: base+68, cantidad 2,
unsigned16. El simulador antiguo de diez canales mantiene su mapa 0..24.

## Persistencia y limites

Base NUEVA en data/database/adquisicion.sqlite: samples guarda cada lectura
aceptada con identidad, origen, timestamp y payload bruto; latest guarda la ultima.
Se actualizan en una transaccion antes de publicar en RAM. No se abre historicos.sqlite.
WAL + synchronous FULL; no garantiza supervivencia a disco averiado. Error de
commit retiene ultimo valor y marca error 4. No recuperar ni reemplazar una base
corrupta automaticamente. El fallo de inicio queda para diagnostico/supervisor.

Al arrancar solo restaura filas con radio_id/origen coincidentes; calidad 2/error5
hasta una nueva lectura. Un cambio de tarjeta o de modo no hereda valores de otra.
Contadores de diagnostico 22/23 reinician con el proceso. Las muestras permanecen.
Copias coherentes deben usar SQLite backup o parar el servicio; no copiar solo
el .sqlite mientras hay un WAL activo. No hay borrado automatico de muestras.

## Verificacion

Tests: 24 bloques por TCP, offsets B2, persistencia/reinicio, reloj atrasado,
fallos sin ceros, timeout SSH parcial, identidad, exclusion de instancias,
validacion de configuracion y compatibilidad de sintaxis Python 3.5 del agente.
Siguen pendientes Windows Server real, credenciales de cuenta de servicio,
reinicio de placa, radio, repetidores, magnitudes RS y ensayo prolongado.
