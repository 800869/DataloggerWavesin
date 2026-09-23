# Visor y herramientas de historicos (guia conservada)

Herramientas Python para analizar una copia local de un datalogger BeagleBone
y consultar sus históricos en un visor web de solo lectura. El visor no conecta
con la placa, la radio ni servidores FTP. La adquisición original pertenece al
programa Java recuperado en la copia privada; no se sustituye con este proyecto.

También hay un [puente de banco U24 → Modbus TCP](MODBUS_TCP.md), independiente
del visor, para consultar contadores reales desde Modbus Poll. El puente funciona
con Python 3.5+ en la BeagleBone, sin paquetes externos, y requiere detener Java
para utilizar su puerto serie. Su puesta en marcha real se valida por separado.

## Estructura

```text
src/dataloggerwavesin/   Visor, HTML y resolución de rutas
scripts/                Análisis de copia/históricos y lanzadores
tools/                  Inspección Java y auditoría del repositorio
config/                 Documentación de configuración versionable
data/                   Ignorado por Git; disponible localmente
  database/             historicos.sqlite
  raw/                  TAR original, copia extraída y archivos de la SD
  processed/            Resúmenes, inventarios y análisis Java
  private/              Auditoría y originales anteriores a la reorganización
logs/                   Logs recuperados; ignorados
tests/                  Pruebas con datos sintéticos
docs/                   Arquitectura y mapa de reorganización
  private/              Informe original, manual, fotos y conversación; ignorados
deployment/             Alcance y requisitos para BeagleBone
BEAGLEBONE/              Lanzadores de compatibilidad con las rutas anteriores
.env.example            Variables opcionales, sin credenciales
requirements.txt        Sin dependencias externas
```

## Requisitos e instalación

- Python 3.10 o posterior, con los módulos estándar `sqlite3` y `http.server`.
- Git, para las comprobaciones del repositorio.
- Datos locales para consultar históricos reales. No se incluyen en Git/GitHub.

No hay paquetes externos que instalar. Opcionalmente, desde la raíz:

```sh
python -m venv .venv
```

En Windows se puede usar `.venv\Scripts\python.exe`; en Linux,
`.venv/bin/python`. Los comandos siguientes suponen que `python` corresponde
al intérprete elegido (en Linux suele llamarse `python3`).

## Abrir el visor

En Windows, ejecutar `scripts\Abrir_visor.cmd`, o desde un terminal:

```sh
python scripts/visor_historicos.py
```

Abrir **http://127.0.0.1:8765/**. Detener con `Ctrl+C`. El programa no abre
automáticamente el navegador. El servidor solo escucha en la interfaz local y
SQLite se abre con `mode=ro`.

Se mantienen `BEAGLEBONE/analisis/Abrir_visor.cmd` y los puntos de entrada Python
anteriores como lanzadores de compatibilidad. El CMD busca, por orden, el
intérprete indicado en `DATALOGGER_PYTHON`, `.venv`, `py -3`, `python` y el runtime
local anterior de Codex si está disponible. No contiene una ruta personal fija.

### Datos necesarios

Para arrancar hacen falta estos tres archivos coherentes entre sí:

```text
data/database/historicos.sqlite
data/processed/resumen_historicos.json
data/raw/extraido/home/actemium/apps/xthreeconpi/config/units.txt
```

En este equipo se conservan los datos existentes. Un clon nuevo no los tendrá:
deben aportarse por un medio privado o generarse a partir de una copia autorizada.
Sin esos archivos el visor no arranca; no se crea una base vacía como sustituto.
El HTML mantiene la unidad inicial `U04` del visor original.

## Configuración

No es necesario configurar variables con la estructura local predeterminada.
`.env.example` documenta las opciones; **no se carga automáticamente**.
Se pueden exportar variables antes de ejecutar, por ejemplo en PowerShell:

```powershell
$env:DATALOGGER_DATA_DIR = 'D:\DatosDatalogger'
python scripts/visor_historicos.py
```

En Linux:

```sh
export DATALOGGER_DATA_DIR=/srv/datalogger-data
python3 scripts/visor_historicos.py
```

También existen `DATALOGGER_DATABASE`, `DATALOGGER_ARCHIVE`, `DATALOGGER_UNITS`
y `DATALOGGER_LOG_DIR`. Las rutas relativas parten siempre de la raíz del
proyecto. El visor no utiliza contraseñas FTP ni SSH. Las credenciales originales
se conservan únicamente en la copia local ignorada. Véase [configuración](../config/README.md).

## Utilidades de análisis

Estos comandos **escriben resultados**. No son necesarios para abrir el visor
cuando la copia ya está preparada. Para experimentar sin reemplazar resúmenes
existentes, usar otro `DATALOGGER_DATA_DIR` y apuntar `DATALOGGER_ARCHIVE` al TAR.

```sh
python scripts/analizar_copia.py
python scripts/analizar_historicos.py
python tools/inspeccionar_java.py
```

- `analizar_copia.py` inventaría el TAR y extrae la selección original a
  `data/raw/extraido/`. No ejecuta los archivos recuperados.
- `analizar_historicos.py` lee históricos del TAR, escribe SQLite, resúmenes en
  `data/processed/` y logs en `logs/`. Conserva la lógica original de deduplicación.
- `inspeccionar_java.py` inspecciona estáticamente las clases del JAR extraído y
  escribe `data/processed/java_estatico/`. No requiere ejecutar Java.

Los informes de calidad y otros resultados previos que no tienen generador en
este repositorio se conservan en `data/processed/`; no se promete regenerarlos.

## Pruebas y Git

```sh
python -m unittest discover -s tests -v
python tools/verify_repository.py
git status --short
git diff --cached --stat
```

Las pruebas usan datos ficticios temporales; no modifican históricos reales.
El verificador comprueba sintaxis/imports, exclusiones y posibles secretos en
los archivos versionables y en el índice. Su búsqueda de secretos es heurística.

`.gitignore` excluye datos, logs, cachés, entornos virtuales, backups, credenciales
y documentación privada. No usar `git add -f` para incluir esos archivos. Los
datos ignorados necesitan sus propias copias de seguridad: Git no los respalda.

El mapa de movimientos y las particularidades de compatibilidad están en
[reorganización](REORGANIZACION.md). Véanse también
[arquitectura](ARQUITECTURA.md) y [despliegue en BeagleBone](../deployment/README.md).
