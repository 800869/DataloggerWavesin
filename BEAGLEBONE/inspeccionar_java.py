"""Lanzador de compatibilidad; implementacion en tools/inspeccionar_java.py."""
import runpy
from pathlib import Path

globals().update(runpy.run_path(str(Path(__file__).resolve().parents[1] / "tools/inspeccionar_java.py"), run_name=__name__))
