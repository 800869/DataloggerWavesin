@echo off
setlocal
echo Visor local: http://127.0.0.1:8765/
echo Mantenga esta ventana abierta. Ctrl+C cierra el visor.
if defined DATALOGGER_PYTHON (
    "%DATALOGGER_PYTHON%" "%~dp0visor_historicos.py"
    exit /b
)
if exist "%~dp0..\.venv\Scripts\python.exe" (
    "%~dp0..\.venv\Scripts\python.exe" "%~dp0visor_historicos.py"
    exit /b
)
where py >nul 2>nul
if not errorlevel 1 (
    py -3 "%~dp0visor_historicos.py"
    exit /b
)
python -c "import sys; assert sys.version_info >= (3, 10)" >nul 2>nul
if not errorlevel 1 (
    python "%~dp0visor_historicos.py"
    exit /b
)
rem Compatibilidad con el entorno local anterior, sin nombre de usuario fijo.
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "%~dp0visor_historicos.py"
    exit /b
)
echo No se encuentra Python. Instale Python 3.10+ o defina DATALOGGER_PYTHON.
exit /b 1
