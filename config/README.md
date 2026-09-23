# Configuración

Las rutas se definen en `src/dataloggerwavesin/paths.py` y se pueden sobrescribir
con las variables descritas en `.env.example`. Todas las rutas relativas parten
de la raíz del proyecto, no del directorio actual del terminal.

El archivo `.env.example` es una referencia: no hay carga automática de `.env`.
No hace falta configurar variables para consultar los datos locales conservados.

La configuración original `settings.txt` y `units.txt` permanece dentro de
`data/raw/extraido/home/actemium/apps/xthreeconpi/config/`, ignorada por Git.
El visor solamente lee `units.txt`; no necesita las credenciales de `settings.txt`.
No se ha modificado la configuración del JAR, que no consume estas variables.

No añadir aquí copias de configuración real ni claves. Los archivos
`*.local.*` y `.env` se ignoran como protección adicional.
