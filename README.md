# DataloggerWavesin

Adquisicion Wavenis desde un PC Windows, persistencia local y publicacion Modbus
TCP para EBO/Modbus Poll. Incluye el visor de historicos del sistema anterior.

**Estado: implementacion de banco probada localmente, no desplegada como servicio
ni validada con toda la instalacion.** U24: A2 y DI1/DI2 comprobados. U13 con
expansion RS485 confirmada por el usuario; su respuesta y escala aun pendientes.

[Indice](docs/INDICE.md) · [Tarjetas](docs/INVENTARIO_TARJETAS.md) ·
[Mapa y adquisicion](docs/ADQUISICION.md) · [Despliegue](deployment/README.md)

Consulta tambi?n la [recopilaci?n de dispositivos y se?ales](docs/DISPOSITIVOS_Y_SENALES.md), con las 24 remotas y evidencias por canal.

## Sistema anterior y objetivo

Java XTHREECONPI V2.4 controla UART4 a 9600 8N1, recoge datos de 24 remotas,
genera JSON y envia FTPES. Su arranque escribe relojes/configuracion; tiene
limpieza de backups y TCP propio 1050 (no Modbus). La cola FTP acumulada coincidio
con errores de almacenamiento lleno. La copia original permanece conservada.

La nueva via sustituye esa adquisicion/envio: **Java detenido, sin FTP**.
El PC consulta por SSH cada 600 segundos, persiste en su propio SQLite y sirve
Modbus de solo lectura. No necesita Node-RED.

```text
Remotas DI / RS485 -> radio -> BeagleBone UART4 -> agente temporal SSH
                                                        |
PC Windows: adquisicion -> SQLite nueva -> Modbus TCP -> EBO / Modbus Poll
```

Configuracion recuperada: 10 remotas tipo 4, 5 tipo 6 y 9 tipo 7; 100 canales
RS configurados en 14 remotas. El formato instantaneo reserva 10 DI, 2 analogicas
y 18 RS por remota. No significa que todos tengan sensores o significado validado.

## Proteccion de la BeagleBone y limites

Este trabajo no ha conectado ni modificado la placa. El agente se transmite por
stdin a Python 3.5, sin instalar paquetes ni archivos de programa. Solo consulta
A2; comprueba MainPID=0 de Java, propietarios del puerto y bloqueo exclusivo.
Si esta ocupado, falla sin detener procesos. Restaura la configuracion serie al
salir normalmente o por senal; un corte de corriente/SIGKILL no permite garantizarlo.
No cambia relojes, ajustes de remotas, GPIO, UART/setuarts ni historicos.

**Para recuperarse tras reiniciar la placa hay que deshabilitar el arranque de
Java de forma reversible.** Mientras siga habilitado, el lector se negara a
competir con el Java que arranque. SSH desatendido requiere clave y known_hosts
para la cuenta Windows del servicio; una contrasena interactiva no basta.
Ambas preparaciones siguen pendientes y se explican en despliegue.

No se promete impacto cero: cambia quien adquiere y Java deja de enviar FTP.
Se conservan programa, configuraciones e historicos para una vuelta atras.
Los cortes pueden perder muestras RS instantaneas; el lector no recupera
historicos remotos. Los contadores acumulados solo permiten diferencias fiables
si se verifican resets, desbordamientos y escala.

## Estructura

```text
src/dataloggerwavesin/
  acquisition/          Configuracion, SSH, B2, persistencia y servidor Modbus
  visor_historicos.py   Visor de solo lectura
  visor.html, paths.py  Interfaz y rutas del visor
scripts/               Lanzadores y utilidades de historicos
tools/                 Diagnostico y lectores de banco conservados
config/                Ejemplos; *.local.json privados ignorados
deployment/windows/    Instalador opcional de tarea Windows
docs/                  Indice, inventario y guias
  private/             Manual, informe, conversacion originales ignorados
tests/                 Pruebas sinteticas y TCP loopback
data/                  Bases, TAR, copia, resultados y auditorias ignorados
logs/                  Logs runtime ignorados
BEAGLEBONE/            Lanzadores antiguos compatibles
```

El nuevo codigo esta agrupado en acquisition/. Se mantienen las rutas de las
evidencias porque aparecen en SQLite, informes y TAR; no se necesita moverlas
para ordenar el software. Se conservan los lectores de banco para reproducir
los ensayos previos. El indice distingue ambos sistemas.

## Requisitos e inicio

PC: Python 3.10+ (validado localmente con 3.12), biblioteca estandar y cliente
OpenSSH para modo real. BeagleBone: Python 3.5, termios/fcntl, SSH y UART4.
No hacen falta paquetes pip. Opcional: `python -m venv .venv`.

En PowerShell, desde la raiz, simular 24 remotas:

```powershell
.\scripts\Iniciar_adquisicion.cmd --config .\config\simulacion_flota.json
```

Modbus Poll: TCP/IP **127.0.0.1:1502**, Slave ID **1**, funcion **03**, direccion
**0**, cantidad **20**. Seleccionar todas las celdas y aplicar **32-bit unsigned,
big-endian, sin intercambio**. Direcciones de base cero, no numeros 40001.
Cada contador ocupa dos registros; una celda `--` puede corresponder a la segunda
palabra. La mezcla de negativos de la captura es compatible con celdas en signed16,
no demuestra fallo TCP. No usar float ni 16-bit signed para estos contadores.

La flota actualiza cada diez minutos. Para cambios cada segundo sigue disponible:

```powershell
.\scripts\Abrir_simulador_modbus.cmd
```

Cerrar el otro servidor antes: ambos usan 1502. No confundir sus valores ficticios
con entradas reales. Registro de origen=1 en ambos simuladores.

Validar configuracion sin red ni escrituras:

```powershell
.\scripts\Iniciar_adquisicion.cmd --config .\config\adquisicion.local.json --check
```

Se preparo un inventario privado local de 24 remotas con solo U24 habilitada.
El ejemplo publico contiene radio y alias SSH ficticios. No ejecutar modo real
hasta preparar SSH y la transicion. Rutas de base/logs relativas al JSON.

## Robustez implementada

- Rondas secuenciales con timeout por unidad; servidor TCP independiente del SSH.
- Una sesion SSH por ronda, no por tarjeta. Se reconstruye cada diez minutos:
  no depende de mantener una conexion abierta durante las esperas. Fallo total:
  espera creciente de 30 a 600 segundos; fallo parcial: nueva ronda ordinaria.
- Ultimo valor retenido con estado, edad y origen. Un fallo no publica ceros validos.
- SQLite transaccional, WAL, synchronous FULL. Tras reinicio: datos recuperados
  marcados antiguos hasta nueva lectura. Simulacion nunca se restaura como real.
- Exclusion de instancias por base, hasta 16 clientes TCP y timeouts de socket.
- Logs rotados (2 MB + cinco copias). Las muestras SQLite no se borran: planificar
  espacio, copias y archivado. 24 tarjetas cada 10 minutos: 3.456 muestras/dia.
- Tarea Windows preparada con arranque, reintentos y supervision periodica,
  **no instalada**. Pendiente ensayo real de reinicios/cortes y rutas con repetidores.

## Historicos y mantenimiento

Abrir `.\scripts\Abrir_visor.cmd` y **http://127.0.0.1:8765/**. Requiere los datos
privados conservados. [Guia de historicos](docs/HISTORICOS.md): instalacion,
variables de entorno, analisis y ubicaciones. La base historica no se modifica.

```powershell
python -m unittest discover -s tests -v
python tools/verify_repository.py
git status --short
git diff --check
```

Usar el interprete configurado si python es el alias de Microsoft Store. Las
pruebas usan datos temporales, no hardware. Git excluye datos, backups, logs,
credenciales y documentos privados; no usar git add -f. La busqueda de secretos
es heuristica. No se ha hecho commit, publicacion ni instalacion remota.
