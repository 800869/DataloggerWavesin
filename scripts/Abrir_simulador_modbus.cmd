@echo off
setlocal
echo SIMULACION Modbus TCP local: 127.0.0.1:1502
echo Mantenga esta ventana abierta. Ctrl+C cierra el simulador.
if defined DATALOGGER_PYTHON (
    "%DATALOGGER_PYTHON%" "%~dp0..\tools\simulador_modbus.py" %*
    exit /b
)
if exist "%~dp0..\.venv\Scripts\python.exe" (
    "%~dp0..\.venv\Scripts\python.exe" "%~dp0..\tools\simulador_modbus.py" %*
    exit /b
)
where py >nul 2>nul
if not errorlevel 1 (
    py -3 "%~dp0..\tools\simulador_modbus.py" %*
    exit /b
)
python -c "import sys; assert sys.version_info >= (3, 10)" >nul 2>nul
if not errorlevel 1 (
    python "%~dp0..\tools\simulador_modbus.py" %*
    exit /b
)
rem Compatibilidad con el entorno local anterior, sin nombre de usuario fijo.
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "%~dp0..\tools\simulador_modbus.py" %*
    exit /b
)
echo No se encuentra Python. Instale Python 3.10+ o defina DATALOGGER_PYTHON.
exit /b 1

