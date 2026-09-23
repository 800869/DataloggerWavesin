"""Rutas locales, independientes del directorio desde el que se ejecute Python.

Las variables de entorno son opcionales. Las rutas relativas se resuelven desde
la raíz del proyecto. Este módulo no crea archivos ni lee credenciales.
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def configured_path(name, default):
    value = os.environ.get(name)
    path = Path(value).expanduser() if value else Path(default)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


DATA_DIR = configured_path("DATALOGGER_DATA_DIR", PROJECT_ROOT / "data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXTRACTED_DIR = RAW_DIR / "extraido"
DATABASE_FILE = configured_path(
    "DATALOGGER_DATABASE", DATA_DIR / "database" / "historicos.sqlite"
)
ARCHIVE_FILE = configured_path(
    "DATALOGGER_ARCHIVE", RAW_DIR / "beaglebone_programacion_01.tar"
)
UNITS_FILE = configured_path(
    "DATALOGGER_UNITS",
    EXTRACTED_DIR / "home/actemium/apps/xthreeconpi/config/units.txt",
)
LOG_DIR = configured_path("DATALOGGER_LOG_DIR", PROJECT_ROOT / "logs")
SUMMARY_FILE = PROCESSED_DIR / "resumen_historicos.json"
JAVA_DIR = PROCESSED_DIR / "java_estatico"
HTML_FILE = Path(__file__).resolve().parent / "visor.html"
