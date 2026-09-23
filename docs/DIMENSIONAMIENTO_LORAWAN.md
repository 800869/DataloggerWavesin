# Dimensionamiento preliminar para sustituir las remotas por LoRaWAN

Fecha: 23/09/2026. Alcance: cantidades recuperadas de la configuración antigua y del análisis histórico. No constituye una selección de equipos ni un presupuesto cerrado.

## 1. Criterio de dimensionamiento

La parte RS485 puede dimensionarse a partir del mapa configurado. El número de DI y analógicas realmente utilizadas sigue parcialmente abierto.

Un **valor RS485 no es una entrada física**: un mismo puerto puede consultar varios esclavos y obtener varios valores de cada uno. Los IDs Modbus son locales a cada bus, distintos de las direcciones de radio y de las direcciones del nuevo servidor Modbus TCP.

Las fotografías corresponden a dos tarjetas retiradas de la instalación para pruebas. Se utilizan para identificar capacidad física; sus bornes sin cables no aportan información sobre las conexiones originales.

## 2. Puntos recuperados por remota

| Remota | IDs Modbus configurados | Valores RS485 de 32 bits | DI según histórico original | Analógicas utilizadas |
|---|---|---:|---|---|
| U01 | 2, 3, 4, 5, 6 | 10 | No determinable [1] | No determinable [2] |
| U02 | 2, 3, 4, 5 | 8 | No determinable [1] | No determinable [2] |
| U03 | 2, 3, 4, 5, 6 | 10 | No determinable [1] | No determinable [2] |
| U04 | 2, 3, 4, 5 | 8 | No determinable [1] | No determinable [2] |
| U05 | 2 | 2 | No determinable [1] | No determinable [2] |
| U06 | 2, 3, 4, 5 | 8 | No determinable [1] | No determinable [2] |
| U07 | 2, 3, 4, 5, 6 | 10 | No determinable [1] | No determinable [2] |
| U08 | 2, 3, 4, 5, 6 | 10 | No determinable [1] | No determinable [2] |
| U09 | 2, 3, 4, 5, 6 | 10 | No determinable [1] | No determinable [2] |
| U10 | 2, 3, 4, 5, 6 | 10 | No determinable [1] | No determinable [2] |
| U11 | 2, 3 | 4 | No determinable [1] | No determinable [2] |
| U12 | 2, 3 | 4 | No determinable [1] | No determinable [2] |
| U13 | 2, 3 | 4 | No determinable [1] | 2 AI disponibles; uso desconocido |
| U14 | 2 | 2 | No determinable [1] | No determinable [2] |
| U15 | Analizador deshabilitado | 0 configurados | DI1 con actividad; DI2–4 dudosas [3] | No determinable [2] |
| U16 | Analizador deshabilitado | 0 configurados | DI1 con actividad; DI2–4 dudosas [3] | No determinable [2] |
| U17 | Analizador deshabilitado | 0 configurados | DI1 con actividad; DI2–4 dudosas [3] | No determinable [2] |
| U18 | Analizador deshabilitado | 0 configurados | DI1 con valor constante | No determinable [2] |
| U19 | Analizador deshabilitado | 0 configurados | DI1 acumulando | No determinable [2] |
| U20 | Analizador deshabilitado | 0 configurados | DI1 acumulando | No determinable [2] |
| U21 | Analizador deshabilitado | 0 configurados | DI1 casi constante, con anomalía | No determinable [2] |
| U22 | Analizador deshabilitado | 0 configurados | DI1 con actividad; DI2–4 dudosas [3] | No determinable [2] |
| U23 | Analizador deshabilitado | 0 configurados | DI1 casi constante; DI2–4 dudosas [3] | No determinable [2] |
| U24 | Analizador deshabilitado | 0 configurados | DI1 acumulando [4] | No determinable [2] |

**Notas de interpretación:**

1. Los perfiles históricos de U01–U14 rellenaban las posiciones DI con ceros. No permiten contar las DI conectadas.
2. Los perfiles recuperados tampoco conservaban medidas analógicas en esos campos. No se puede presupuestar cero entradas 4–20 mA basándose en ellos.
3. Hay apariciones puntuales de valores con subidas y bajadas. No acreditan todavía contadores adicionales. DI5–DI10 quedan fuera del perfil histórico tipo 4.
4. DI2 de U24 funciona en el banco; eso no demuestra que tuviera un contador conectado en la instalación.

«Analizador deshabilitado» describe el mapa recuperado, no una remota completa deshabilitada ni una ausencia física garantizada de expansión. DI1 fuera de U24 se interpreta como primer campo candidato a contador DI, pendiente de contraste físico.

## 3. Totales RS485 y distribución

| Concepto | Cantidad recuperada |
|---|---:|
| Remotas con analizador habilitado | 14 |
| Asociaciones remota/esclavo | 50 |
| Valores configurados de 32 bits | 100 |
| Palabras Modbus de 16 bits correspondientes | 200 |

Las 50 asociaciones no prueban 50 aparatos físicos únicos ni su presencia actual.

| Tamaño de lectura por remota | Remotas | Cantidad de remotas | Total de valores |
|---|---|---:|---:|
| 5 esclavos / 10 valores | U01, U03, U07, U08, U09, U10 | 6 | 60 |
| 4 esclavos / 8 valores | U02, U04, U06 | 3 | 24 |
| 2 esclavos / 4 valores | U11, U12, U13 | 3 | 12 |
| 1 esclavo / 2 valores | U05, U14 | 2 | 4 |
| **Total** | | **14** | **100** |

Por cada esclavo se configuran dos valores:

| Dirección inicial decimal | Hexadecimal | Cantidad | Conversión antigua |
|---|---|---:|---|
| 53 | 0x0035 | 2 registros | Tipo 0 del Java |
| 55 | 0x0037 | 2 registros | Tipo 0 del Java |

El tipo 0 tiene un tratamiento particular del bit31; no debe equipararse sin comprobación a un int32/uint32 estándar del analizador. Faltan modelo, función 03/04, velocidad, paridad, escala y correspondencia con la numeración del manual del aparato.

Ejemplo: sustituir U01 requiere capacidad para consultar cinco esclavos y diez valores por un bus RS485, no diez puertos RS485. La compatibilidad eléctrica y los parámetros reales del bus siguen pendientes de verificar.

## 4. Capacidad física comprobada frente a uso

| Tarjeta de banco | Capacidad identificada | Uso original recuperable |
|---|---|---|
| U13 | 10 DI + expansión de 2 AI seleccionables 0–10 V / 4–20 mA + RS485 | 4 valores RS de dos esclavos; DI/AI utilizadas sin determinar |
| U24 | 10 DI, sin expansión montada en las fotos | Primer contador DI con acumulación histórica; resto sin identificación suficiente |

No extrapolar esa configuración física a las otras 22 remotas. Tampoco convertir los cuatro campos DI del perfil histórico en cuatro entradas utilizadas. No hay todavía un total confirmado de puntos DI o AI instalados.

## 5. Familias de sustitución a estudiar

| Familia | Necesidad recuperada | Pendiente antes de seleccionar |
|---|---|---|
| U01–U14 | Adquisición Modbus RS485 de 1–5 esclavos y 2–10 valores por ubicación | Parámetros del bus, formatos/escalas, alimentación y DI/AI adicionales |
| U15–U24 | Adquisición de contadores de impulsos; investigar DI1 en cada ubicación | Número real de canales, servicio agua/luz/gas, factor y características del pulso |
| AI donde se confirme uso | Adquisición 4–20 mA o 0–10 V según sensor y configuración | Cantidad, rango, alimentación del lazo, precisión y escala |

Para comparar alternativas LoRaWAN, exigir y verificar contaje continuo de impulsos entre transmisiones, conservación del acumulado ante reinicios, capacidad de lectura multi-esclavo donde corresponda, estado/antigüedad de medidas y recuperación tras cortes. El objetivo de transmitir cada diez minutos no implica contar pulsos solo cada diez minutos.

Esto es una lista de requisitos, no una afirmación de que cualquier equipo LoRaWAN los cumpla. También quedan por dimensionar cobertura, gateway, servidor de red, alimentación y conexión con el servidor Modbus TCP del PC.

## 6. Qué falta para cerrar cantidades y compra

- Recuperar la indexación de variables de ViewGest: remota/canal, nombre, magnitud y factor.
- Contrastar planos/listado de puntos y cableado original para DI y AI.
- Identificar los analizadores y sus parámetros de comunicación.
- Resolver canales constantes, anomalías y posibles señales adicionales antes de descartarlos.
- Mantener separadas las cantidades verificadas, las reservas de capacidad y las hipótesis.

**Conclusión de dimensionamiento:** 14 mapas RS485 bien delimitados; diez ubicaciones restantes orientadas por el histórico al contaje de impulsos. Cantidades definitivas de DI y AI pendientes. No cerrar una compra tomando «no determinable» como cero.

## 7. Fuentes

- Configuración original: `data/raw/extraido/home/actemium/apps/xthreeconpi/config/units.txt`.
- Resumen histórico: `data/processed/resumen_historicos.json`.
- Análisis temporal: `data/processed/tendencias_dispositivos.json`, excluyendo fechas con versiones contradictorias.
- [Recopilación detallada de dispositivos y señales](DISPOSITIVOS_Y_SENALES.md).
- [Inventario de tarjetas](INVENTARIO_TARJETAS.md).
- [Índice general](INDICE.md).

Documento local de análisis. No implica cambios en la BeagleBone, firmware, configuración de remotas ni históricos.
