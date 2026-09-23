"""Lanzador de compatibilidad; implementacion en scripts/analizar_copia.py."""
import runpy
from pathlib import Path

globals().update(runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/analizar_copia.py"), run_name=__name__))
