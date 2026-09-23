"""Inicia el visor desde cualquier directorio, sin instalar el paquete."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

if __name__ == "__main__":
    runpy.run_module("dataloggerwavesin.visor_historicos", run_name="__main__")
