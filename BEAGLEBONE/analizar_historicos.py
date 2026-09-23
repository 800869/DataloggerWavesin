"""Lanzador de compatibilidad; implementacion en scripts/analizar_historicos.py."""
import runpy
from pathlib import Path

globals().update(runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/analizar_historicos.py"), run_name=__name__))
