# Arquitectura y referencias

El código Python de este repositorio analiza una copia local y presenta los
históricos mediante HTTP. No implementa la adquisición Wavenis en tiempo real.
La aplicación de campo recuperada está compilada en `xthreeconpi.jar`.

## Flujo de archivos

```text
data/raw/beaglebone_programacion_01.tar
    ├── scripts/analizar_copia.py
    │   ├── data/raw/extraido/ (selección de archivos, sin ejecutar contenido)
    │   └── data/processed/ (inventarios y enlaces)
    └── scripts/analizar_historicos.py
        ├── data/database/historicos.sqlite
        ├── data/processed/resumen_historicos.json y resumen_logs.json
        └── logs/

data/raw/extraido/.../xthreeconpi.jar
    └── tools/inspeccionar_java.py → data/processed/java_estatico/

units.txt + resumen_historicos.json + historicos.sqlite + visor.html
    └── src/dataloggerwavesin/visor_historicos.py
        └── HTTP local, 127.0.0.1:8765
```

`paths.py` concentra las rutas de entrada/salida. Los lanzadores introducen
`src/` en `sys.path` a partir de su ubicación, por lo que no dependen del
directorio actual. El HTML se conserva junto al visor, sin dependencias web
externas. Sus peticiones `/api/unidades` y `/api/serie` no cambian.

## Clasificación del contenido original

| Contenido | Tratamiento |
| --- | --- |
| Cuatro scripts Python propios y HTML | Código mantenido y versionable |
| Lanzador CMD con ruta personal al intérprete | Sustituido por selección portable de Python |
| Copia extraída de `/etc`, `/home`, `/root`, `/usr`, `/var` | Evidencia local íntegra en `data/raw/extraido/` |
| Dos `sitecustomize.py` de la copia del sistema | Parte de la evidencia, no módulos del proyecto |
| Runtimes, ejemplos y fuentes de terceros dentro del TAR | Se conservan en el archivo original, sin incorporarlos a `src/` |
| SQLite de históricos | `data/database/`, solo lectura desde el visor |
| TAR original, configuración SD e históricos FTP | `data/raw/`, ignorados |
| Inventarios JSON/JSONL/TXT, informes de calidad, desensamblado | `data/processed/`, ignorados |
| Logs recuperados | `logs/`, ignorados |
| Informe de instalación, conversación, manual y fotografías | `docs/private/`, conservados sin publicar |
| Cachés Python | Se conservan donde existan; ignoradas |
| Credenciales FTP, configuración de red y claves del sistema | Permanecen en la copia privada; no se exportan al código |

No se necesitan paquetes de terceros para los scripts Python. Las bibliotecas
Java recuperadas (`ftp4j`, `gson`, `jsch`, `RXTXcomm`) pertenecen al programa
original de campo, no a `requirements.txt`. No se publica ningún JAR ni archivo
comprimido como parte del código Python.

## Referencias históricas y configuración de campo

Las rutas Linux que aparecen en la copia, el desensamblado y los informes
describen el equipo original. Se conservan literalmente como evidencia; no son
rutas locales que deba usar Python. Tampoco se cambian los nombres contenidos en
el TAR o en la columna `origen` de SQLite.

Los archivos de `docs/private/` son documentos históricos. Las ubicaciones
actuales se describen en `REORGANIZACION.md`, sin reescribir la evidencia original.

## Límites existentes

- El visor requiere una copia preparada: no descarga ni genera datos al arrancar.
- Los scripts de análisis escriben resultados y pueden reemplazar resúmenes.
  No deben ejecutarse sobre la copia conservada simplemente para abrir el visor.
- La selección inicial `U04`, el puerto 8765, los canales y las reglas de
  consulta siguen siendo los del programa original.
- Los scripts son utilidades ejecutables: importarlos puede ejecutar su análisis.
  Las pruebas los ejecutan exclusivamente con archivos sintéticos temporales.
