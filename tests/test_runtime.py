"""Pruebas aisladas: nunca necesitan datos privados ni conectan a la placa."""
import importlib
from contextlib import closing
import gc
import io
import json
import os
from pathlib import Path
import sqlite3
import struct
import subprocess
import sys
import tarfile
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
UID = "000000000001"


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.data = self.base / "data"
        self.env = {
            "DATALOGGER_DATA_DIR": str(self.data),
            "DATALOGGER_LOG_DIR": str(self.base / "logs"),
            "DATALOGGER_DATABASE": "",
            "DATALOGGER_ARCHIVE": "",
            "DATALOGGER_UNITS": "",
        }
        self.environment = patch.dict(os.environ, self.env)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        import dataloggerwavesin.paths as paths
        self.paths = importlib.reload(paths)

    def make_archive(self):
        self.paths.RAW_DIR.mkdir(parents=True)
        files = {
            "home/actemium/apps/xthreeconpi/config/units.txt":
                ";".join([UID, "U04", "", "0", "", "", "", "false", ""]).encode(),
            "home/actemium/apps/xthreeconpi/ftpOut/sample.txt": json.dumps({
                "id": UID,
                "energyLogs": [
                    {"dateTime": 1704067200, "values": [1] * 32},
                    {"dateTime": 1704070800, "values": [3] * 32},
                ],
            }).encode(),
            "home/actemium/apps/xthreeconpi/log/sample.log": b"INFO: sample\n",
        }
        with tarfile.open(self.paths.ARCHIVE_FILE, "w") as archive:
            for name, content in files.items():
                info = tarfile.TarInfo(name)
                info.size = len(content)
                archive.addfile(info, io.BytesIO(content))

    def run_script(self, relative):
        result = subprocess.run(
            [sys.executable, str(ROOT / relative)], cwd=self.base,
            env=os.environ.copy(), capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_analysis_and_readonly_viewer_from_other_directory(self):
        self.make_archive()
        self.run_script("scripts/analizar_copia.py")
        self.run_script("scripts/analizar_historicos.py")
        self.assertTrue(self.paths.UNITS_FILE.is_file())
        self.assertTrue((self.paths.LOG_DIR / "sample.log").is_file())
        self.assertTrue((self.paths.PROCESSED_DIR / "inventario.jsonl").is_file())
        module_name = "dataloggerwavesin.visor_historicos"
        if module_name in sys.modules:
            viewer = importlib.reload(sys.modules[module_name])
        else:
            viewer = importlib.import_module(module_name)
        server = viewer.ThreadingHTTPServer(("127.0.0.1", 0), viewer.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(gc.collect)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)

        def get(path):
            try:
                response = urllib.request.urlopen(
                    f"http://127.0.0.1:{server.server_port}{path}", timeout=10
                )
            except urllib.error.HTTPError as error:
                response = error
            with response:
                return response.status, response.read()

        status, html = get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"/api/unidades", html)
        status, body = get("/api/unidades")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["total"], 2)
        status, body = get(f"/api/serie?unidad={UID}&canal=14")
        self.assertEqual(status, 200)
        series = json.loads(body)
        self.assertEqual((series["total"], series["min"], series["max"]), (2, 1, 3))
        status, body = get(f"/api/serie?unidad={UID}&canal=14&desde=2025-01-01")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["total"], 0)
        self.assertEqual(get(f"/api/serie?unidad={UID}&canal=99")[0], 400)
        self.assertEqual(get("/api/serie?unidad=INVALID")[0], 400)
        self.assertEqual(get("/extraido/etc/shadow")[0], 404)
        with closing(viewer.db()) as connection:
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("DELETE FROM lecturas")

    def test_java_inspector_uses_relocated_input_and_output(self):
        jar = self.paths.EXTRACTED_DIR / "home/actemium/apps/xthreeconpi/xthreeconpi.jar"
        jar.parent.mkdir(parents=True)
        bytecode = struct.pack(">IHHH", 0xCAFEBABE, 0, 52, 3)
        bytecode += b"\x01\x00\x04Demo\x07\x00\x01"
        bytecode += struct.pack(">HHHHHHH", 0x21, 2, 0, 0, 0, 0, 0)
        with zipfile.ZipFile(jar, "w") as archive:
            archive.writestr("Demo.class", bytecode)
        self.run_script("tools/inspeccionar_java.py")
        self.assertIn("CLASS Demo", (self.paths.JAVA_DIR / "Demo.txt").read_text())
        self.assertEqual(json.loads((self.paths.JAVA_DIR / "Demo.strings.json").read_text()), ["Demo"])
        self.run_script("BEAGLEBONE/inspeccionar_java.py")
        self.assertEqual(json.loads((self.paths.JAVA_DIR / "Demo.strings.json").read_text()), ["Demo"])

    def test_legacy_analysis_launchers(self):
        self.make_archive()
        self.run_script("BEAGLEBONE/analizar_copia.py")
        self.run_script("BEAGLEBONE/analizar_historicos.py")
        self.assertTrue(self.paths.DATABASE_FILE.is_file())

    def test_relative_environment_path_is_project_relative(self):
        with patch.dict(os.environ, {"DATALOGGER_TEST_PATH": "data/example"}):
            self.assertEqual(
                self.paths.configured_path("DATALOGGER_TEST_PATH", "."),
                ROOT / "data/example",
            )


if __name__ == "__main__":
    unittest.main()
