# Pruebas de banco: U24 y simulador simple

Para el servicio PC de 24 remotas, ver [ADQUISICION.md](ADQUISICION.md).
Esta guia conserva las pruebas monounidad anteriores y su mapa 0..24.

## Prueba local sin hardware (Windows)

Ejecutar desde la raiz del proyecto:

```powershell
.\scripts\Abrir_simulador_modbus.cmd
```

Mantener la consola abierta; Ctrl+C termina el servidor. No requiere paquetes
externos ni accede a la BeagleBone. Todos los valores son **FICTICIOS**.
En Modbus Poll conectar por TCP/IP a `127.0.0.1`, puerto `1502`.
Configurar Slave ID `1`, funcion `03`, direccion inicial `0`, cantidad `20`
registros y periodo `1000 ms`. Mostrar como unsigned de 32 bits, palabra alta
primero (big-endian, sin intercambio). Usar direcciones basadas en cero.
Los diez contadores empiezan en 100000, 200000, ... 1000000 y aumentan
respectivamente 1, 2, ... 10 cada segundo.

Otra lectura de direccion `20`, cantidad `5`, formato unsigned de 16 bits
muestra estado, edad, lecturas correctas, fallos y origen. El registro `24=1`
identifica simulacion; esta extension solo existe en el simulador, sin cambiar
el mapa del puente real (0..23).

Para probar fallos y recuperacion:

```powershell
.\scripts\Abrir_simulador_modbus.cmd --fault-cycle
```

Con el intervalo predeterminado, cada ciclo tiene 20 segundos de datos y 10
de fallo: los contadores quedan retenidos, el estado pasa a 2 y aumenta la
edad. Despues se recupera el estado 1. Se simula fallo de adquisicion, no
desconexion TCP. Cerrar primero cualquier simulador anterior.

## Decision actual

El usuario ha elegido Java detenido y lectura directa por SSH, sin FTP ni
Node-RED. La alternativa de leer archivos generados por Java queda descartada.
El nuevo coordinador y su despliegue estan en ADQUISICION.md y deployment/README.md.
Lo siguiente describe el puente monounidad conservado para ensayos anteriores.

`tools/puente_u24_modbus.py` es un ejecutable independiente, compatible en
sintaxis con Python 3.5. Solo usa la biblioteca estándar. Se ejecuta en Linux;
las pruebas de protocolo y TCP se ejecutan también en Windows.

Es un puente de banco para una U24. No sustituye todavía la adquisición ni el
almacenamiento del programa Java. No instala paquetes, no escribe archivos y
no cambia configuraciones ni contadores de la tarjeta. Java debe permanecer
detenido durante la prueba. No ejecutar simultáneamente el lector original.

## Arranque desde PowerShell

Desde la raíz del proyecto, sustituir `BEAGLE_HOST` por la dirección del equipo
y `RADIO_ID` por los doce dígitos hexadecimales de U24:

```powershell
Get-Content -Raw -Encoding UTF8 .\tools\puente_u24_modbus.py | ssh root@BEAGLE_HOST "python3 -u - --unit RADIO_ID --port 502"
```

El programa recibe su código por stdin, sin crear un archivo en la BeagleBone.
Mantener abierta esta sesión. Al arrancar comprueba el PID del servicio Java,
los descriptores abiertos sobre el puerto serie y el puerto TCP. No detiene
servicios automáticamente. Cada apertura del puerto serie utiliza además un
bloqueo cooperativo exclusivo.

La salida debe mostrar `Modbus TCP escuchando...` y después `U24 OK: DI1=...`.
Cada lectura muestra los diez contadores, etiquetados de `DI1` a `DI10`.
Que el servidor TCP esté escuchando no demuestra que haya lecturas válidas:
comprobar siempre el registro de estado 20.

## Modbus Poll en el PC

1. **Connection > Connect (F3):** Modbus TCP/IP, dirección de la BeagleBone,
   puerto 502. Timeout de respuesta: 1000 ms.
2. **Setup > Read/Write Definition (F8):** Slave ID 1, función 03 Read Holding
   Registers, Address 0, Quantity 24, Scan Rate 1000 ms.
3. Para la primera prueba, mostrar **Unsigned de 16 bits**. Cada contador ocupa
   dos registros, palabra alta primero. DI1 estará en 0 y 1; DI2 en 2 y 3.
4. Para ver las **diez entradas juntas**, leer Address **0**, Quantity **20** y mostrar
   **32-bit unsigned, Big-endian**, sin intercambio de palabras ni bytes.
   Así aparecen diez contadores, desde DI1 hasta DI10. Para diagnóstico, abrir
   otra ventana con Address **20**, Quantity **4**, **Unsigned de 16 bits**.

Se utilizan direcciones de protocolo desde cero. La dirección 0 corresponde a
la referencia convencional 40001: no escribir 40001 en el campo Address.

## Mapa de registros, Slave ID 1

| Dirección desde 0 | Tipo | Contenido |
| --- | --- | --- |
| 0–1 | uint32, alta/baja | DI1: asociación física comprobada |
| 2–3 | uint32, alta/baja | DI2: asociación física comprobada |
| 4–5 | uint32, alta/baja | DI3: asignación provisional al contador 3 |
| 6–7 | uint32, alta/baja | DI4: asignación provisional al contador 4 |
| 8–9 | uint32, alta/baja | DI5: asignación provisional al contador 5 |
| 10–11 | uint32, alta/baja | DI6: asignación provisional al contador 6 |
| 12–13 | uint32, alta/baja | DI7: asignación provisional al contador 7 |
| 14–15 | uint32, alta/baja | DI8: asignación provisional al contador 8 |
| 16–17 | uint32, alta/baja | DI9: asignación provisional al contador 9 |
| 18–19 | uint32, alta/baja | DI10: asignación provisional al contador 10 |
| 20 | uint16 | 0: sin lectura válida; 1: última consulta válida y reciente; 2: fallo de consulta o datos antiguos |
| 21 | uint16 | Segundos desde la última respuesta válida; 65535 si nunca hubo respuesta, o edad saturada |
| 22 | uint16 | Consultas válidas desde el arranque; saturación en 65535 |
| 23 | uint16 | Consultas fallidas desde el arranque; saturación en 65535 |

`contador = registro_alto * 65536 + registro_bajo`. No son números float.
Se leen y publican los diez contadores en cada respuesta A2, sin consultas
individuales por entrada ni comandos para habilitar canales. Las etiquetas
DI3..DI10 siguen el orden de los campos; su correspondencia con los bornes
todavía debe comprobarse. No se deduce el estado abierto/cerrado del valor del
contador y no se exponen estas entradas como bobinas booleanas.

La prueba automática inyecta diez valores distintos mayores de 65535 en una
respuesta de radio fragmentada y comprueba su lectura conjunta e individual por
TCP en los registros 0..19. Esto valida el recorrido de software completo; no
sustituye la prueba física de cada entrada. DI1 tiene pendiente verificar la
repetibilidad: en una serie manual de cinco cierres se observaron cuatro
incrementos. DI2 sí registró cinco incrementos en la serie de cinco cierres.

Los valores iniciales cero no son mediciones si el estado es 0. Ante un fallo
se conservan los últimos contadores, pero el estado pasa a 2. No hay persistencia
de la caché del puente entre arranques; los contadores proceden de la tarjeta.

FC04 ofrece el mismo mapa. Las funciones de escritura se rechazan con excepción
01; direcciones fuera del mapa, con 02; cantidades/formato inválidos, con 03.
Otro Slave ID devuelve excepción 0B. Solo se implementa este subconjunto de
Modbus para lectura, no un servidor Modbus certificado ni de propósito general.

## Radio y temporización

Se conserva la petición A2 del script recuperado: comando de base 0x22,
dirección de seis bytes y A2, CRC original, 9600 8N1, sin ACK añadido.
El receptor reúne fragmentos, valida el CRC, comprueba dirección y tipo B2 y
acepta el perfil de 130 bytes adicionales observado en U24. Los diez campos
uint32 se leen desde el desplazamiento 15 del payload que empieza por B2.

A diferencia de la consulta manual, termina la espera al recibir una respuesta
válida y repite tras cinco segundos. Si no recibe datos, espera hasta veinte
segundos antes de marcar fallo. La edad se calcula con el reloj monotónico de
la BeagleBone, no con el reloj de la tarjeta. Se marca antigüedad excesiva a los
treinta segundos. La consulta del PC no genera peticiones de radio.

Opciones: `--bind`, `--port`, `--slave-id`, `--serial`, `--interval`, `--timeout`,
`--stale-after`. La dirección radio es obligatoria mediante `--unit`.

## Parada y vuelta al programa original

Al interrumpir el proceso con SIGINT/SIGTERM/SIGHUP se cierra el servidor, se
termina la espera serie y se restauran los parámetros del puerto. La vigilancia
del proceso padre y de la salida del terminal ayuda a detenerlo si se cierra SSH.
Si fuera necesario, localizar el PID de esta ejecución con `ps` en otra sesión
SSH y enviar `kill -TERM PID`; comprobar después que el puerto serie está libre.

Java no se arranca automáticamente. Tras terminar la prueba y comprobar que el
puente ya no tiene abierto el puerto, se puede recuperar la adquisición original:

```sh
systemctl start xthreeconpi.service
systemctl status xthreeconpi.service --no-pager -l
```

No se ha instalado arranque automático del puente. Las pruebas locales verifican
CRC, fragmentación, mapa de registros, lectura TCP, excepciones y datos antiguos;
la comunicación real BeagleBone → Modbus Poll se valida durante la prueba de banco.

Fuentes del protocolo y de la interfaz del cliente:
[Modbus Organization](https://www.modbus.org/modbus-specifications) y
[manual oficial de Modbus Poll](https://www.modbustools.com/mbpoll-user-manual.html).
