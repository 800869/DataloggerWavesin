@echo off
setlocal
echo Adquisicion PC: consulte la configuracion elegida
echo Mantenga esta ventana abierta. Ctrl+C cierra la adquisicion.
if defined DATALOGGER_PYTHON (
    "%DATALOGGER_PYTHON%" "%~dp0adquisicion.py" %*
    exit /b
)
if exist "%~dp0..\.venv\Scripts\python.exe" (
    "%~dp0..\.venv\Scripts\python.exe" "%~dp0adquisicion.py" %*
    exit /b
)
where py >nul 2>nul
if not errorlevel 1 (
    py -3 "%~dp0adquisicion.py" %*
    exit /b
)
python -c "import sys; assert sys.version_info >= (3, 10)" >nul 2>nul
if not errorlevel 1 (
    python "%~dp0adquisicion.py" %*
    exit /b
)
rem Compatibilidad con el entorno local anterior, sin nombre de usuario fijo.
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "%~dp0adquisicion.py" %*
    exit /b
)
echo No se encuentra Python. Instale Python 3.10+ o defina DATALOGGER_PYTHON.
exit /b 1

