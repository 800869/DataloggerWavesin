# Despliegue y recuperacion

No se ha instalado ninguna tarea ni accedido a la BeagleBone durante este trabajo.
No ejecutar el despliegue definitivo hasta completar el banco U24/U13.

## Preparacion BeagleBone (cambio minimo explicito)

El servicio original es xthreeconpi.service, ejecuta el JAR original bajo
/home/actemium/apps/xthreeconpi y arranca automaticamente. Una parada manual no
sobrevive a un reinicio. Para la nueva arquitectura se necesita, durante la
transicion programada, detenerlo y deshabilitar SOLO su arranque:

```bash
systemctl stop xthreeconpi.service
systemctl disable xthreeconpi.service
systemctl show xthreeconpi.service --no-pager -p MainPID -p ActiveState
systemctl is-enabled xthreeconpi.service
```

Estos comandos CAMBIAN el estado de Java; aqui solo se documentan. Esperar
MainPID=0 y disabled. Un estado failed con salida 143 tras parada no implica que
siga ejecutandose. No tocar setuarts.service, uarts.sh, red, SSH ni configuracion
original. El lector comprueba puerto y PID antes de cada consulta y falla cerrado
si Java reaparece. No lo deshabilita ni lo mata automaticamente.

Probar UART4 tras un reinicio real antes de aceptar la instalacion. La copia
original no incluia uarts.sh, por lo que no se certifica ese arranque desde la copia.

## SSH desatendido

En la cuenta Windows elegida preparar un alias SSH `beaglebone-lectura`, clave
privada protegida por ACL y known_hosts con huella comprobada. La clave publica
debe estar autorizada en la BeagleBone si aun no lo esta. Eso es otra preparacion
remota real, no una promesa de cero cambios. No hay contrasenas en el repositorio.
El programa no acepta interacciones: BatchMode=yes y StrictHostKeyChecking=yes.
No desactivar la comprobacion de huella para ocultar fallos de conexion.

Verificar previamente desde ESA cuenta:

```powershell
ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes beaglebone-lectura "python3 --version"
```

Es una consulta, no instala archivos. El alias debe funcionar sin pedir password
ni confirmacion. Usar el mismo perfil Windows al ejecutar la tarea. Un alias
preparado en el perfil de un administrador distinto no basta.

## PC / Enterprise Server

1. Python 3.10+ instalado en ruta estable, cliente OpenSSH y cuenta de servicio
   con acceso al proyecto, SQLite/logs y su perfil SSH. No depender del runtime
   de Codex para produccion. Evitar carpeta sincronizada/red para SQLite.
2. Copiar/adaptar config/adquisicion.example.json a un archivo *.local.json.
   El inventario local ya preparado habilita solo U24; U13 y el resto esperan ensayo.
3. Ejecutar --check y despues probar en primer plano con el JSON privado.
4. Confirmar calidad/origen, timestamps, persistencia y salida Ctrl+C. La parada
   espera terminar la ronda acotada (puede tardar varios minutos).
5. Elegir interfaz de escucha para EBO: localhost si cliente y servidor estan en
   el mismo PC; IP LAN explicita en otro caso. Preparar regla de firewall limitada
   al cliente. No se crea ninguna regla automaticamente. Puerto inicial 1502.
6. Registrar tarea con PowerShell elevado, rutas reales y cuenta preparada:

```powershell
.\deployment\windows\Instalar_tarea.ps1 -Python 'C:\Python312\python.exe' -Config '.\config\adquisicion.local.json'
```

El script pide credenciales de Windows para el Programador de tareas; no las
escribe a archivos. Registra inicio al arrancar y comprobacion cada cinco minutos,
IgnoreNew para no duplicar, reintentos de fallo y sin limite de ejecucion. La tarea
puede iniciarse al minuto de registrarla, sin sesion interactiva. No reemplaza una
tarea existente. Hay tambien bloqueo de instancia por base y rechazo de puerto
ocupado. Revisar privilegio de inicio por lotes y permisos de la cuenta.

El programa conserva su servidor TCP cuando falla SSH y sigue reintentando.
Si muere el proceso, la tarea lo relanza. Si vuelve la BeagleBone, la siguiente
ronda debe recuperar lecturas, siempre que Java siga deshabilitado y UART/SSH listos.

## Matriz de aceptacion de campo

| Prueba | Resultado exigido | Estado |
|---|---|---|
| Modbus local, 24 unidades ficticias | Bloques y formatos correctos | Automatizada localmente |
| Cierre/reinicio proceso con SQLite | Retiene valores con calidad antigua | Automatizada localmente |
| Corte SSH simulado | Mantiene TCP/datos, indica fallo | Automatizada localmente |
| U24 real con nuevo coordinador | DI1/DI2 coherentes | Pendiente |
| U13 real | B2 y campos RS comparados con equipo | Pendiente |
| Reinicio Beagle | UART y SSH listos, Java no arranca, recupera | Pendiente |
| Corte/restablecimiento de red | Sin bloqueo; datos antiguos y recuperacion | Pendiente |
| Reinicio PC sin login | Tarea, SSH y Modbus operativos | Pendiente |
| 24 remotas y repetidores | Cadencia y calidad verificadas | Pendiente |
| Disco lleno / corrupcion | Alarma, sin datos falsamente validos | Requiere ensayo de despliegue |

## Vuelta atras

Primero detener/deshabilitar la tarea Windows y confirmar que no quedan lector
SSH ni propietarios de UART. Despues, solo si se decide volver al original:

```bash
systemctl enable xthreeconpi.service
systemctl start xthreeconpi.service
```

Arrancar Java vuelve a sus escrituras de reloj/configuracion, FTP y politicas de
retencion; no es una operacion pasiva. Conservar antes una copia coherente de los
datos. No se borran ni sobrescriben el JAR, units.txt, settings.txt o historicos.

## Referencias tecnicas

- [OpenSSH ssh_config](https://man.openbsd.org/ssh_config): BatchMode, verificacion
  de host y ServerAliveInterval/CountMax.
- [Microsoft ScheduledTasks](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/new-scheduledtasksettingsset):
  reinicio, limite de ejecucion y politica de instancias.

El visor historico sigue en el PC con Python 3.10+, solo lectura; no se instala
sobre el Python 3.5 de la placa. Vease docs/HISTORICOS.md.
