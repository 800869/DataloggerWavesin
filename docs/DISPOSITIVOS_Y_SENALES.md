# Dispositivos de campo y se?ales recuperadas: RS485, DI y anal?gicas

Fecha de recopilaci?n: 23/09/2026. Documento de investigaci?n de la instalaci?n original y del banco actual.

**Objetivo:** reunir en un ?nico lugar las identidades, conexiones, mapas y evidencias disponibles para identificar qu? equipos estaban conectados a cada remota. No convertir una capacidad de hardware, un cero o un valor hist?rico en una identificaci?n f?sica inventada.

## ?ndice

1. [Conclusiones y grado de certeza](#1-conclusiones-y-grado-de-certeza)
2. [Fuentes y alcance](#2-fuentes-y-alcance)
3. [Hardware fotografiado](#3-hardware-fotografiado)
4. [Par?metros RS485 recuperados](#4-par?metros-rs485-recuperados)
5. [DI: entradas, contadores y equipos](#5-di-entradas-contadores-y-equipos)
6. [Anal?gicas: 0?10 V y 4?20 mA](#6-anal?gicas-010-v-y-420-ma)
7. [Fichas de las 24 remotas](#7-fichas-de-las-24-remotas)
8. [Informaci?n que falta y d?nde recuperarla](#8-informaci?n-que-falta-y-d?nde-recuperarla)
9. [Registro de hallazgos y mantenimiento](#9-registro-de-hallazgos-y-mantenimiento)

## 1. Conclusiones y grado de certeza

| Hallazgo | Estado | Evidencia |
|---|---|---|
| 24 remotas U01?U24 configuradas | Confirmado en copia | S1 |
| 14 remotas con analizador habilitado, 100 valores RS configurados | Confirmado en copia | S1, S3 |
| 50 asociaciones remota/ID esclavo | Derivado del mapa | S1; dos valores por ID; no prueba 50 aparatos f?sicos ?nicos |
| U24: radio 076351302B9C, placa de diez DI | Confirmado visualmente y por ensayo | F3/F9, S7 |
| U13: radio 076351302B95, diez DI y expansi?n de dos AI + RS485 | Confirmado visualmente y por usuario | F7/F8, S7 |
| Expansi?n U13 admite selecci?n 0?10 V / 4?20 mA | Confirmado por serigraf?a | F7/F8; no certifica posici?n actual ni calibraci?n |
| Expansi?n U13 rotulada Modbus RTU | Confirmado por serigraf?a | F7/F8 |
| Qu? contador/sensor concreto ocupaba cada canal | Sin identificaci?n recuperada | No hay marca/modelo/tag f?sico asociado a cada canal en S1/S4 |
| Baudrate, paridad y funci?n 03/04 del bus remoto | No recuperados | El mensaje setModbus revisado no los transporta |
| Magnitudes, escalas, factores de impulsos y unidades | No recuperados para la instalaci?n | ViewGest permite configurarlos, pero no se dispone de esa configuraci?n del sitio |

**Leyenda:** ?configurado? describe la copia, ?observado? describe fotos/valores/ensayos, ?inferencia? es una interpretaci?n pendiente, ?desconocido? no equivale a inexistente.

No se han encontrado etiquetas de analizadores, contadores de agua/gas o transmisores de presi?n/caudal conectados. S? se identifican las placas de adquisici?n. Las fotos son de banco, con bornes de se?al sin cables; no constituyen un plano del cableado original.

## 2. Fuentes y alcance

| C?digo | Fuente local | Qu? aporta |
|---|---|---|
| S1 | `data/raw/extraido/home/actemium/apps/xthreeconpi/config/units.txt` | Radio, nombre Uxx, tipo hist?rico, ruta y mapa de analizador |
| S2 | `data/raw/extraido/home/actemium/apps/xthreeconpi/config/settings.txt` | Ciclos del concentrador; contiene informaci?n privada que no se reproduce |
| S3 | `data/processed/java_estatico/classes_Analyzer.txt`, `classes_eUnit.txt`, `classes_eLog.txt`, `utils_Utils.txt` | Significado de campos, mensaje A9 de configuraci?n y conversiones |
| S4 | `data/processed/resumen_historicos.json` y `data/database/historicos.sqlite` | Rangos, cobertura, 32 posiciones por lectura y n?mero de valores no nulos |
| S5 | `docs/private/INFORME_BEAGLEBONE.md` | An?lisis previo y anomal?as; sus l?mites anteriores se actualizan con las fotos |
| S6 | Manual ViewGest en `docs/private/`, texto en `data/processed/manual_texto.txt` | Capacidades gen?ricas y d?nde se asignan nombres/escalas |
| S7 | Conversaci?n aportada y `docs/private/CODEX CHAT.txt` | Identificaci?n de dos remotas, consultas A2 y ensayos de DI |
| S8 | `data/processed/inventario.jsonl` y archivos recuperados de SD | B?squeda de configuraciones adicionales y alcance de la copia |
| S9 | `logs/logPi202607.txt`, `logs/logPi202609.txt` | Fallos documentados de configuraci?n Modbus; no garantizan aceptaci?n del mapa |
| F1?F9 | Nueve fotos en `docs/private/IMAGENES PLACAS/` | Identificaci?n visual de placas y bornes |

Se revisaron las nueve fotos, el mapa de todas las unidades, las clases Java de analizador/conversi?n, los res?menes de todos los canales de las 24 unidades y el texto extra?do del manual. SQLite se abri? en modo solo lectura para comprobar esquema y formato. Los rangos tabulados proceden del resumen existente: no se han recalculado eliminando anomal?as.

La b?squeda de nombres/configuraciones relevantes en el inventario TAR encontr? units.txt y settings.txt, pero no un mapa de nombres de equipos de campo ni firmware de las MicroRTU. Los tres archivos recuperados por SD (`sysconf.txt`, `START.HTM`, `ID.txt`) no aportaron coincidencias de par?metros de analizador en la b?squeda dirigida. No se afirma una auditor?a sem?ntica de todo Debian ni de bibliotecas de terceros.

Los documentos privados, fotos, copia del sistema y credenciales permanecen fuera de Git. Este informe referencia esas fuentes, sin incorporar credenciales ni configuraci?n de red privada. En un clon p?blico las fuentes privadas no estar?n disponibles.

## 3. Hardware fotografiado

Todas las fotos llevan el prefijo `WhatsApp Image 2026-09-21 at 13.54.` y extensi?n `.jpeg`.

| Foto | Sufijo del archivo | Observaci?n directamente legible |
|---|---|---|
| F1 | `47 (1)` | M?dulo desmontado: PCB CS-PCB-029-C; no permite asociar por s? solo un sensor |
| F2 | `47 (2)` | Actemium STM-X3-10DI-2, 30-06-2014; LOW POWER WAVENIS RADIO, 25mW; EXPANSION BOARD |
| F3 | `47 (3)` | U24: radio 076351302B9C / 244-201A; diez DI; SN STM17070043 |
| F4 | `47` | Base radio 186254C072B0 / 245-201A; cape Actemium BBB-CAPE-02, 2020-02-04 |
| F5 | `48 (1)` | Reverso STM-X3-10DI, DC 3,6 V, ensayo 04-07-2017; etiqueta 1718790062 |
| F6 | `48 (2)` | Otro reverso STM-X3-10DI, DC 3,6 V, ensayo 04-07-2017; etiqueta 1718790015 |
| F7 | `48 (3)` | U13: 076351302B95 / 244-201A; expansi?n STM-X3-2AI-RS485-1, 17-04-2014 |
| F8 | `48 (4)` | Segunda vista de U13 y selecci?n de AI, bornes RS485 MODBUS RTU |
| F9 | `48` | Segunda vista U24, sin expansi?n montada; DI1?DI10 y SN STM17070043 |

Las etiquetas de reverso F5/F6 no se asignan a U13/U24 porque en esas caras no se ve simult?neamente el ID radio. `244-201A` y `245-201A` son inscripciones de los m?dulos fotografiados, no modelos de analizadores RS485.

### 3.1 U24: placa base de DI

- Actemium **STM-X3-10DI-2**, fecha de dise?o impresa 30-06-2014.
- Diez entradas DI1?DI10; pares de terminales con leyenda `+3.3V / DI`.
- Conectores inferiores X3?X7, cada conjunto agrupa dos entradas.
- Radio `076351302B9C`, etiqueta `244-201A`; no se aprecia expansi?n anal?gica montada.
- Conectores de alimentaci?n P1/P2, expansi?n y botones STATUS/RESET visibles.
- Las pruebas de banco asocian DI1 y DI2 con los dos primeros contadores B2.
- No hay en las fotos contador de agua, gas, energ?a o contacto de proceso unido a DI.

### 3.2 U13: placa base y expansi?n

- Base STM-X3-10DI-2 con radio `076351302B95`, etiqueta `244-201A`.
- Expansi?n **STM-X3-2AI-RS485-1**, fecha 17-04-2014.
- Bornero anal?gico X3: `+ AI1 -`, `+ AI2 -`.
- Dos selectores JP1/JP2; leyenda `AI JUMPERS`, `0-10V` y `4-20mA`.
- Bornero X2 rotulado **RS485 MODBUS RTU**, con etiquetas `B+` y `A-`.
- No se deduce solo de la imagen la conexi?n interna de los cuatro tornillos RS485, terminaci?n, polarizaci?n o aislamiento.
- La fuente de banco visible est? rotulada Mean Well RS-15-3.3 / salida 3,3 V. Es alimentaci?n del montaje fotografiado, no un dispositivo de medida ni evidencia de alimentaci?n hist?rica.
- En las fotos AI, DI y RS485 no tienen cables de campo. No se deduce modo de los jumpers por apariencia ni se propone modificarlos.

### 3.3 BeagleBone: no confundir su cape con la expansi?n remota

El cape BBB-CAPE-02 tiene leyendas PWR IN +5V/GND, RS232 TX/RX/GND y RS485 B+/A-/GND. Eso prueba conectores f?sicos, no que Java estuviera consultando analizadores por ese RS485. El flujo recuperado usa UART4 hacia la base radio; las consultas a analizadores se configuran en las remotas. Los 9600 8N1 comprobados son de ese enlace local de radio.

## 4. Par?metros RS485 recuperados

### 4.1 Qu? significa cada entrada

`canal&esclavo_direccion_longitud_conversion`, por ejemplo `1&2_53_2_0`:

| Campo | Ejemplo | Interpretaci?n comprobada |
|---|---:|---|
| Canal l?gico de la remota | 1 | Posici?n RS1; no es DI1 |
| ID esclavo Modbus | 2 | Direcci?n de equipo en el bus local de esa remota |
| Direcci?n configurada | 53 | Entero decimal; se transmite sin restar uno en setModbus |
| Longitud | 2 | Dos registros/palabras de 16 bits por valor |
| Conversi?n Java | 0 | Tratamiento entero de 32 bits; no float |

Todas las entradas recuperadas emplean direcciones **53 (0x0035) y 55 (0x0037)**, longitud 2 y conversi?n 0. Cada asociaci?n remota/esclavo aporta dos valores de 32 bits. Son 100 valores y 200 palabras configuradas, no necesariamente 100 peticiones de bus independientes: la planificaci?n interna del firmware no est? recuperada.

El m?todo `setModbus()` compone A9 con n?mero de canales y, por canal, ?ndice, esclavo, direcci?n de dos bytes y longitud. No env?a ah? baudrate, paridad, funci?n ni conversi?n Java. Esto sit?a parte del comportamiento en el firmware/configuraci?n local de la remota, que no est? en la copia. No se ha enviado A9 en esta recopilaci?n.

Los logs a?aden una limitaci?n: el 21/09/2026 a las 08:34:33 se registra para U01 `modbus configuration update timeout`; tambi?n hay timeouts en julio. Por tanto, **configuraci?n guardada no equivale a configuraci?n aceptada por la remota**. Tampoco el timeout demuestra que la remota careciera de una configuraci?n anterior v?lida. No se ha le?do una confirmaci?n actual de par?metros desde su firmware.

### 4.2 Tipo de dato y precauci?n de interpretaci?n

Java reconstruye cada campo como dos palabras, alta primero, y para tipo 0 conserva el entero si bit31=0. Si bit31=1 aplica `(-valor) & 0x7FFFFFFF`. Ejemplos de esa operaci?n: 0x80000000 pasa a 0; 0xFFFFFFFF pasa a 1. No equivale a interpretar sin m?s un int32 firmado ni a conservar un uint32. El c?digo est? en `eLog.ConvertModbusType`, rama 0; `Utils.checkBit` comprueba el bit.

Por ello los rangos de hist?ricos son **valores ya tratados por Java**, mientras los RS del lector nuevo son **brutos uint32**. Pueden diferir si estaba activo el bit31. No asignar float, signo, kWh, kvarh, factor de transformaci?n o escala por intuici?n. Se necesita el manual del analizador real. La correspondencia entre direcci?n 53 y una notaci?n de manual 400xx/300xx tampoco queda cerrada sin conocer funci?n y base del fabricante.

### 4.3 Par?metros todav?a sin recuperar

| Par?metro | Situaci?n |
|---|---|
| RS485 / Modbus RTU en expansi?n U13 | Confirmado visualmente |
| Baudrate del bus remoto | Desconocido |
| Paridad / bits de datos / parada del bus remoto | Desconocidos |
| Funci?n 03 o 04 | Desconocida |
| Timeout/reintentos propios del bus RS | Desconocidos; no confundir con timeout de radio |
| Orden original de palabras del analizador | Java combina alta primero; falta contrato del aparato/firmware |
| Modelo, firmware y n?mero de serie del analizador | No encontrado |
| Significado de 53 y 55 / unidad / factor | No encontrado |
| Terminaci?n, polarizaci?n, distancia y cableado original | No encontrados |
| Frescura/calidad propia del dato RS devuelto por radio | No documentada; B2 reciente no prueba una nueva transacci?n RS exitosa |

## 5. DI: entradas, contadores y equipos

U24 confirma contadores, no un simple estado abierto/cerrado. DI1 subi? durante maniobras, permaneci? al mantener contacto y no aument? al abrir en los ensayos aportados; cinco maniobras produjeron cuatro incrementos en una prueba. DI2 pas? de 0 a 5 tras cinco maniobras confirmadas por el usuario. No se certifican antirrebote, frecuencia m?xima, anchura m?nima de pulso ni un incremento por cada cierre.

El hist?rico tipo 4 guarda cuatro campos en posiciones 2..5. Su representaci?n de 32 columnas rellena otros campos con cero; por eso no puede usarse para demostrar que DI5..DI10 estaban libres. En tipos 6/7 Java rellena las posiciones DI con ceros: la ausencia de datos DI hist?ricos en U13 no demuestra ausencia de entradas/cableado.

No se recuperaron nombres de los contadores o contactos, ubicaci?n, magnitud (agua/gas/energ?a), relaci?n impulsos/unidad, tipo el?ctrico de cada sensor ni n?meros de serie. Los campos de tipo 4 con actividad sostenida sugieren acumuladores de impulsos, pero no identifican el equipo que los genera. Una cifra constante como la de U18 puede tener varias causas; no se clasifica como aver?a.

## 6. Anal?gicas: 0?10 V y 4?20 mA

La capacidad est? **confirmada en U13 por la placa STM-X3-2AI-RS485-1**. No se identifican sensores 4?20 mA concretos ni escalas f?sicas. Tampoco se extiende autom?ticamente la presencia de esa expansi?n a las otras 23 remotas.

| Se?al U13 | Bornes | Modo que admite la placa | Modo instalado | Sensor/modelo | Escala f?sica |
|---|---|---|---|---|---|
| AI1 | + AI1 - | 0?10 V / 4?20 mA por selecci?n | Pendiente | No identificado | No recuperada |
| AI2 | + AI2 - | 0?10 V / 4?20 mA por selecci?n | Pendiente | No identificado | No recuperada |

En B2 actual, AI1/AI2 son los uint16 brutos de bytes 55..58 contando B2 como byte0. No hay conversi?n a mA implementada ni prueba de que 4095/65535 sea fondo de escala. El campo separado que Java convierte `raw*5/4096`, hist?rico ?ndice1, **no identifica una AI de proceso ni prueba un lazo 4?20 mA**.

En la copia hist?rica todas las posiciones 12/13 tienen cero. Las ramas de tipos 4/6/7 revisadas insertan ceros en esos huecos; no permiten concluir que no hubo sensores anal?gicos. Adem?s, U24 devolvi? campos anal?gicos brutos no nulos aun sin expansi?n visible (por ejemplo 0x0C24 y 0x0CAA en una captura). Eso demuestra por qu? un n?mero no basta para declarar una entrada conectada o v?lida.

Pendientes para cada AI: modelo y rango del transmisor, dos/tres/cuatro hilos, alimentaci?n del lazo, aislamiento, polaridad, posici?n comprobada de selector, escalado raw?mA?magnitud, comportamiento de circuito abierto y etiquetas de campo. No se proponen conexiones o inyecci?n de corriente sin identificar estos puntos.

## 7. Fichas de las 24 remotas

**C?mo leer las tablas:** ?ndice hist?rico empieza en 0. RS l?gico k corresponde a ?ndice 13+k en la representaci?n JSON. ?No cero? cuenta filas cuyo valor no era cero, no transacciones v?lidas ni equipos conectados. M?nimo/m?ximo incluyen anomal?as, duplicados conflictivos y tratamientos Java; no son rangos nominales de sensores. Las fechas son UTC. La configuraci?n y los hist?ricos no son necesariamente coet?neos en cada cambio de equipo.

Para tipos 6/7 se tabulan todos los canales configurados. Para tipo4 se tabulan sus cuatro campos DI hist?ricos. AI1/AI2 siguen sin identificar en todas las unidades; solo la expansi?n f?sica de U13 est? comprobada. Ubicaci?n y marca/modelo de los dispositivos de campo: pendientes para todas salvo futuras incorporaciones documentadas.

### U01 ? radio `076351302B96`

- Tipo hist?rico **7**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? 186250C054F5 ? U01. No prueba ruta operativa actual.
- Hist?rico: **27644 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 0; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
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

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

**Datos fuera del mapa esperado:** ?ndice 24: 9 filas no cero, rango 0..1644167168; ?ndice 25: 2 filas no cero, rango 0..40960. Se conservan como anomal?a/cambio hist?rico posible; no se asignan a equipos nuevos.

### U02 ? radio `076351302B7E`

- Tipo hist?rico **7**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? 186250C054F5 ? U02. No prueba ruta operativa actual.
- Hist?rico: **27545 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 96; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 85447 | 1073960250 | 27545 / 27545 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 0 | 40978 | 2 / 27545 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 79116 | 17389967 | 27545 / 27545 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 10 | 49166 | 27545 / 27545 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 397204 | 1979242927 | 27545 / 27545 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 526858 | 1511594542 | 27545 / 27545 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 268410 | 1073453257 | 27545 / 27545 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 67255 | 2071229165 | 27545 / 27545 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

**Datos fuera del mapa esperado:** ?ndice 22: 8 filas no cero, rango 0..2147549184; ?ndice 23: 2 filas no cero, rango 0..1610613760; ?ndice 24: 6 filas no cero, rango 0..3221536768; ?ndice 25: 7 filas no cero, rango 0..84934912. Se conservan como anomal?a/cambio hist?rico posible; no se asignan a equipos nuevos.

### U03 ? radio `076351302B9D`

- Tipo hist?rico **7**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? 186250C054F5 ? U03. No prueba ruta operativa actual.
- Hist?rico: **27136 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 192; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
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

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

**Datos fuera del mapa esperado:** ?ndice 24: 5 filas no cero, rango 0..1610620928; ?ndice 25: 6 filas no cero, rango 0..1275068416. Se conservan como anomal?a/cambio hist?rico posible; no se asignan a equipos nuevos.

### U04 ? radio `076351302BCD`

- Tipo hist?rico **7**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? U04. No prueba ruta operativa actual.
- Hist?rico: **28636 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 288; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 127794 | 150794 | 28636 / 28636 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 221179 | 267389 | 28636 / 28636 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 263220 | 318384 | 28636 / 28636 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 95475 | 114691 | 28636 / 28636 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 496846 | 604761 | 28636 / 28636 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 24287 | 28628 | 28636 / 28636 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 244872 | 292033 | 28636 / 28636 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 461534 | 553534 | 28636 / 28636 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

### U05 ? radio `076351302BA7`

- Tipo hist?rico **6**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? U05. No prueba ruta operativa actual.
- Hist?rico: **27447 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 384; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 4324 | 2142399218 | 27447 / 27447 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 147 | 1140879392 | 27447 / 27447 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

**Datos fuera del mapa esperado:** ?ndice 16: 35 filas no cero, rango 0..1207959552; ?ndice 17: 37 filas no cero, rango 0..2148073472; ?ndice 18: 29 filas no cero, rango 0..328180; ?ndice 19: 29 filas no cero, rango 0..21226; ?ndice 20: 29 filas no cero, rango 0..323508; ?ndice 21: 29 filas no cero, rango 0..145957; ?ndice 22: 29 filas no cero, rango 0..3054; ?ndice 23: 29 filas no cero, rango 0..4018; ?ndice 25: 1 filas no cero, rango 0..24576. Se conservan como anomal?a/cambio hist?rico posible; no se asignan a equipos nuevos.

### U06 ? radio `076351302BB3`

- Tipo hist?rico **7**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? U06. No prueba ruta operativa actual.
- Hist?rico: **28636 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 480; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 441143 | 525910 | 28636 / 28636 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 7280 | 7589 | 28636 / 28636 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 400689 | 481802 | 28636 / 28636 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 1430196 | 1765793 | 28636 / 28636 |
| 5 | 4 | 53 / 0x0035 | 2 | 0 | 18 | 502084 | 617549 | 28636 / 28636 |
| 6 | 4 | 55 / 0x0037 | 2 | 0 | 19 | 103324 | 127951 | 28636 / 28636 |
| 7 | 5 | 53 / 0x0035 | 2 | 0 | 20 | 1439 | 1792 | 28636 / 28636 |
| 8 | 5 | 55 / 0x0037 | 2 | 0 | 21 | 54 | 65 | 28636 / 28636 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

### U07 ? radio `076351302B8F`

- Tipo hist?rico **7**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? 186250C054F5 ? 186250C054E4 ? U07. No prueba ruta operativa actual.
- Hist?rico: **27611 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 576; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
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

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

**Datos fuera del mapa esperado:** ?ndice 24: 7 filas no cero, rango 0..2684363264; ?ndice 25: 9 filas no cero, rango 0..2550136832. Se conservan como anomal?a/cambio hist?rico posible; no se asignan a equipos nuevos.

### U08 ? radio `076351302B8D`

- Tipo hist?rico **7**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? 186250C054F5 ? 186250C054E4 ? U08. No prueba ruta operativa actual.
- Hist?rico: **27800 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 672; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
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

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

**Datos fuera del mapa esperado:** ?ndice 24: 4 filas no cero, rango 0..33554432; ?ndice 25: 6 filas no cero, rango 0..268500992. Se conservan como anomal?a/cambio hist?rico posible; no se asignan a equipos nuevos.

### U09 ? radio `076351302B8E`

- Tipo hist?rico **7**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? 186250C054F5 ? 186250C054E4 ? U09. No prueba ruta operativa actual.
- Hist?rico: **27814 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 768; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
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

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

**Datos fuera del mapa esperado:** ?ndice 24: 7 filas no cero, rango 0..3406001409; ?ndice 25: 9 filas no cero, rango 0..1868829788. Se conservan como anomal?a/cambio hist?rico posible; no se asignan a equipos nuevos.

### U10 ? radio `076351302B9F`

- Tipo hist?rico **7**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? 186250C054F5 ? 186250C054E4 ? U10. No prueba ruta operativa actual.
- Hist?rico: **27688 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 864; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
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

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

**Datos fuera del mapa esperado:** ?ndice 24: 6 filas no cero, rango 0..3356367628; ?ndice 25: 8 filas no cero, rango 0..1084325316. Se conservan como anomal?a/cambio hist?rico posible; no se asignan a equipos nuevos.

### U11 ? radio `076351302B92`

- Tipo hist?rico **6**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 076351302BB3 ? U11. No prueba ruta operativa actual.
- Hist?rico: **28634 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:00:00+00:00.
- Referencia nueva Modbus TCP: base 960; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 576933 | 15184392 | 28634 / 28634 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 0 | 20517401 | 4 / 28634 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 1507047 | 1855188 | 28634 / 28634 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 38759 | 684800 | 28634 / 28634 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

**Datos fuera del mapa esperado:** ?ndice 18: 4 filas no cero, rango 0..3274991; ?ndice 19: 4 filas no cero, rango 0..375424; ?ndice 20: 4 filas no cero, rango 0..4021024; ?ndice 21: 4 filas no cero, rango 0..249901; ?ndice 22: 4 filas no cero, rango 0..3655197; ?ndice 23: 4 filas no cero, rango 0..327554. Se conservan como anomal?a/cambio hist?rico posible; no se asignan a equipos nuevos.

### U12 ? radio `076351302B9E`

- Tipo hist?rico **6**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? 186250C05529 ? U12. No prueba ruta operativa actual.
- Hist?rico: **26287 filas**, 2025-10-28T10:15:00+00:00 a 2026-08-23T15:00:00+00:00.
- Referencia nueva Modbus TCP: base 1056; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 99282 | 77430230 | 26287 / 26287 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 44345 | 1275117161 | 26287 / 26287 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 102208 | 2146469799 | 26287 / 26287 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 15741 | 2146843265 | 26287 / 26287 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

**Datos fuera del mapa esperado:** ?ndice 18: 6 filas no cero, rango 0..3100216; ?ndice 19: 6 filas no cero, rango 0..425453; ?ndice 20: 6 filas no cero, rango 0..3958156; ?ndice 21: 6 filas no cero, rango 0..397557; ?ndice 22: 6 filas no cero, rango 0..3604632; ?ndice 23: 6 filas no cero, rango 0..327477. Se conservan como anomal?a/cambio hist?rico posible; no se asignan a equipos nuevos.

### U13 ? radio `076351302B95`

- Tipo hist?rico **6**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 076351302BB3 ? U13. No prueba ruta operativa actual.
- Hist?rico: **28590 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1152; no confundir con las direcciones 53/55 del bus remoto.
- Disponible en banco, expansi?n AI/RS fotografiada. IDs configurados 2 y 3. Canal RS4 permanece cero en todo el resumen; no se deduce equipo ausente.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 521344 | 606839 | 28590 / 28590 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 421924 | 494927 | 28590 / 28590 |
| 3 | 3 | 53 / 0x0035 | 2 | 0 | 16 | 982709 | 1194708 | 28590 / 28590 |
| 4 | 3 | 55 / 0x0037 | 2 | 0 | 17 | 0 | 0 | 0 / 28590 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

### U14 ? radio `076351302BAB`

- Tipo hist?rico **6**; analizador **habilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054F8 ? 186250C054EC ? U14. No prueba ruta operativa actual.
- Hist?rico: **28515 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1248; no confundir con las direcciones 53/55 del bus remoto.

| RS | Esclavo | Direcci?n decimal / hex | Palabras | Conversi?n | ?ndice hist?rico | M?nimo | M?ximo | No cero / filas |
|---|---:|---|---:|---:|---:|---:|---:|---|
| 1 | 2 | 53 / 0x0035 | 2 | 0 | 14 | 100928 | 272143 | 28515 / 28515 |
| 2 | 2 | 55 / 0x0037 | 2 | 0 | 15 | 100959 | 272217 | 28515 / 28515 |

Dispositivo y magnitud de cada fila: **no identificados**. DI y AI no se recuperan como medidas de proceso en este perfil hist?rico.

### U15 ? radio `186352319CDA`

- Tipo hist?rico **4**; analizador **deshabilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? U15. No prueba ruta operativa actual.
- Hist?rico: **13190 filas**, 2025-10-29T00:00:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1344; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI hist?rico | ?ndice | M?nimo | M?ximo | No cero / filas | Identificaci?n del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 0 | 1476805374 | 13170 / 13190 | Pendiente |
| DI2 candidato | 3 | 0 | 1140850688 | 1 / 13190 | Pendiente |
| DI3 candidato | 4 | 0 | 1084752384 | 4 / 13190 | Pendiente |
| DI4 candidato | 5 | 0 | 137363456 | 9 / 13190 | Pendiente |

DI5?DI10: el perfil hist?rico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

**Datos fuera del mapa esperado:** ?ndice 14: 20 filas no cero, rango 0..14539733; ?ndice 15: 20 filas no cero, rango 0..19683614; ?ndice 16: 20 filas no cero, rango 0..1459953; ?ndice 17: 20 filas no cero, rango 0..662674; ?ndice 18: 4 filas no cero, rango 0..3105902; ?ndice 19: 4 filas no cero, rango 0..375222; ?ndice 20: 4 filas no cero, rango 0..3960828; ?ndice 21: 4 filas no cero, rango 0..249876; ?ndice 22: 4 filas no cero, rango 0..3606223; ?ndice 23: 4 filas no cero, rango 0..327478. Se conservan como anomal?a/cambio hist?rico posible; no se asignan a equipos nuevos.

### U16 ? radio `076351302B84`

- Tipo hist?rico **4**; analizador **deshabilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054F5 ? 186250C054FA ? 186250C051CF ? U16. No prueba ruta operativa actual.
- Hist?rico: **28144 filas**, 2025-10-29T03:45:00+00:00 a 2026-08-23T11:00:00+00:00.
- Referencia nueva Modbus TCP: base 1440; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI hist?rico | ?ndice | M?nimo | M?ximo | No cero / filas | Identificaci?n del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 143159 | 4294967295 | 28144 / 28144 | Pendiente |
| DI2 candidato | 3 | 0 | 4294967295 | 2 / 28144 | Pendiente |
| DI3 candidato | 4 | 0 | 4294967295 | 2 / 28144 | Pendiente |
| DI4 candidato | 5 | 0 | 4294967295 | 8 / 28144 | Pendiente |

DI5?DI10: el perfil hist?rico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U17 ? radio `076351302BC7`

- Tipo hist?rico **4**; analizador **deshabilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? 186250C054F5 ? 186250C054FA ? U17. No prueba ruta operativa actual.
- Hist?rico: **28045 filas**, 2025-10-29T10:15:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1536; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI hist?rico | ?ndice | M?nimo | M?ximo | No cero / filas | Identificaci?n del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 17501 | 3222062369 | 28045 / 28045 | Pendiente |
| DI2 candidato | 3 | 0 | 2684363264 | 10 / 28045 | Pendiente |
| DI3 candidato | 4 | 0 | 1074003968 | 4 / 28045 | Pendiente |
| DI4 candidato | 5 | 0 | 1342181632 | 12 / 28045 | Pendiente |

DI5?DI10: el perfil hist?rico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U18 ? radio `076351302B7C`

- Tipo hist?rico **4**; analizador **deshabilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? U18. No prueba ruta operativa actual.
- Hist?rico: **28635 filas**, 2025-10-29T10:30:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1632; no confundir con las direcciones 53/55 del bus remoto.
- Campo DI1 hist?rico constante en 1463472; causa desconocida.

| Campo DI hist?rico | ?ndice | M?nimo | M?ximo | No cero / filas | Identificaci?n del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 1463472 | 1463472 | 28635 / 28635 | Pendiente |
| DI2 candidato | 3 | 0 | 0 | 0 / 28635 | Pendiente |
| DI3 candidato | 4 | 0 | 0 | 0 / 28635 | Pendiente |
| DI4 candidato | 5 | 0 | 0 | 0 / 28635 | Pendiente |

DI5?DI10: el perfil hist?rico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U19 ? radio `076351302BC2`

- Tipo hist?rico **4**; analizador **deshabilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 076351302BB3 ? U19. No prueba ruta operativa actual.
- Hist?rico: **28628 filas**, 2025-10-29T10:30:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1728; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI hist?rico | ?ndice | M?nimo | M?ximo | No cero / filas | Identificaci?n del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 2073137 | 2312953 | 28628 / 28628 | Pendiente |
| DI2 candidato | 3 | 0 | 0 | 0 / 28628 | Pendiente |
| DI3 candidato | 4 | 0 | 0 | 0 / 28628 | Pendiente |
| DI4 candidato | 5 | 0 | 0 | 0 / 28628 | Pendiente |

DI5?DI10: el perfil hist?rico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U20 ? radio `18634E30A2CB`

- Tipo hist?rico **4**; analizador **deshabilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 076351302BB3 ? 076351302BC2 ? U20. No prueba ruta operativa actual.
- Hist?rico: **28633 filas**, 2025-10-29T10:30:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1824; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI hist?rico | ?ndice | M?nimo | M?ximo | No cero / filas | Identificaci?n del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 237219 | 267478 | 28633 / 28633 | Pendiente |
| DI2 candidato | 3 | 0 | 0 | 0 / 28633 | Pendiente |
| DI3 candidato | 4 | 0 | 0 | 0 / 28633 | Pendiente |
| DI4 candidato | 5 | 0 | 0 | 0 / 28633 | Pendiente |

DI5?DI10: el perfil hist?rico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U21 ? radio `076351302B99`

- Tipo hist?rico **4**; analizador **deshabilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054F8 ? 186250C054EC ? U21. No prueba ruta operativa actual.
- Hist?rico: **28645 filas**, 2025-10-29T08:15:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 1920; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI hist?rico | ?ndice | M?nimo | M?ximo | No cero / filas | Identificaci?n del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 102190 | 33850926 | 28645 / 28645 | Pendiente |
| DI2 candidato | 3 | 0 | 0 | 0 / 28645 | Pendiente |
| DI3 candidato | 4 | 0 | 0 | 0 / 28645 | Pendiente |
| DI4 candidato | 5 | 0 | 0 | 0 / 28645 | Pendiente |

DI5?DI10: el perfil hist?rico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U22 ? radio `076351302B9A`

- Tipo hist?rico **4**; analizador **deshabilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? 186250C05529 ? U22. No prueba ruta operativa actual.
- Hist?rico: **25862 filas**, 2025-10-28T15:15:00+00:00 a 2026-08-23T11:15:00+00:00.
- Referencia nueva Modbus TCP: base 2016; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI hist?rico | ?ndice | M?nimo | M?ximo | No cero / filas | Identificaci?n del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 144117 | 3225540590 | 25862 / 25862 | Pendiente |
| DI2 candidato | 3 | 0 | 2281701376 | 5 / 25862 | Pendiente |
| DI3 candidato | 4 | 0 | 318767104 | 1 / 25862 | Pendiente |
| DI4 candidato | 5 | 0 | 2147649536 | 6 / 25862 | Pendiente |

DI5?DI10: el perfil hist?rico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U23 ? radio `076351302B85`

- Tipo hist?rico **4**; analizador **deshabilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 186250C054E8 ? 186250C054F5 ? U23. No prueba ruta operativa actual.
- Hist?rico: **27908 filas**, 2025-10-29T10:30:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 2112; no confundir con las direcciones 53/55 del bus remoto.

| Campo DI hist?rico | ?ndice | M?nimo | M?ximo | No cero / filas | Identificaci?n del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 309 | 1749090613 | 27908 / 27908 | Pendiente |
| DI2 candidato | 3 | 0 | 2147649536 | 8 / 27908 | Pendiente |
| DI3 candidato | 4 | 0 | 8389256 | 2 / 27908 | Pendiente |
| DI4 candidato | 5 | 0 | 402787395 | 4 / 27908 | Pendiente |

DI5?DI10: el perfil hist?rico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### U24 ? radio `076351302B9C`

- Tipo hist?rico **4**; analizador **deshabilitado**; direcci?n radio distinta del ID Modbus local.
- Ruta configurada: base ? 076351302BB3 ? U24. No prueba ruta operativa actual.
- Hist?rico: **28569 filas**, 2025-10-29T10:30:00+00:00 a 2026-08-23T17:15:00+00:00.
- Referencia nueva Modbus TCP: base 2208; no confundir con las direcciones 53/55 del bus remoto.
- Disponible en banco; DI1/DI2 ensayadas. DI2 hist?rico cero no contradice el ensayo posterior de cinco pulsos.

| Campo DI hist?rico | ?ndice | M?nimo | M?ximo | No cero / filas | Identificaci?n del equipo |
|---|---:|---:|---:|---|---|
| DI1 candidato | 2 | 61016 | 65075 | 28569 / 28569 | Pendiente |
| DI2 candidato | 3 | 0 | 0 | 0 / 28569 | Pendiente |
| DI3 candidato | 4 | 0 | 0 | 0 / 28569 | Pendiente |
| DI4 candidato | 5 | 0 | 0 | 0 / 28569 | Pendiente |

DI5?DI10: el perfil hist?rico no las documenta. No hay mapa RS habilitado; no significa que la remota completa estuviera deshabilitada.

### 7.25 ?ltima muestra conservada de las dos remotas disponibles

Consulta directa a SQLite en modo de solo lectura. En ambos casos el ?ltimo timestamp tiene una sola versi?n en la base.

| Remota | ?ltima fecha UTC | Campos observados | Interpretaci?n permitida |
|---|---|---|---|
| U13 | 2026-08-23 17:15:00 | RS1=606839; RS2=494927; RS3=1194708; RS4=0 | Asociados respectivamente a ID2/53, ID2/55, ID3/53, ID3/55 seg?n mapa; unidades desconocidas |
| U24 | 2026-08-23 17:15:00 | ?ndices DI hist?ricos 2..5: 65075, 0, 0, 0 | El primer campo corresponde al acumulador candidato DI1; ning?n equipo f?sico identificado |

La lectura de banco posterior de U24 lleg? a DI1=62838 y DI2=5. El valor DI1 es inferior al ?ltimo hist?rico: **no empalmar ambas series como un contador continuo** sin explicar el cambio (reset, reconfiguraci?n u otra causa no determinada). El reloj de la respuesta de banco tampoco se considera fiable. No se calcula consumo a partir de esa diferencia.

## 8. Informaci?n que falta y d?nde recuperarla

El manual ViewGest explica que nombre, descripci?n, tipo de magnitud, comentarios, factor multiplicativo y escalado bruto/f?sico se configuran en la **variable del servidor**, ligada a una concentradora, ID MicroRTU e ?ndice. Referencias: p?ginas impresas 38?40 (PDF 39?41), secciones 3.1.2.3.2 y 3.1.2.3.2.1. Sus ejemplos de energ?a activa, gas, agua y presi?n son posibilidades del producto, no una lista de equipos de ForumMadeira.

La copia BeagleBone no incluye la base SQL Server de ViewGest ni una exportaci?n de esa indexaci?n. Ese es el candidato principal para recuperar etiquetas y factores, antes de intentar adivinarlos por series num?ricas.

| Prioridad | Evidencia a conseguir | Datos que resolver?a |
|---|---|---|
| 1 | Exportaci?n autorizada de variables e indexaci?n del sitio ViewGest | Uxx/canal ? nombre, ubicaci?n, magnitud, factor y escala |
| 1 | Fotos de placas de caracter?sticas de analizadores y sus pantallas de comunicaci?n | Modelo, ID, baudrate, paridad, mapa de registros |
| 1 | Esquema/as-built o listado de puntos de puesta en marcha | Canal ? cable ? equipo; referencias de DI y AI |
| 2 | Etiquetas y recorrido de cables del armario original | Asociaci?n f?sica y bus local de cada ID |
| 2 | Manual/esquema de STM-X3-2AI-RS485-1 y firmware instalado | Par?metros fijos/configurables, funci?n Modbus, escala AI y calidad RS |
| 2 | Fichas de transmisores AI1/AI2 | 4?20 mA o 0?10 V, rango, unidades, alimentaci?n |
| 2 | Lectura A2 de U13 sin cambios de configuraci?n | Valores brutos actuales; contraste contra aparato conocido |
| 3 | Ensayo controlado de cada DI y AI identificada | Correspondencia de canal, factor y comportamiento |

No hay que reiniciar Java para esta investigaci?n: su inicializaci?n puede escribir configuraci?n. No enviar A9, cambiar jumpers, aplicar tensi?n a DI ni ajustar analizadores solo para descubrir qu? hab?a instalado. La b?squeda realizada fue local, sin SSH ni modificaciones de campo.

### Ficha que se debe completar por dispositivo

| Campo | Valor a registrar |
|---|---|
| Remota / ID radio / canal / bornero | Identificador inequ?voco |
| Tag de instalaci?n / ubicaci?n / servicio | Del plano o etiqueta, no inferido |
| Fabricante / modelo / n?mero de serie | Foto y referencia |
| Se?al DI | Contacto/pulso, factor impulsos/unidad, anchura y frecuencia documentadas |
| Se?al RS485 | ID, baudrate, paridad, bits/parada, funci?n, direcci?n y base, cantidad, formato, orden, escala |
| Se?al AI | Corriente/tensi?n, selector, rango bruto, rango f?sico, unidad y esquema del lazo |
| Evidencia | Archivo/foto/p?gina/fecha de lectura |
| Estado | Configurado / observado / validado f?sicamente / pendiente |

## 9. Registro de hallazgos y mantenimiento

| Fecha | Hallazgo | Consecuencia |
|---|---|---|
| 2026-09-23 | Fotos F7/F8 identifican STM-X3-2AI-RS485-1 y selecci?n 4?20 mA | La capacidad anal?gica de U13 deja de ser una suposici?n |
| 2026-09-23 | Inscripci?n MODBUS RTU en expansi?n U13 | Confirma familia de protocolo de esa placa, no funci?n/baudrate |
| 2026-09-23 | Las 100 entradas del mapa usan 53/55, longitud2, tipo0 | Inventario completo incluido por unidad |
| 2026-09-23 | U13 RS4 hist?rico siempre cero; U24 DI2 antiguo cero pero cambia en banco | No convertir cero en ausencia f?sica |
| 2026-09-23 | Posiciones AI hist?ricas rellenadas por perfiles | No deducir ausencia de sensores 4?20 mA |
| 2026-09-23 | ViewGest alberga nombre/indexaci?n/escalado a nivel servidor | Priorizar recuperar esa configuraci?n autorizadamente |

Actualizar este archivo a?adiendo fuente y fecha para cada identificaci?n nueva. No reemplazar silenciosamente el mapa hist?rico por el de banco. Mantener los valores brutos originales y distinguir los registros del bus RS485 de los publicados por el nuevo servidor TCP.

Relacionados: [inventario de tarjetas](INVENTARIO_TARJETAS.md), [adquisici?n y mapa TCP](ADQUISICION.md), [?ndice general](INDICE.md).

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

### Fotograf?as originales enlazadas

Se conservan localmente y siguen ignoradas por Git. Los enlaces no publican ni copian las im?genes.

- [F1 ? WhatsApp Image 2026-09-21 at 13.54.47 (1).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.47%20%281%29.jpeg)
- [F2 ? WhatsApp Image 2026-09-21 at 13.54.47 (2).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.47%20%282%29.jpeg)
- [F3 ? WhatsApp Image 2026-09-21 at 13.54.47 (3).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.47%20%283%29.jpeg)
- [F4 ? WhatsApp Image 2026-09-21 at 13.54.47.jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.47.jpeg)
- [F5 ? WhatsApp Image 2026-09-21 at 13.54.48 (1).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.48%20%281%29.jpeg)
- [F6 ? WhatsApp Image 2026-09-21 at 13.54.48 (2).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.48%20%282%29.jpeg)
- [F7 ? WhatsApp Image 2026-09-21 at 13.54.48 (3).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.48%20%283%29.jpeg)
- [F8 ? WhatsApp Image 2026-09-21 at 13.54.48 (4).jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.48%20%284%29.jpeg)
- [F9 ? WhatsApp Image 2026-09-21 at 13.54.48.jpeg](private/IMAGENES%20PLACAS/WhatsApp%20Image%202026-09-21%20at%2013.54.48.jpeg)
