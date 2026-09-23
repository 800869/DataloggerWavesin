# Reorganización del repositorio

## Estado inicial y criterio

Inventario previo: 131.800 archivos, 1.844.711.382 bytes, sin contar `.git`.
Git tenía 54.918 entradas en el índice. El commit inicial solo contenía
`.gitattributes`, `LICENSE` y `README.md`.

Se clasificó todo el árbol y se buscaron referencias textuales a las rutas y
nombres usados por el código antes de moverlos. Se conservaron hashes SHA-256,
inventario, referencias y una copia del índice original en una auditoría local.
No se eliminan históricos ni se ejecuta el software Java recuperado.

## Mapa de traslados

Las rutas de origen de esta tabla parten de `BEAGLEBONE/`.

| Origen | Destino desde la raíz del proyecto |
| --- | --- |
| `analisis/visor_historicos.py`, `analisis/visor.html` | `src/dataloggerwavesin/` |
| `analizar_copia.py`, `analizar_historicos.py` | `scripts/` |
| `inspeccionar_java.py` | `tools/` |
| `analisis/Abrir_visor.cmd` | `scripts/Abrir_visor.cmd` |
| `beaglebone_programacion_01.tar` | `data/raw/` |
| `analisis/extraido/` | `data/raw/extraido/` |
| `Archivos sacados de beaglebone mediante SD/` | `data/raw/Archivos sacados de beaglebone mediante SD/` |
| `analisis/historicos.sqlite` | `data/database/historicos.sqlite` |
| `analisis/*.json`, `analisis/*.jsonl` | `data/processed/` |
| `inventario_tar.txt` | `data/processed/inventario_tar.txt` |
| `analisis/java_estatico/` | `data/processed/java_estatico/` |
| `analisis/logs/` | `logs/` |
| `analisis/INFORME_BEAGLEBONE.md` | `docs/private/INFORME_BEAGLEBONE.md` |
| Conversación, manual PDF y `IMAGENES PLACAS/` | `docs/private/`, conservando nombres |

Los antiguos puntos de entrada Python y CMD permanecen como pequeños
lanzadores. No duplican la lógica: ejecutan los archivos nuevos. Las cachés
originales permanecen ignoradas en sus ubicaciones.

## Cambios que afectan a rutas

- Las rutas locales se resuelven en `src/dataloggerwavesin/paths.py`.
- Las utilidades crean los directorios de salida necesarios en la nueva estructura.
- El lanzador Windows usa `DATALOGGER_PYTHON`, `.venv`, `py -3`, `python` o,
  como compatibilidad final, el runtime local ya existente de Codex.
- Los consumidores externos que abran directamente el antiguo SQLite, HTML o
  JSON deberán usar las rutas de esta tabla. No se crean enlaces simbólicos.
- No se modifican el esquema SQLite, consultas, reducción de puntos del gráfico,
  puerto HTTP, interfaz HTML ni datos de configuración del programa de campo.

Los archivos originales que requirieron edición se conservan también en
`data/private/reorganization/originals/`. Los inventarios y el mapa exacto de
movimientos están en `data/private/reorganization/`, ignorados por Git.

## Verificación

Las pruebas reproducibles se ejecutan con:

```sh
python -m unittest discover -s tests -v
python tools/verify_repository.py
```

La auditoría privada recoge la comparación del visor antes/después, la
conservación de archivos y la revisión de Git. No se reejecutan los análisis
sobre el histórico original: las pruebas de esas utilidades emplean entradas
sintéticas en directorios temporales.

### Resultados de la comprobación local

Entorno: Windows, Python 3.12.14. Comprobación realizada el 23/09/2026.

| Comprobación | Resultado |
| --- | --- |
| Conservación de los 131.800 archivos originales | Sin archivos perdidos ni diferencias en las huellas verificadas |
| SQLite, TAR, históricos, configuración y documentos privados | Contenido conservado byte a byte |
| Archivos editados | Originales guardados en la auditoría privada |
| Imports y sintaxis Python | Correctos en los archivos versionables |
| Pruebas aisladas | Cuatro pruebas: análisis, consulta, Java, compatibilidad y rutas |
| Visor antes/después | Cinco respuestas HTTP idénticas por SHA-256, incluido el HTML |
| Datos visibles | 24 unidades y 656.242 registros |
| Arranque desde otra carpeta | Correcto con ambos lanzadores Python y ambos CMD |
| Referencias ejecutables antiguas y enlaces Markdown locales | Sin referencias rotas detectadas |
| Índice y archivos versionables | 26 archivos; sin datos runtime ni secretos detectados por el escáner |
| Exclusiones de Git | 14 casos comprobados, incluidos SQLite WAL/SHM, `.env` y copias privadas |
| Revisión de whitespace de Git | Sin errores |

La copia del `.gitignore` anterior se obtuvo del índice original y conserva los
finales de línea normalizados por Git. Los demás originales editados se guardaron
desde los archivos de trabajo antes de modificarlos.

Los cambios quedan preparados en el índice, sin crear commits ni publicar en
GitHub. El verificador de secretos es heurístico. La comprobación local no
equivale a una prueba de adquisición en la BeagleBone: no se actuó sobre la placa.
