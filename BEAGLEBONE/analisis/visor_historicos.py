"""Lanzador de compatibilidad del visor local."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
globals().update(runpy.run_module("dataloggerwavesin.visor_historicos", run_name=__name__))
