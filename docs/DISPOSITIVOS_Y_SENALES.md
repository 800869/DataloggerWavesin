# Dispositivos de campo y señales recuperadas: RS485, DI y analógicas

Fecha de recopilación: 23/09/2026. Documento de investigación de la instalación original y del banco actual.

**Objetivo:** reunir en un -nico lugar las identidades, conexiones, mapas y evidencias disponibles para identificar qué equipos estaban conectados a cada remota. No convertir una capacidad de hardware, un cero o un valor histórico en una identificación física inventada.

## Indice

1. [Conclusiones y grado de certeza](#1-conclusiones-y-grado-de-certeza)
2. [Fuentes y alcance](#2-fuentes-y-alcance)
3. [Hardware fotografiado](#3-hardware-fotografiado)
4. [Parâmetros RS485 recuperados](#4-parâmetros-rs485-recuperados)
5. [DI: entradas, contadores y equipos](#5-di-entradas-contadores-y-equipos)
6. [Analógicas: 0-10 V y 4-20 mA](#6-analógicas-010-v-y-420-ma)
7. [Fichas de las 24 remotas](#7-fichas-de-las-24-remotas)
8. [Información que falta y dónde recuperarla](#8-información-que-falta-y-dónde-recuperarla)
9. [Registro de hallazgos y mantenimiento](#9-registro-de-hallazgos-y-mantenimiento)

## 0. Reconstruccion funcional desde la programacion antigua

Actualizacion tras aclaracion del usuario: priorizar **que se leia en la instalacion**, no que hay conectado en el banco. Las fotos solo identifican las dos tarjetas retiradas.

| Grupo | Evidencia del programa y configuracion | Interpretacion de trabajo | Limite |
|---|---|---|---|
| U01-U14 | Analyzer habilitado; parejas 53/55, dos palabras cada una, IDs locales 2..6 | Lectura de contadores/analizadores, probablemente magnitudes acumuladas electricas en varios canales | No asignar energia activa/reactiva, importada/exportada ni fabricante sin mapa del aparato |
| U15-U24 | Tipo historico4, cuatro campos enteros; predomina el primero | Contaje de impulsos de contadores de servicios, consistente con agua/luz/gas descritos por el usuario | Factor impulso/unidad y servicio por canal desconocidos |
| AI1/AI2 | Campos presentes en formato instantaneo; perfiles historicos4/6/7 rellenan huecos | Posibles medidas adicionales; no reconstruibles de esos ceros historicos | No se ha identificado una senal de proceso ni escala 4-20mA |
| Campo indice1 | Java aplica raw*5/4096; alrededor de 3,3 en muchas muestras | Candidato a medida auxiliar interna/alimentacion | No identificado por nombre; no etiquetar como sensor externo |
| Estado indice0 | Palabra numerica separada de contadores | Estado/diagnostico candidato | Sin mapa de bits confirmado |
| OneWire | Analyzer.isOneWire() y eUnit.setOneWire(); conversion255 | Capacidad adicional del software | Ninguna entrada del mapa recuperado usa255; no prueba sondas instaladas |

### Que confirma el analisis temporal nuevo

Se recorrieron las lecturas SQLite ordenadas por unidad y fecha, sin modificar la base. Se excluyeron completamente las **161 combinaciones unidad/fecha con versiones distintas**. Se contaron aumentos, descensos e igualdades entre muestras inequ?vocas consecutivas (pueden quedar huecos; no se asume separacion fija).

- U04 y U06: sus ocho canales RS no presentan descensos en ese analisis. Respaldan la hipotesis de acumuladores frente a medidas instantaneas, sin demostrar unidades.
- U13: RS2 y RS3 no descienden; RS1 tiene un descenso; RS4 permanece cero. Son candidatos fuertes a contadores acumulados, pero el registro55 no puede llamarse automaticamente energia reactiva.
- U19, U20 y U24: primer campo DI crece o permanece igual, sin descensos. Encaja con acumulacion de impulsos.
- U18: primer campo constante. U21 y U23: primer y ultimo valor iguales con pocas excursiones. No considerarlos contadores activos fiables solo por tener valores grandes/no nulos.
- U14: numerosos descensos; revisar configuracion, cambios de origen o calidad antes de diferencias. No se determina la causa con este recuento.

La pareja 53/55 y el comportamiento acumulativo constituyen una pista para identificar el modelo en el futuro; no una identificacion unica. La busqueda dirigida de nombres de magnitudes/modelos en las constantes propias del Java no encontro kWh/kvarh, agua/gas o fabricante de contador que cierre esa correspondencia. No se ha hecho una atribucion basada en coincidencias de direcciones de otro producto.

## 1. Conclusiones y grado de certeza

| Hallazgo | Estado | Evidencia |
|---|---|---|
| 24 remotas U01-U24 configuradas | Confirmado en copia | S1 |
| 14 remotas con analizador habilitado, 100 valores RS configurados | Confirmado en copia | S1, S3 |
| 50 asociaciones remota/ID esclavo | Derivado del mapa | S1; dos valores por ID; no prueba 50 aparatos físicos -nicos |
| U24: radio 076351302B9C, placa de diez DI | Confirmado visualmente y por ensayo | F3/F9, S7 |
| U13: radio 076351302B95, diez DI y expansión de dos AI + RS485 | Confirmado visualmente y por usuario | F7/F8, S7 |
| Expansión U13 admite selección 0-10 V / 4-20 mA | Confirmado por serigrafía | F7/F8; no certifica posición actual ni calibración |
| Expansión U13 rotulada Modbus RTU | Confirmado por serigrafía | F7/F8 |
| Qué contador/sensor concreto ocupaba cada canal | Sin identificación recuperada | No hay marca/modelo/tag físico asociado a cada canal en S1/S4 |
| Baudrate, paridad y función 03/04 del bus remoto | No recuperados | El mensaje setModbus revisado no los transporta |
| Magnitudes, escalas, factores de impulsos y unidades | No recuperados para la instalación | ViewGest permite configurarlos, pero no se dispone de esa configuración del sitio |

**Leyenda:** "configurado" describe la copia, "observado" describe fotos/valores/ensayos, "inferencia" es una interpretación pendiente, "desconocido" no equivale a inexistente.

Las dos tarjetas fotografiadas fueron retiradas de la instalacion por el usuario para hacer pruebas. Sus bornes vacios son consecuencia de ese traslado y **no aportan ninguna evidencia sobre que estaba conectado antes**. Las fotos se usan exclusivamente para identificar hardware. La reconstruccion de dispositivos originales se basa en configuracion, programacion Java, historicos y documentacion del sistema.

**Contexto confirmado por el usuario:** la instalacion se utilizaba principalmente para contadores de agua, electricidad y gas, mediante analizadores de redes y contaje de impulsos; pueden existir otras senales. Este dato orienta la clasificacion, pero no asigna automaticamente una magnitud a un Uxx/canal concreto.


## 2. Fuentes y alcance

| Código | Fuente local | Qué aporta |
|---|---|---|
| S1 | `data/raw/extraido/home/actemium/apps/xthreeconpi/config/units.txt` | Radio, nombre Uxx, tipo histórico, ruta y mapa de analizador |
| S2 | `data/raw/extraido/home/actemium/apps/xthreeconpi/config/settings.txt` | Ciclos del concentrador; contiene información privada que no se reproduce |
| S3 | `data/processed/java_estatico/classes_Analyzer.txt`, `classes_eUnit.txt`, `classes_eLog.txt`, `utils_Utils.txt` | Significado de campos, mensaje A9 de configuración y conversiones |
| S4 | `data/processed/resumen_historicos.json` y `data/database/historicos.sqlite` | Rangos, cobertura, 32 posiciones por lectura y número de valores no nulos |
| S5 | `docs/private/INFORME_BEAGLEBONE.md` | Análisis previo y anomalías; sus límites anteriores se actualizan con las fotos |
| S6 | Manual ViewGest en `docs/private/`, texto en `data/processed/manual_texto.txt` | Capacidades genéricas y dónde se asignan nombres/escalas |
| S7 | Conversación aportada y `docs/private/CODEX CHAT.txt` | Identificación de dos remotas, consultas A2 y ensayos de DI |
| S8 | `data/processed/inventario.jsonl` y archivos recuperados de SD | Búsqueda de configuraciones adicionales y alcance de la copia |
| S9 | `logs/logPi202607.txt`, `logs/logPi202609.txt` | Fallos documentados de configuración Modbus; no garantizan aceptación del mapa |
| F1-F9 | Nueve fotos en `docs/private/IMAGENES PLACAS/` | Identificación visual de placas y bornes |

Se revisaron las nueve fotos, el mapa de todas las unidades, las clases Java de analizador/conversión, los resúmenes de todos los canales de las 24 unidades y el texto extraído del manual. SQLite se abrió en modo solo lectura para comprobar esquema y formato. Los rangos tabulados proceden del resumen existente: no se han recalculado eliminando anomalías.

La búsqueda de nombres/configuraciones relevantes en el inventario TAR encontró units.txt y settings.txt, pero no un mapa de nombres de equipos de campo ni firmware de las MicroRTU. Los tres archivos recuperados por SD (`sysconf.txt`, `START.HTM`, `ID.txt`) no aportaron coincidencias de parâmetros de analizador en la búsqueda dirigida. No se afirma una auditoría semántica de todo Debian ni de bibliotecas de terceros.

Los documentos privados, fotos, copia del sistema y credenciales permanecen fuera de Git. Este informe referencia esas fuentes, sin incorporar credenciales ni configuración de red privada. En un clon público las fuentes privadas no estarán disponibles.

## 3. Hardware fotografiado

Todas las fotos llevan el prefijo `WhatsApp Image 2026-09-21 at 13.54.` y extensión `.jpeg`.

| Foto | Sufijo del archivo | Observación directamente legible |
|---|---|---|
| F1 | `47 (1)` | Módulo desmontado: PCB CS-PCB-029-C; no permite asociar por sí solo un sensor |
| F2 | `47 (2)` | Actemium STM-X3-10DI-2, 30-06-2014; LOW POWER WAVENIS RADIO, 25mW; EXPANSION BOARD |
| F3 | `47 (3)` | U24: radio 076351302B9C / 244-201A; diez DI; SN STM17070043 |
| F4 | `47` | Base radio 186254C072B0 / 245-201A; cape Actemium BBB-CAPE-02, 2020-02-04 |
| F5 | `48 (1)` | Reverso STM-X3-10DI, DC 3,6 V, ensayo 04-07-2017; etiqueta 1718790062 |
| F6 | `48 (2)` | Otro reverso STM-X3-10DI, DC 3,6 V, ensayo 04-07-2017; etiqueta 1718790015 |
| F7 | `48 (3)` | U13: 076351302B95 / 244-201A; expansión STM-X3-2AI-RS485-1, 17-04-2014 |
| F8 | `48 (4)` | Segunda vista de U13 y selección de AI, bornes RS485 MODBUS RTU |
| F9 | `48` | Segunda vista U24, sin expansión montada; DI1-DI10 y SN STM17070043 |

Las etiquetas de reverso F5/F6 no se asignan a U13/U24 porque en esas caras no se ve simultáneamente el ID radio. `244-201A` y `245-201A` son inscripciones de los módulos fotografiados, no modelos de analizadores RS485.

### 3.1 U24: placa base de DI

- Actemium **STM-X3-10DI-2**, fecha de diseño impresa 30-06-2014.
- Diez entradas DI1-DI10; pares de terminales con leyenda `+3.3V / DI`.
- Conectores inferiores X3-X7, cada conjunto agrupa dos entradas.
- Radio `076351302B9C`, etiqueta `244-201A`; no se aprecia expansión analógica montada.
- Conectores de alimentación P1/P2, expansión y botones STATUS/RESET visibles.
- Las pruebas de banco asocian DI1 y DI2 con los dos primeros contadores B2.
- No hay en las fotos contador de agua, gas, energía o contacto de proceso unido a DI.

### 3.2 U13: placa base y expansión

- Base STM-X3-10DI-2 con radio `076351302B95`, etiqueta `244-201A`.
- Expansión **STM-X3-2AI-RS485-1**, fecha 17-04-2014.
- Bornero analógico X3: `+ AI1 -`, `+ AI2 -`.
- Dos selectores JP1/JP2; leyenda `AI JUMPERS`, `0-10V` y `4-20mA`.
- Bornero X2 rotulado **RS485 MODBUS RTU**, con etiquetas `B+` y `A-`.
- No se deduce solo de la imagen la conexión interna de los cuatro tornillos RS485, terminación, polarización o aislamiento.
- La fuente de banco visible está rotulada Mean Well RS-15-3.3 / salida 3,3 V. Es alimentación del montaje fotografiado, no un dispositivo de medida ni evidencia de alimentación histórica.
- En las fotos AI, DI y RS485 no tienen cables de campo. No se deduce modo de los jumpers por apariencia ni se propone modificarlos.

### 3.3 BeagleBone: no confundir su cape con la expansión remota

El cape BBB-CAPE-02 tiene leyendas PWR IN +5V/GND, RS232 TX/RX/GND y RS485 B+/A-/GND. Eso prueba conectores físicos, no que Java estuviera consultando analizadores por ese RS485. El flujo recuperado usa UART4 hacia la base radio; las consultas a analizadores se configuran en las remotas. Los 9600 8N1 comprobados son de ese enlace local de radio.

## 4. Parâmetros RS485 recuperados

### 4.1 Qué significa cada entrada

`canal&esclavo_direccion_longitud_conversion`, por ejemplo `1&2_53_2_0`:

| Campo | Ejemplo | Interpretación comprobada |
|---|---:|---|
| Canal lógico de la remota | 1 | Posición RS1; no es DI1 |
| ID esclavo Modbus | 2 | Dirección de equipo en el bus local de esa remota |
| Dirección configurada | 53 | Entero decimal; se transmite sin restar uno en setModbus |
| Longitud | 2 | Dos registros/palabras de 16 bits por valor |
| Conversión Java | 0 | Tratamiento entero de 32 bits; no float |

Todas las entradas recuperadas emplean direcciones **53 (0x0035) y 55 (0x0037)**, longitud 2 y conversión 0. Cada asociación remota/esclavo aporta dos valores de 32 bits. Son 100 valores y 200 palabras configuradas, no necesariamente 100 peticiones de bus independientes: la planificación interna del firmware no está recuperada.

El método `setModbus()` compone A9 con número de canales y, por canal, Indice, esclavo, dirección de dos bytes y longitud. No envía ahí baudrate, paridad, función ni conversión Java. Esto sitúa parte del comportamiento en el firmware/configuración local de la remota, que no está en la copia. No se ha enviado A9 en esta recopilación.

Los logs añaden una limitación: el 21/09/2026 a las 08:34:33 se registra para U01 `modbus configuration update timeout`; también hay timeouts en julio. Por tanto, **configuración guardada no equivale a configuración aceptada por la remota**. Tampoco el timeout demuestra que la remota careciera de una configuración anterior válida. No se ha leído una confirmación actual de parâmetros desde su firmware.

### 4.2 Tipo de dato y precaución de interpretación

Java reconstruye cada campo como dos palabras, alta primero, y para tipo 0 conserva el entero si bit31=0. Si bit31=1 aplica `(-valor) & 0x7FFFFFFF`. Ejemplos de esa operación: 0x80000000 pasa a 0; 0xFFFFFFFF pasa a 1. No equivale a interpretar sin mês un int32 firmado ni a conservar un uint32. El código está en `eLog.ConvertModbusType`, rama 0; `Utils.checkBit` comprueba el bit.

Por ello los rangos de históricos son **valores ya tratados por Java**, mientras los RS del lector nuevo son **brutos uint32**. Pueden diferir si estaba activo el bit31. No asignar float, signo, kWh, kvarh, factor de transformación o escala por intuición. Se necesita el manual del analizador real. La correspondencia entre dirección 53 y una notación de manual 400xx/300xx tampoco queda cerrada sin conocer función y base del fabricante.

### 4.3 Parâmetros todavía sin recuperar

| Parámetro | Situación |
|---|---|
| RS485 / Modbus RTU en expansión U13 | Confirmado visualmente |
| Baudrate del bus remoto | Desconocido |
| Paridad / bits de datos / parada del bus remoto | Desconocidos |
| Función 03 o 04 | Desconocida |
| Timeout/reintentos propios del bus RS | Desconocidos; no confundir con timeout de radio |
| Orden original de palabras del analizador | Java combina alta primero; falta contrato del aparato/firmware |
| Modelo, firmware y número de serie del analizador | No encontrado |
| Significado de 53 y 55 / unidad / factor | No encontrado |
| Terminación, polarización, distancia y cableado original | No encontrados |
| Frescura/calidad propia del dato RS devuelto por radio | No documentada; B2 reciente no prueba una nueva transacción RS exitosa |

## 5. DI: entradas, contadores y equipos

U24 confirma contadores, no un simple estado abierto/cerrado. DI1 subió durante maniobras, permaneció al mantener contacto y no aumentó al abrir en los ensayos aportados; cinco maniobras produjeron cuatro incrementos en una prueba. DI2 pasó de 0 a 5 tras cinco maniobras confirmadas por el usuario. No se certifican antirrebote, frecuencia máxima, anchura mínima de pulso ni un incremento por cada cierre.

El histórico tipo 4 guarda cuatro campos en posiciones 2..5. Su representación de 32 columnas rellena otros campos con cero; por eso no puede usarse para demostrar que DI5..DI10 estaban libres. En tipos 6/7 Java rellena las posiciones DI con ceros: la ausencia de datos DI históricos en U13 no demuestra ausencia de entradas/cableado.

No se recuperaron nombres de los contadores o contactos, ubicación, magnitud (agua/gas/energía), relación impulsos/unidad, tipo eléctrico de cada sensor ni números de serie. Los campos de tipo 4 con actividad sostenida sugieren acumuladores de impulsos, pero no identifican el equipo que los genera. Una cifra constante como la de U18 puede tener varias causas; no se clasifica como avería.

## 6. Analógicas: 0-10 V y 4-20 mA

La capacidad está **confirmada en U13 por la placa STM-X3-2AI-RS485-1**. No se identifican sensores 4-20 mA concretos ni escalas físicas. Tampoco se extiende automáticamente la presencia de esa expansión a las otras 23 remotas.

| Señal U13 | Bornes | Modo que admite la placa | Modo instalado | Sensor/modelo | Escala física |
|---|---|---|---|---|---|
| AI1 | + AI1 - | 0-10 V / 4-20 mA por selección | Pendiente | No identificado | No recuperada |
| AI2 | + AI2 - | 0-10 V / 4-20 mA por selección | Pendiente | No identificado | No recuperada |

En B2 actual, AI1/AI2 son los uint16 brutos de bytes 55..58 contando B2 como byte0. No hay conversión a mA implementada ni prueba de que 4095/65535 sea fondo de escala. El campo separado que Java convierte `raw*5/4096`, histórico Indice1, **no identifica una AI de proceso ni prueba un lazo 4-20 mA**.

En la copia histórica todas las posiciones 12/13 tienen cero. Las ramas de tipos 4/6/7 revisadas insertan ceros en esos huecos; no permiten concluir que no hubo sensores analógicos. Además, U24 devolvió campos analógicos brutos no nulos aun sin expansión visible (por ejemplo 0x0C24 y 0x0CAA en una captura). Eso demuestra por qué un número no basta para declarar una entrada conectada o válida.

Pendientes para cada AI: modelo y rango del transmisor, dos/tres/cuatro hilos, alimentación del lazo, aislamiento, polaridad, posición comprobada de selector, escalado raw -> mA -> magnitud, comportamiento de circuito abierto y etiquetas de campo. No se proponen conexiones o inyección de corriente sin identificar estos puntos.

## 7. Fichas de las 24 remotas

**Cómo leer las tablas:** Indice histórico empieza en 0. RS lógico k corresponde a Indice 13+k en la representación JSON. "No cero" cuenta filas cuyo valor no era cero, no transacciones válidas ni equipos conectados. Mínimo/máximo incluyen anomalías, duplicados conflictivos y tratamientos Java; no son rangos nominales de sensores. Las fechas son UTC. La configuración y los históricos no son necesariamente coetáneos en cada cambio de equipo.

Para tipos 6/7 se tabulan todos los canales configurados. Para tipo4 se tabulan sus cuatro campos DI históricos. AI1/AI2 siguen sin identificar en todas las unidades; solo la expansión física de U13 está comprobada. Ubicación y marca/modelo de los dispositivos de campo: pendientes para todas salvo futuras incorporaciones documentadas.

### U01 - radio `076351302B96`

- Tipo histórico **7**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - 186250C054F5 - U01. No prueba ruta operativa actual.
- Histórico: **27644 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 0; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 92227 | 2146865430 | 27644 / 27644 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 5226 | 1795160980 | 27644 / 27644 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 41956 | 1074572086 | 27644 / 27644 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 0 | 32769 | 4 / 27644 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 114984 | 1576940494 | 27644 / 27644 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 805 | 17306149 | 27644 / 27644 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 104044 | 2443263 | 27644 / 27644 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 43715 | 339785866 | 27644 / 27644 |
| 9 | 6 | 53 / 0x0035 | 2 | 0 | 22 | 184094 | 822322492 | 27644 / 27644 |
| 10 | 6 | 55 / 0x0037 | 2 | 0 | 23 | 11815 | 1954512567 | 27644 / 27644 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

**Datos fuera del mapa esperado:** Indice 24: 9 filas no cero, rango 0..1644167168; Indice 25: 2 filas no cero, rango 0..40960. Se conservan como anomalía/cambio histórico posible; no se asignan a equipos nuevos.

### U02 - radio `076351302B7E`

- Tipo histórico **7**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - 186250C054F5 - U02. No prueba ruta operativa actual.
- Histórico: **27545 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 96; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 85447 | 1073960250 | 27545 / 27545 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 0 | 40978 | 2 / 27545 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 79116 | 17389967 | 27545 / 27545 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 10 | 49166 | 27545 / 27545 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 397204 | 1979242927 | 27545 / 27545 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 526858 | 1511594542 | 27545 / 27545 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 268410 | 1073453257 | 27545 / 27545 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 67255 | 2071229165 | 27545 / 27545 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

**Datos fuera del mapa esperado:** Indice 22: 8 filas no cero, rango 0..2147549184; Indice 23: 2 filas no cero, rango 0..1610613760; Indice 24: 6 filas no cero, rango 0..3221536768; Indice 25: 7 filas no cero, rango 0..84934912. Se conservan como anomalía/cambio histórico posible; no se asignan a equipos nuevos.

### U03 - radio `076351302B9D`

- Tipo histórico **7**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - 186250C054F5 - U03. No prueba ruta operativa actual.
- Histórico: **27136 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 192; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 86739 | 2146614672 | 27136 / 27136 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 0 | 1713401920 | 27128 / 27136 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 80296 | 1879187533 | 27136 / 27136 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 11 | 339739825 | 27136 / 27136 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 40711 | 805663666 | 27136 / 27136 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 19575 | 2023554363 | 27136 / 27136 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 271484 | 1974485446 | 27136 / 27136 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 29751 | 1027555231 | 27136 / 27136 |
| 9 | 6 | 53 / 0x0035 | 2 | 0 | 22 | 0 | 2143216649 | 27128 / 27136 |
| 10 | 6 | 55 / 0x0037 | 2 | 0 | 23 | 0 | 1655647031 | 27128 / 27136 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

**Datos fuera del mapa esperado:** Indice 24: 5 filas no cero, rango 0..1610620928; Indice 25: 6 filas no cero, rango 0..1275068416. Se conservan como anomalía/cambio histórico posible; no se asignan a equipos nuevos.

### U04 - radio `076351302BCD`

- Tipo histórico **7**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - U04. No prueba ruta operativa actual.
- Histórico: **28636 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 288; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 127794 | 150794 | 28636 / 28636 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 221179 | 267389 | 28636 / 28636 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 263220 | 318384 | 28636 / 28636 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 95475 | 114691 | 28636 / 28636 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 496846 | 604761 | 28636 / 28636 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 24287 | 28628 | 28636 / 28636 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 244872 | 292033 | 28636 / 28636 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 461534 | 553534 | 28636 / 28636 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

### U05 - radio `076351302BA7`

- Tipo histórico **6**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - U05. No prueba ruta operativa actual.
- Histórico: **27447 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 384; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 4324 | 2142399218 | 27447 / 27447 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 147 | 1140879392 | 27447 / 27447 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

**Datos fuera del mapa esperado:** Indice 16: 35 filas no cero, rango 0..1207959552; Indice 17: 37 filas no cero, rango 0..2148073472; Indice 18: 29 filas no cero, rango 0..328180; Indice 19: 29 filas no cero, rango 0..21226; Indice 20: 29 filas no cero, rango 0..323508; Indice 21: 29 filas no cero, rango 0..145957; Indice 22: 29 filas no cero, rango 0..3054; Indice 23: 29 filas no cero, rango 0..4018; Indice 25: 1 filas no cero, rango 0..24576. Se conservan como anomalía/cambio histórico posible; no se asignan a equipos nuevos.

### U06 - radio `076351302BB3`

- Tipo histórico **7**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - U06. No prueba ruta operativa actual.
- Histórico: **28636 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 480; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 441143 | 525910 | 28636 / 28636 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 7280 | 7589 | 28636 / 28636 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 400689 | 481802 | 28636 / 28636 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 1430196 | 1765793 | 28636 / 28636 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 502084 | 617549 | 28636 / 28636 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 103324 | 127951 | 28636 / 28636 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 1439 | 1792 | 28636 / 28636 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 54 | 65 | 28636 / 28636 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

### U07 - radio `076351302B8F`

- Tipo histórico **7**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - 186250C054F5 - 186250C054E4 - U07. No prueba ruta operativa actual.
- Histórico: **27611 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 576; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 4062 | 1610082192 | 27611 / 27611 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 139 | 42467474 | 27611 / 27611 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 2413 | 2147319305 | 27611 / 27611 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 71 | 1875771317 | 27611 / 27611 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 72248 | 2146577322 | 27611 / 27611 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 15348 | 1611155282 | 27611 / 27611 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 133846 | 1610479201 | 27611 / 27611 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 32610 | 1476429318 | 27611 / 27611 |
| 9 | 6 | 53 / 0x0035 | 2 | 0 | 22 | 2838 | 1342191230 | 27611 / 27611 |
| 10 | 6 | 55 / 0x0037 | 2 | 0 | 23 | 3188 | 117705880 | 27611 / 27611 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

**Datos fuera del mapa esperado:** Indice 24: 7 filas no cero, rango 0..2684363264; Indice 25: 9 filas no cero, rango 0..2550136832. Se conservan como anomalía/cambio histórico posible; no se asignan a equipos nuevos.

### U08 - radio `076351302B8D`

- Tipo histórico **7**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - 186250C054F5 - 186250C054E4 - U08. No prueba ruta operativa actual.
- Histórico: **27800 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 672; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 4461 | 2147169656 | 27800 / 27800 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 151 | 1978670901 | 27800 / 27800 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 2592 | 236132 | 27800 / 27800 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 76 | 811468538 | 27800 / 27800 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 87043 | 1610865774 | 27800 / 27800 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 19083 | 1074441654 | 27800 / 27800 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 143924 | 2147363054 | 27800 / 27800 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 34990 | 1073957726 | 27800 / 27800 |
| 9 | 6 | 53 / 0x0035 | 2 | 0 | 22 | 10116 | 1342525072 | 27800 / 27800 |
| 10 | 6 | 55 / 0x0037 | 2 | 0 | 23 | 3652 | 1627602654 | 27800 / 27800 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

**Datos fuera del mapa esperado:** Indice 24: 4 filas no cero, rango 0..33554432; Indice 25: 6 filas no cero, rango 0..268500992. Se conservan como anomalía/cambio histórico posible; no se asignan a equipos nuevos.

### U09 - radio `076351302B8E`

- Tipo histórico **7**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - 186250C054F5 - 186250C054E4 - U09. No prueba ruta operativa actual.
- Histórico: **27814 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 768; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 94408 | 1610873818 | 27814 / 27814 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 159870 | 1611317408 | 27814 / 27814 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 96913 | 402756832 | 27814 / 27814 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 109600 | 2144732335 | 27814 / 27814 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 94585 | 268461912 | 27814 / 27814 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 243326 | 2112363778 | 27814 / 27814 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 103676 | 549566650 | 27814 / 27814 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 378510 | 2146572707 | 27814 / 27814 |
| 9 | 6 | 53 / 0x0035 | 2 | 0 | 22 | 83337 | 33661735 | 27814 / 27814 |
| 10 | 6 | 55 / 0x0037 | 2 | 0 | 23 | 166116 | 1745003923 | 27814 / 27814 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

**Datos fuera del mapa esperado:** Indice 24: 7 filas no cero, rango 0..3406001409; Indice 25: 9 filas no cero, rango 0..1868829788. Se conservan como anomalía/cambio histórico posible; no se asignan a equipos nuevos.

### U10 - radio `076351302B9F`

- Tipo histórico **7**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - 186250C054F5 - 186250C054E4 - U10. No prueba ruta operativa actual.
- Histórico: **27688 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 864; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 4324 | 568855008 | 27688 / 27688 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 147 | 22931087 | 27688 / 27688 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 2551 | 538332074 | 27688 / 27688 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 75 | 806047302 | 27688 / 27688 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 83124 | 1622561300 | 27688 / 27688 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 18067 | 1071138036 | 27688 / 27688 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 105384 | 1874857192 | 27688 / 27688 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 34290 | 1610862668 | 27688 / 27688 |
| 9 | 6 | 53 / 0x0035 | 2 | 0 | 22 | 9770 | 674865521 | 27688 / 27688 |
| 10 | 6 | 55 / 0x0037 | 2 | 0 | 23 | 3530 | 1761628252 | 27688 / 27688 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

**Datos fuera del mapa esperado:** Indice 24: 6 filas no cero, rango 0..3356367628; Indice 25: 8 filas no cero, rango 0..1084325316. Se conservan como anomalía/cambio histórico posible; no se asignan a equipos nuevos.

### U11 - radio `076351302B92`

- Tipo histórico **6**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 076351302BB3 - U11. No prueba ruta operativa actual.
- Histórico: **28634 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 960; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 576933 | 15184392 | 28634 / 28634 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 0 | 20517401 | 4 / 28634 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 1507047 | 1855188 | 28634 / 28634 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 38759 | 684800 | 28634 / 28634 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

**Datos fuera del mapa esperado:** Indice 18: 4 filas no cero, rango 0..3274991; Indice 19: 4 filas no cero, rango 0..375424; Indice 20: 4 filas no cero, rango 0..4021024; Indice 21: 4 filas no cero, rango 0..249901; Indice 22: 4 filas no cero, rango 0..3655197; Indice 23: 4 filas no cero, rango 0..327554. Se conservan como anomalía/cambio histórico posible; no se asignan a equipos nuevos.

### U12 - radio `076351302B9E`

- Tipo histórico **6**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - 186250C05529 - U12. No prueba ruta operativa actual.
- Histórico: **26287 filas**, 2025-10-28T10:15:00+00:00 a 2026-08-23T15:00:00+00:00.
- Referencia nueva Modbus TCP: base 1056; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 99282 | 77430230 | 26287 / 26287 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 44345 | 1275117161 | 26287 / 26287 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 102208 | 2146469799 | 26287 / 26287 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 15741 | 2146843265 | 26287 / 26287 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

**Datos fuera del mapa esperado:** Indice 18: 6 filas no cero, rango 0..3100216; Indice 19: 6 filas no cero, rango 0..425453; Indice 20: 6 filas no cero, rango 0..3958156; Indice 21: 6 filas no cero, rango 0..397557; Indice 22: 6 filas no cero, rango 0..3604632; Indice 23: 6 filas no cero, rango 0..327477. Se conservan como anomalía/cambio histórico posible; no se asignan a equipos nuevos.

### U13 - radio `076351302B95`

- Tipo histórico **6**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 076351302BB3 - U13. No prueba ruta operativa actual.
- Histórico: **28590 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1152; no confundir con las direcciones 53/55 del bus remoto.
- Disponible en banco, expansión AI/RS fotografiada. IDs configurados 2 y 3. Canal RS4 permanece cero en todo el resumen; no se deduce equipo ausente.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 521344 | 606839 | 28590 / 28590 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 421924 | 494927 | 28590 / 28590 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 982709 | 1194708 | 28590 / 28590 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 0 | 0 | 0 / 28590 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

### U14 - radio `076351302BAB`

- Tipo histórico **6**; analizador **habilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054F8 - 186250C054EC - U14. No prueba ruta operativa actual.
- Histórico: **28515 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1248; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Dirección decimal / hex | Palabras | Conversión | Indice histórico | Mínimo | Máximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 100928 | 272143 | 28515 / 28515 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 100959 | 272217 | 28515 / 28515 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil histórico.

### U15 - radio `186352319CDA`

- Tipo histórico **4**; analizador **deshabilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - U15. No prueba ruta operativa actual.
- Histórico: **13190 filas**, 2025-10-29T00:00:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1344; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI histórico | Indice | Mínimo | Máximo | No cero / filas | Identificación del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 0 | 1476805374 | 13170 / 13190 | Pendiente |
| DI2 candidato | 3 | 0 | 1140850688 | 1 / 13190 | Pendiente |
| DI3 candidato | 4 | 0 | 1084752384 | 4 / 13190 | Pendiente |
| DI4 candidato | 5 | 0 | 137363456 | 9 / 13190 | Pendiente |

DI5-DI10: el perfil histórico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

**Datos fuera del mapa esperado:** Indice 14: 20 filas no cero, rango 0..14539733; Indice 15: 20 filas no cero, rango 0..19683614; Indice 16: 20 filas no cero, rango 0..1459953; Indice 17: 20 filas no cero, rango 0..662674; Indice 18: 4 filas no cero, rango 0..3105902; Indice 19: 4 filas no cero, rango 0..375222; Indice 20: 4 filas no cero, rango 0..3960828; Indice 21: 4 filas no cero, rango 0..249876; Indice 22: 4 filas no cero, rango 0..3606223; Indice 23: 4 filas no cero, rango 0..327478. Se conservan como anomalía/cambio histórico posible; no se asignan a equipos nuevos.

### U16 - radio `076351302B84`

- Tipo histórico **4**; analizador **deshabilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054F5 - 186250C054FA - 186250C051CF - U16. No prueba ruta operativa actual.
- Histórico: **28144 filas**, 2025-10-29T03:45:00+00:00 a 2026-08-23T11:00:00+00:00.
- Referencia nueva Modbus TCP: base 1440; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI histórico | Indice | Mínimo | Máximo | No cero / filas | Identificación del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 143159 | 4294967295 | 28144 / 28144 | Pendiente |
| DI2 candidato | 3 | 0 | 4294967295 | 2 / 28144 | Pendiente |
| DI3 candidato | 4 | 0 | 4294967295 | 2 / 28144 | Pendiente |
| DI4 candidato | 5 | 0 | 4294967295 | 8 / 28144 | Pendiente |

DI5-DI10: el perfil histórico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U17 - radio `076351302BC7`

- Tipo histórico **4**; analizador **deshabilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - 186250C054F5 - 186250C054FA - U17. No prueba ruta operativa actual.
- Histórico: **28045 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1536; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI histórico | Indice | Mínimo | Máximo | No cero / filas | Identificación del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 17501 | 3222062369 | 28045 / 28045 | Pendiente |
| DI2 candidato | 3 | 0 | 2684363264 | 10 / 28045 | Pendiente |
| DI3 candidato | 4 | 0 | 1074003968 | 4 / 28045 | Pendiente |
| DI4 candidato | 5 | 0 | 1342181632 | 12 / 28045 | Pendiente |

DI5-DI10: el perfil histórico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U18 - radio `076351302B7C`

- Tipo histórico **4**; analizador **deshabilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - U18. No prueba ruta operativa actual.
- Histórico: **28635 filas**, 2025-10-29T10:30:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1632; no confundir con las direcciones 53/55 del bus remoto.
- Campo DI1 histórico constante en 1463472; causa desconocida.

| Campo DI histórico | Indice | Mínimo | Máximo | No cero / filas | Identificación del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 1463472 | 1463472 | 28635 / 28635 | Pendiente |
| DI2 candidato | 3 | 0 | 0 | 0 / 28635 | Pendiente |
| DI3 candidato | 4 | 0 | 0 | 0 / 28635 | Pendiente |
| DI4 candidato | 5 | 0 | 0 | 0 / 28635 | Pendiente |

DI5-DI10: el perfil histórico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U19 - radio `076351302BC2`

- Tipo histórico **4**; analizador **deshabilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 076351302BB3 - U19. No prueba ruta operativa actual.
- Histórico: **28628 filas**, 2025-10-29T10:30:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1728; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI histórico | Indice | Mínimo | Máximo | No cero / filas | Identificación del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 2073137 | 2312953 | 28628 / 28628 | Pendiente |
| DI2 candidato | 3 | 0 | 0 | 0 / 28628 | Pendiente |
| DI3 candidato | 4 | 0 | 0 | 0 / 28628 | Pendiente |
| DI4 candidato | 5 | 0 | 0 | 0 / 28628 | Pendiente |

DI5-DI10: el perfil histórico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U20 - radio `18634E30A2CB`

- Tipo histórico **4**; analizador **deshabilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 076351302BB3 - 076351302BC2 - U20. No prueba ruta operativa actual.
- Histórico: **28633 filas**, 2025-10-29T10:30:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1824; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI histórico | Indice | Mínimo | Máximo | No cero / filas | Identificación del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 237219 | 267478 | 28633 / 28633 | Pendiente |
| DI2 candidato | 3 | 0 | 0 | 0 / 28633 | Pendiente |
| DI3 candidato | 4 | 0 | 0 | 0 / 28633 | Pendiente |
| DI4 candidato | 5 | 0 | 0 | 0 / 28633 | Pendiente |

DI5-DI10: el perfil histórico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U21 - radio `076351302B99`

- Tipo histórico **4**; analizador **deshabilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054F8 - 186250C054EC - U21. No prueba ruta operativa actual.
- Histórico: **28645 filas**, 2025-10-29T08:15:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1920; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI histórico | Indice | Mínimo | Máximo | No cero / filas | Identificación del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 102190 | 33850926 | 28645 / 28645 | Pendiente |
| DI2 candidato | 3 | 0 | 0 | 0 / 28645 | Pendiente |
| DI3 candidato | 4 | 0 | 0 | 0 / 28645 | Pendiente |
| DI4 candidato | 5 | 0 | 0 | 0 / 28645 | Pendiente |

DI5-DI10: el perfil histórico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U22 - radio `076351302B9A`

- Tipo histórico **4**; analizador **deshabilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - 186250C05529 - U22. No prueba ruta operativa actual.
- Histórico: **25862 filas**, 2025-10-28T15:15:00+00:00 a 2026-08-23T11:15:00+00:00.
- Referencia nueva Modbus TCP: base 2016; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI histórico | Indice | Mínimo | Máximo | No cero / filas | Identificación del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 144117 | 3225540590 | 25862 / 25862 | Pendiente |
| DI2 candidato | 3 | 0 | 2281701376 | 5 / 25862 | Pendiente |
| DI3 candidato | 4 | 0 | 318767104 | 1 / 25862 | Pendiente |
| DI4 candidato | 5 | 0 | 2147649536 | 6 / 25862 | Pendiente |

DI5-DI10: el perfil histórico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U23 - radio `076351302B85`

- Tipo histórico **4**; analizador **deshabilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 186250C054E8 - 186250C054F5 - U23. No prueba ruta operativa actual.
- Histórico: **27908 filas**, 2025-10-29T10:30:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 2112; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI histórico | Indice | Mínimo | Máximo | No cero / filas | Identificación del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 309 | 1749090613 | 27908 / 27908 | Pendiente |
| DI2 candidato | 3 | 0 | 2147649536 | 8 / 27908 | Pendiente |
| DI3 candidato | 4 | 0 | 8389256 | 2 / 27908 | Pendiente |
| DI4 candidato | 5 | 0 | 402787395 | 4 / 27908 | Pendiente |

DI5-DI10: el perfil histórico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U24 - radio `076351302B9C`

- Tipo histórico **4**; analizador **deshabilitado**; dirección radio distinta del ID Modbus local.
- Ruta configurada: base - 076351302BB3 - U24. No prueba ruta operativa actual.
- Histórico: **28569 filas**, 2025-10-29T10:30:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 2208; no confundir con las direcciones 53/55 del bus remoto.
- Disponible en banco; DI1/DI2 ensayadas. DI2 histórico cero no contradice el ensayo posterior de cinco pulsos.

| Campo DI histórico | Indice | Mínimo | Máximo | No cero / filas | Identificación del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 61016 | 65075 | 28569 / 28569 | Pendiente |
| DI2 candidato | 3 | 0 | 0 | 0 / 28569 | Pendiente |
| DI3 candidato | 4 | 0 | 0 | 0 / 28569 | Pendiente |
| DI4 candidato | 5 | 0 | 0 | 0 / 28569 | Pendiente |

DI5-DI10: el perfil histórico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### 7.25 -ltima muestra conservada de las dos remotas disponibles

Consulta directa a SQLite en modo de solo lectura. En ambos casos el -ltimo timestamp tiene una sola versión en la base.

| Remota | -ltima fecha UTC | Campos observados | Interpretación permitida |
|---|---|---|---|
| U13 | 2026-08-23 17:15:00 | RS1=606839; RS2=494927; RS3=1194708; RS4=0 | Asociados respectivamente a ID2/53, ID2/55, ID3/53, ID3/55 según mapa; unidades desconocidas |
| U24 | 2026-08-23 17:15:00 | Indices DI históricos 2..5: 65075, 0, 0, 0 | El primer campo corresponde al acumulador candidato DI1; ningún equipo físico identificado |

La lectura de banco posterior de U24 llegó a DI1=62838 y DI2=5. El valor DI1 es inferior al -ltimo histórico: **no empalmar ambas series como un contador continuo** sin explicar el cambio (reset, reconfiguración u otra causa no determinada). El reloj de la respuesta de banco tampoco se considera fiable. No se calcula consumo a partir de esa diferencia.

## 8. Información que falta y dónde recuperarla

El manual ViewGest explica que nombre, descripción, tipo de magnitud, comentarios, factor multiplicativo y escalado bruto/físico se configuran en la **variable del servidor**, ligada a una concentradora, ID MicroRTU e Indice. Referencias: páginas impresas 38-40 (PDF 39-41), secciones 3.1.2.3.2 y 3.1.2.3.2.1. Sus ejemplos de energía activa, gas, agua y presión son posibilidades del producto, no una lista de equipos de ForumMadeira.

La copia BeagleBone no incluye la base SQL Server de ViewGest ni una exportación de esa indexación. Ese es el candidato principal para recuperar etiquetas y factores, antes de intentar adivinarlos por series numéricas.

| Prioridad | Evidencia a conseguir | Datos que resolvería |
|---|---|---|
| 1 | Exportación autorizada de variables e indexación del sitio ViewGest | Uxx/canal - nombre, ubicación, magnitud, factor y escala |
| 1 | Fotos de placas de características de analizadores y sus pantallas de comunicación | Modelo, ID, baudrate, paridad, mapa de registros |
| 1 | Esquema/as-built o listado de puntos de puesta en marcha | Canal - cable - equipo; referencias de DI y AI |
| 2 | Etiquetas y recorrido de cables del armario original | Asociación física y bus local de cada ID |
| 2 | Manual/esquema de STM-X3-2AI-RS485-1 y firmware instalado | Parâmetros fijos/configurables, función Modbus, escala AI y calidad RS |
| 2 | Fichas de transmisores AI1/AI2 | 4-20 mA o 0-10 V, rango, unidades, alimentación |
| 2 | Lectura A2 de U13 sin cambios de configuración | Valores brutos actuales; contraste contra aparato conocido |
| 3 | Ensayo controlado de cada DI y AI identificada | Correspondencia de canal, factor y comportamiento |

No hay que reiniciar Java para esta investigación: su inicialización puede escribir configuración. No enviar A9, cambiar jumpers, aplicar tensión a DI ni ajustar analizadores solo para descubrir qué había instalado. La búsqueda realizada fue local, sin SSH ni modificaciones de campo.

### Ficha que se debe completar por dispositivo

| Campo | Valor a registrar |
|---|---|
| Remota / ID radio / canal / bornero | Identificador inequívoco |
| Tag de instalación / ubicación / servicio | Del plano o etiqueta, no inferido |
| Fabricante / modelo / número de serie | Foto y referencia |
| Señal DI | Contacto/pulso, factor impulsos/unidad, anchura y frecuencia documentadas |
| Señal RS485 | ID, baudrate, paridad, bits/parada, función, dirección y base, cantidad, formato, orden, escala |
| Señal AI | Corriente/tensión, selector, rango bruto, rango físico, unidad y esquema del lazo |
| Evidencia | Archivo/foto/página/fecha de lectura |
| Estado | Configurado / observado / validado físicamente / pendiente |

## 9. Registro de hallazgos y mantenimiento

| Fecha | Hallazgo | Consecuencia |
|---|---|---|
| 2026-09-23 | Fotos F7/F8 identifican STM-X3-2AI-RS485-1 y selección 4-20 mA | La capacidad analógica de U13 deja de ser una suposición |
| 2026-09-23 | Inscripción MODBUS RTU en expansión U13 | Confirma familia de protocolo de esa placa, no función/baudrate |
| 2026-09-23 | Las 100 entradas del mapa usan 53/55, longitud2, tipo0 | Inventario completo incluido por unidad |
| 2026-09-23 | U13 RS4 histórico siempre cero; U24 DI2 antiguo cero pero cambia en banco | No convertir cero en ausencia física |
| 2026-09-23 | Posiciones AI históricas rellenadas por perfiles | No deducir ausencia de sensores 4-20 mA |
| 2026-09-23 | ViewGest alberga nombre/indexación/escalado a nivel servidor | Priorizar recuperar esa configuración autorizadamente |

Actualizar este archivo añadiendo fuente y fecha para cada identificación nueva. No reemplazar silenciosamente el mapa histórico por el de banco. Mantener los valores brutos originales y distinguir los registros del bus RS485 de los publicados por el nuevo servidor TCP.

Relacionados: [inventario de tarjetas](INVENTARIO_TARJETAS.md), [adquisición y mapa TCP](ADQUISICION.md), [Indice general](INDICE.md).

### Huellas de fuentes principales

SHA-256 para identificar exactamente la evidencia usada, sin copiar su contenido privado:

| Fuente | SHA-256 |
|---|---|
| `data/raw/extraido/home/actemium/apps/xthreeconpi/config/units.txt` | `426e31be37186e0aa1061b4171f08ca22e9f445adf5586d87861a36a6a2a95c1` |
| `data/processed/resumen_historicos.json` | `b3f7314b38f16a4411f35b6fa837da0ee86c6a6d05de4b24c64e20ac0bcdbb9e` |
| `data/processed/java_estatico/classes_Analyzer.txt` | `3ec34c67d5a8d73d3d4b0b5291db24e17c69703eb40902bdfdf2aa786eedda07` |
| `data/processed/java_estatico/classes_eUnit.txt` | `a905c17cee5a31263ed93e26e6a4fed83384d0dded5a618cd851989db2b3112e` |
| `data/processed/java_estatico/classes_eLog.txt` | `465c4cdf181c898551ab9c9dcf37a2deff803a45efe31611be04e36ee846c49d` |

Comprobacion de consistencia: las 24 entradas coinciden con units.txt y los recuentos por unidad del resumen coinciden con SQLite abierta en solo lectura. No se han filtrado ni corregido las series.

### Fotografías originales enlazadas

Se conservan localmente y siguen ignoradas por Git. Los enlaces no publican ni copian las imágenes.

- [F1 - WhatsApp Image 2026-09-21 at 13.54.47 (1).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.47%20%281%29.jpeg)
- [F2 - WhatsApp Image 2026-09-21 at 13.54.47 (2).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.47%20%282%29.jpeg)
- [F3 - WhatsApp Image 2026-09-21 at 13.54.47 (3).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.47%20%283%29.jpeg)
- [F4 - WhatsApp Image 2026-09-21 at 13.54.47.jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.47.jpeg)
- [F5 - WhatsApp Image 2026-09-21 at 13.54.48 (1).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.48%20%281%29.jpeg)
- [F6 - WhatsApp Image 2026-09-21 at 13.54.48 (2).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.48%20%282%29.jpeg)
- [F7 - WhatsApp Image 2026-09-21 at 13.54.48 (3).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.48%20%283%29.jpeg)
- [F8 - WhatsApp Image 2026-09-21 at 13.54.48 (4).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.48%20%284%29.jpeg)
- [F9 - WhatsApp Image 2026-09-21 at 13.54.48.jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.48.jpeg)

## Anexo: comportamiento cronologico de cada canal configurado

Fuente derivada: `data/processed/tendencias_dispositivos.json`. Valores ya tratados por Java, sin unidades atribuidas. Subidas/bajadas no son pulsos individuales ni consumos.

| Remota | Canal / indice historico | Primero | Ultimo | Subidas | Bajadas | Iguales |
|---|---|---:|---:|---:|---:|---:|
| U01 | RS1 / 14 | 92227 | 126259 | 13326 | 3 | 14314 |
| U01 | RS2 / 15 | 5228 | 5228 | 7 | 7 | 27629 |
| U01 | RS3 / 16 | 41956 | 49349 | 6720 | 6 | 20917 |
| U01 | RS4 / 17 | 0 | 0 | 4 | 4 | 27635 |
| U01 | RS5 / 18 | 114984 | 131449 | 13131 | 9 | 14503 |
| U01 | RS6 / 19 | 805 | 805 | 1 | 1 | 27641 |
| U01 | RS7 / 20 | 196785 | 233729 | 17518 | 5 | 10120 |
| U01 | RS8 / 21 | 45088 | 54137 | 8879 | 6 | 18758 |
| U01 | RS9 / 22 | 234674 | 303928 | 19855 | 12 | 7776 |
| U01 | RS10 / 23 | 31237 | 35939 | 4636 | 11 | 22996 |
| U02 | RS1 / 14 | 85447 | 106914 | 3864 | 3 | 23677 |
| U02 | RS2 / 15 | 0 | 0 | 2 | 2 | 27540 |
| U02 | RS3 / 16 | 79116 | 111532 | 4804 | 3 | 22737 |
| U02 | RS4 / 17 | 10 | 15 | 8 | 3 | 27533 |
| U02 | RS5 / 18 | 397204 | 481522 | 20205 | 9 | 7330 |
| U02 | RS6 / 19 | 528036 | 638580 | 25491 | 10 | 2043 |
| U02 | RS7 / 20 | 268410 | 325701 | 19789 | 13 | 7742 |
| U02 | RS8 / 21 | 92560 | 117477 | 17177 | 17 | 10350 |
| U03 | RS1 / 14 | 333049 | 379069 | 20167 | 6 | 6958 |
| U03 | RS2 / 15 | 224129 | 257258 | 19483 | 7 | 7641 |
| U03 | RS3 / 16 | 139152 | 177358 | 4375 | 12 | 22744 |
| U03 | RS4 / 17 | 177 | 177 | 8 | 8 | 27115 |
| U03 | RS5 / 18 | 297273 | 360310 | 19219 | 6 | 7906 |
| U03 | RS6 / 19 | 19575 | 23010 | 3365 | 7 | 23759 |
| U03 | RS7 / 20 | 283227 | 365747 | 19354 | 11 | 7766 |
| U03 | RS8 / 21 | 29751 | 285235 | 18324 | 11 | 8796 |
| U03 | RS9 / 22 | 2688 | 3119 | 150 | 10 | 26971 |
| U03 | RS10 / 23 | 3521 | 4107 | 156 | 10 | 26965 |
| U04 | RS1 / 14 | 127794 | 150794 | 19948 | 0 | 8687 |
| U04 | RS2 / 15 | 221179 | 267389 | 20674 | 0 | 7961 |
| U04 | RS3 / 16 | 263220 | 318384 | 17066 | 0 | 11569 |
| U04 | RS4 / 17 | 95475 | 114691 | 15948 | 0 | 12687 |
| U04 | RS5 / 18 | 496846 | 604761 | 20569 | 0 | 8066 |
| U04 | RS6 / 19 | 24287 | 28628 | 4341 | 0 | 24294 |
| U04 | RS7 / 20 | 244872 | 292033 | 28635 | 0 | 0 |
| U04 | RS8 / 21 | 461534 | 553534 | 28635 | 0 | 0 |
| U05 | RS1 / 14 | 98513 | 122650 | 23093 | 10 | 4289 |
| U05 | RS2 / 15 | 25184 | 33299 | 7851 | 11 | 19530 |
| U06 | RS1 / 14 | 441143 | 525910 | 22596 | 0 | 6039 |
| U06 | RS2 / 15 | 7280 | 7589 | 309 | 0 | 28326 |
| U06 | RS3 / 16 | 400689 | 481802 | 20571 | 0 | 8064 |
| U06 | RS4 / 17 | 1.4302e+06 | 1.76579e+06 | 20534 | 0 | 8101 |
| U06 | RS5 / 18 | 502084 | 617549 | 20696 | 0 | 7939 |
| U06 | RS6 / 19 | 103324 | 127951 | 19594 | 0 | 9041 |
| U06 | RS7 / 20 | 1439 | 1792 | 300 | 0 | 28335 |
| U06 | RS8 / 21 | 54 | 65 | 11 | 0 | 28624 |
| U07 | RS1 / 14 | 4062 | 4708 | 96 | 8 | 27482 |
| U07 | RS2 / 15 | 139 | 158 | 18 | 2 | 27566 |
| U07 | RS3 / 16 | 2413 | 2791 | 25 | 5 | 27556 |
| U07 | RS4 / 17 | 71 | 80 | 13 | 4 | 27569 |
| U07 | RS5 / 18 | 72248 | 97375 | 12090 | 6 | 15490 |
| U07 | RS6 / 19 | 15348 | 21853 | 4948 | 9 | 22629 |
| U07 | RS7 / 20 | 133846 | 151778 | 3662 | 9 | 23915 |
| U07 | RS8 / 21 | 32610 | 36800 | 3099 | 9 | 24478 |
| U07 | RS9 / 22 | 8796 | 10572 | 308 | 9 | 27269 |
| U07 | RS10 / 23 | 3188 | 3813 | 283 | 3 | 27300 |
| U08 | RS1 / 14 | 305244 | 336135 | 21899 | 8 | 5886 |
| U08 | RS2 / 15 | 895560 | 1.05207e+06 | 27788 | 5 | 0 |
| U08 | RS3 / 16 | 148306 | 236132 | 27791 | 2 | 0 |
| U08 | RS4 / 17 | 1.45837e+06 | 1.74398e+06 | 27788 | 5 | 0 |
| U08 | RS5 / 18 | 107692 | 129131 | 14820 | 11 | 12962 |
| U08 | RS6 / 19 | 238704 | 277170 | 14357 | 11 | 13425 |
| U08 | RS7 / 20 | 217126 | 265045 | 27703 | 11 | 79 |
| U08 | RS8 / 21 | 425378 | 518939 | 27775 | 8 | 10 |
| U08 | RS9 / 22 | 80061 | 102891 | 21808 | 14 | 5971 |
| U08 | RS10 / 23 | 193394 | 232706 | 27771 | 10 | 12 |
| U09 | RS1 / 14 | 94408 | 113095 | 18181 | 12 | 9620 |
| U09 | RS2 / 15 | 159870 | 192718 | 27177 | 12 | 624 |
| U09 | RS3 / 16 | 96913 | 117438 | 19968 | 12 | 7833 |
| U09 | RS4 / 17 | 109600 | 132899 | 22382 | 8 | 5423 |
| U09 | RS5 / 18 | 94585 | 115150 | 16877 | 11 | 10925 |
| U09 | RS6 / 19 | 404686 | 485672 | 27793 | 14 | 6 |
| U09 | RS7 / 20 | 103676 | 125417 | 19009 | 12 | 8792 |
| U09 | RS8 / 21 | 378510 | 453836 | 26994 | 10 | 809 |
| U09 | RS9 / 22 | 98488 | 117530 | 18534 | 8 | 9271 |
| U09 | RS10 / 23 | 166116 | 198290 | 27221 | 12 | 580 |
| U10 | RS1 / 14 | 1.43095e+07 | 1.70672e+07 | 23582 | 7 | 4074 |
| U10 | RS2 / 15 | 1.93862e+07 | 2.29311e+07 | 25811 | 6 | 1846 |
| U10 | RS3 / 16 | 1.43853e+06 | 1.70768e+06 | 21686 | 8 | 5969 |
| U10 | RS4 / 17 | 652947 | 774417 | 19925 | 7 | 7731 |
| U10 | RS5 / 18 | 3.01131e+06 | 3.94636e+06 | 17985 | 14 | 9664 |
| U10 | RS6 / 19 | 371348 | 457477 | 4455 | 8 | 23200 |
| U10 | RS7 / 20 | 3.90615e+06 | 4.35205e+06 | 7923 | 9 | 19731 |
| U10 | RS8 / 21 | 249401 | 279192 | 1785 | 8 | 25870 |
| U10 | RS9 / 22 | 3.57103e+06 | 3.84824e+06 | 7927 | 8 | 19728 |
| U10 | RS10 / 23 | 324824 | 364303 | 3220 | 10 | 24433 |
| U11 | RS1 / 14 | 576933 | 710818 | 28080 | 1 | 544 |
| U11 | RS2 / 15 | 0 | 0 | 0 | 0 | 28625 |
| U11 | RS3 / 16 | 1.56157e+06 | 1.85519e+06 | 28624 | 1 | 0 |
| U11 | RS4 / 17 | 38759 | 59427 | 17361 | 0 | 11264 |
| U12 | RS1 / 14 | 340941 | 408810 | 23126 | 2 | 3146 |
| U12 | RS2 / 15 | 44345 | 51736 | 6819 | 6 | 19449 |
| U12 | RS3 / 16 | 328950 | 386118 | 15436 | 5 | 10833 |
| U12 | RS4 / 17 | 15741 | 18161 | 2324 | 9 | 23941 |
| U13 | RS1 / 14 | 521344 | 606839 | 27086 | 1 | 1502 |
| U13 | RS2 / 15 | 421924 | 494927 | 28587 | 0 | 2 |
| U13 | RS3 / 16 | 982709 | 1.19471e+06 | 28589 | 0 | 0 |
| U13 | RS4 / 17 | 0 | 0 | 0 | 0 | 28589 |
| U14 | RS1 / 14 | 100928 | 125802 | 9354 | 1625 | 17533 |
| U14 | RS2 / 15 | 217095 | 272217 | 9854 | 434 | 18224 |
| U15 | DI1 candidato / 2 | 141523 | 149863 | 501 | 8 | 12674 |
| U15 | DI2 candidato / 3 | 0 | 0 | 1 | 1 | 13181 |
| U15 | DI3 candidato / 4 | 0 | 0 | 4 | 4 | 13175 |
| U15 | DI4 candidato / 5 | 0 | 0 | 9 | 9 | 13165 |
| U16 | DI1 candidato / 2 | 165176 | 181918 | 14890 | 6 | 13201 |
| U16 | DI2 candidato / 3 | 0 | 0 | 2 | 2 | 28093 |
| U16 | DI3 candidato / 4 | 0 | 0 | 2 | 2 | 28093 |
| U16 | DI4 candidato / 5 | 0 | 0 | 8 | 8 | 28081 |
| U17 | DI1 candidato / 2 | 567688 | 619183 | 4594 | 13 | 23331 |
| U17 | DI2 candidato / 3 | 0 | 0 | 9 | 9 | 27920 |
| U17 | DI3 candidato / 4 | 0 | 0 | 4 | 4 | 27930 |
| U17 | DI4 candidato / 5 | 0 | 0 | 12 | 12 | 27914 |
| U18 | DI1 candidato / 2 | 1.46347e+06 | 1.46347e+06 | 0 | 0 | 28634 |
| U18 | DI2 candidato / 3 | 0 | 0 | 0 | 0 | 28634 |
| U18 | DI3 candidato / 4 | 0 | 0 | 0 | 0 | 28634 |
| U18 | DI4 candidato / 5 | 0 | 0 | 0 | 0 | 28634 |
| U19 | DI1 candidato / 2 | 2.07314e+06 | 2.31295e+06 | 18275 | 0 | 10352 |
| U19 | DI2 candidato / 3 | 0 | 0 | 0 | 0 | 28627 |
| U19 | DI3 candidato / 4 | 0 | 0 | 0 | 0 | 28627 |
| U19 | DI4 candidato / 5 | 0 | 0 | 0 | 0 | 28627 |
| U20 | DI1 candidato / 2 | 237219 | 267478 | 15869 | 0 | 12763 |
| U20 | DI2 candidato / 3 | 0 | 0 | 0 | 0 | 28632 |
| U20 | DI3 candidato / 4 | 0 | 0 | 0 | 0 | 28632 |
| U20 | DI4 candidato / 5 | 0 | 0 | 0 | 0 | 28632 |
| U21 | DI1 candidato / 2 | 102190 | 102190 | 1 | 1 | 28642 |
| U21 | DI2 candidato / 3 | 0 | 0 | 0 | 0 | 28644 |
| U21 | DI3 candidato / 4 | 0 | 0 | 0 | 0 | 28644 |
| U21 | DI4 candidato / 5 | 0 | 0 | 0 | 0 | 28644 |
| U22 | DI1 candidato / 2 | 174740 | 186753 | 3127 | 14 | 22690 |
| U22 | DI2 candidato / 3 | 0 | 0 | 5 | 5 | 25821 |
| U22 | DI3 candidato / 4 | 0 | 0 | 1 | 1 | 25829 |
| U22 | DI4 candidato / 5 | 0 | 0 | 6 | 6 | 25819 |
| U23 | DI1 candidato / 2 | 309 | 309 | 15 | 15 | 27877 |
| U23 | DI2 candidato / 3 | 0 | 0 | 8 | 8 | 27891 |
| U23 | DI3 candidato / 4 | 0 | 0 | 2 | 2 | 27903 |
| U23 | DI4 candidato / 5 | 0 | 0 | 4 | 4 | 27899 |
| U24 | DI1 candidato / 2 | 61016 | 65075 | 3743 | 0 | 24825 |
| U24 | DI2 candidato / 3 | 0 | 0 | 0 | 0 | 28568 |
| U24 | DI3 candidato / 4 | 0 | 0 | 0 | 0 | 28568 |
| U24 | DI4 candidato / 5 | 0 | 0 | 0 | 0 | 28568 |
