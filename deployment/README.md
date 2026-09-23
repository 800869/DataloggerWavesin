# BeagleBone: alcance del despliegue

La reorganización afecta únicamente al repositorio local. No se ha conectado a
la BeagleBone, cambiado su servicio, usado la radio ni enviado datos por FTP.

## Programa original de campo

La copia contiene `etc/systemd/system/xthreeconpi.service`, cuyo arranque es:

```text
/usr/bin/java -jar /home/actemium/apps/xthreeconpi/xthreeconpi.jar
```

También contiene `setuarts.service`, que hace referencia a `/usr/bin/uarts.sh`.
Ese script no está en la selección extraída del proyecto. El servicio original,
sus configuraciones y las bibliotecas Java se conservan bajo
`data/raw/extraido/`. Son evidencia privada, no una instalación reproducible.

No se proporciona un instalador automático del JAR: faltan verificaciones de
Java, RXTX nativo, puertos serie, GPIO/UART, permisos y configuración del equipo.
Copiar este repositorio a la placa no sustituye al programa de adquisición.
Las rutas absolutas Linux del servicio original deben permanecer intactas.

## Visor Python en un equipo Linux o BeagleBone compatible

Requiere Python 3.10+ con `sqlite3`, los archivos privados indicados en el README
y espacio suficiente para la copia. No usar el Python 3.5 de la imagen antigua
como si estuviera validado para esta versión del proyecto.

Desde la raíz del proyecto:

```sh
python3 scripts/visor_historicos.py
```

El servidor escucha exclusivamente en `127.0.0.1:8765`. No ocupa la radio ni el
puerto serie y abre SQLite en modo de solo lectura. Para consulta desde otro
equipo, puede utilizarse un túnel SSH configurado por el administrador; el
repositorio no expone el visor en la red ni instala servicios automáticamente.

Esta ejecución se ha comprobado en Windows con Python 3.12; la puesta en marcha
en hardware BeagleBone requiere una comprobación independiente.
