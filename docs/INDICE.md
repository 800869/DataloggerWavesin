# Indice de contenidos

## Leer primero

- **[Dimensionamiento preliminar LoRaWAN](DIMENSIONAMIENTO_LORAWAN.md):** puntos por remota, equipos/valores RS485, DI/AI pendientes y requisitos para sustitución.

- **[Dispositivos y se?ales de campo](DISPOSITIVOS_Y_SENALES.md):** recopilaci?n por remota/canal, RS485, DI, 0?10 V y 4?20 mA, fotos, hist?ricos y pendientes.

1. [README](../README.md): sistema anterior, objetivo, uso y limites.
2. [Inventario de tarjetas](INVENTARIO_TARJETAS.md): 24 unidades, capacidades y evidencias.
3. [Adquisicion y mapa Modbus](ADQUISICION.md): contrato estable y calidad de datos.
4. [Despliegue y vuelta atras](../deployment/README.md): Java, SSH y tarea Windows.
5. [Guia de historicos](HISTORICOS.md): visor, analisis y variables de entorno.
6. [Pruebas de banco originales](MODBUS_TCP.md): puente U24 y simulador simple.
7. [Arquitectura historica](ARQUITECTURA.md): flujos de archivos y evidencia.
8. [Reorganizacion inicial](REORGANIZACION.md): movimientos y compatibilidad.

## Codigo mantenido

| Ruta | Responsabilidad |
|---|---|
| src/dataloggerwavesin/acquisition/config.py | Validacion del inventario y rutas |
| src/dataloggerwavesin/acquisition/service.py | Ciclos, reintentos y supervision |
| src/dataloggerwavesin/acquisition/collector.py | SSH acotado, identidad y salida parcial |
| src/dataloggerwavesin/acquisition/radio_agent.py | Agente Python 3.5 enviado por stdin, A2 |
| src/dataloggerwavesin/acquisition/protocol.py | B2 completo: DI, analogicas, RS brutos |
| src/dataloggerwavesin/acquisition/state.py | SQLite y bloques Modbus de 96 registros |
| src/dataloggerwavesin/acquisition/modbus.py | TCP FC03/04 de solo lectura |
| src/dataloggerwavesin/acquisition/instance.py | Bloqueo de instancia por base |
| src/dataloggerwavesin/visor_historicos.py | HTTP historico de solo lectura |
| src/dataloggerwavesin/visor.html | Interfaz historica |
| src/dataloggerwavesin/paths.py | Rutas del subsistema historico |
| scripts/adquisicion.py | Entrada del coordinador PC |
| scripts/Iniciar_adquisicion.cmd | Seleccion de Python Windows |
| scripts/Abrir_visor.cmd, visor_historicos.py | Entradas del visor |
| scripts/analizar_copia.py, analizar_historicos.py | Analisis local que escribe resultados |
| tools/inspeccionar_java.py | Analisis estatico del JAR, no lo ejecuta |
| tools/verify_repository.py | Auditoria de imports, Git y secretos |
| deployment/windows/Instalar_tarea.ps1 | Instalacion opcional de tarea Windows |

## Banco conservado

- tools/consultar_u24_original.py: lector que obtuvo la respuesta real. Conservar
  como referencia reproducible; no es el servicio de produccion.
- tools/puente_u24_modbus.py: puente monounidad independiente ejecutable en placa.
- tools/simulador_modbus.py y scripts/Abrir_simulador_modbus.cmd: diez contadores
  ficticios cada segundo; utiliza el servidor del puente antiguo.
- BEAGLEBONE/: lanzadores compatibles del visor y analisis anteriores.

La implementacion nueva reutiliza el algoritmo A2/CRC y la capa TCP comprobada,
conservando los scripts independientes de banco. Son lineas separadas a proposito:
no modificar el script original cuando se cambie el servicio PC. La captura real
sigue siendo referencia; los tests nuevos comprueban el contrato nuevo.

## Configuracion y pruebas

- config/simulacion_flota.json: 24 identidades ficticias, periodo 600 s.
- config/adquisicion.example.json: ejemplo SSH publicable.
- config/adquisicion.local.json: inventario privado generado, solo U24 habilitada;
  ignorado por Git, alias SSH pendiente. No existe en un clon limpio.
- tests/test_acquisition.py: flota, B2, persistencia, fallos y exclusion.
- tests/test_modbus_bridge.py: referencia radio y protocolo Modbus.
- tests/test_modbus_simulator.py: simulador simple.
- tests/test_runtime.py: visor y analisis con datos sinteticos.

## Datos y documentacion privados (no publicados)

| Ruta | Contenido |
|---|---|
| data/raw/beaglebone_programacion_01.tar | Copia original conservada |
| data/raw/extraido/ | Evidencia de sistema; no ejecutar ni restaurar como imagen |
| data/database/historicos.sqlite | Base de analisis historico, solo lectura desde visor |
| data/database/adquisicion.sqlite | Nueva adquisicion real, solo se crea al arrancar |
| data/database/simulacion_flota.sqlite | Nueva simulacion, separada |
| data/processed/ | Inventarios, calidad, resumenes y Java desensamblado |
| data/processed/manual_texto.txt | Extraccion del manual para esta revision |
| data/private/audit_robustez/ | Hashes previos e inventario de tarjetas |
| docs/private/ | Informe original, manual ViewGest, fotos y conversacion |
| logs/ | Logs originales y subcarpetas rotadas del servicio nuevo |

No se mueven TAR, SQLite historica, configuraciones originales ni archivos de
historicos: conservar nombres mantiene trazabilidad. No se borra ningun original.
