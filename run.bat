@echo off
REM Roda o controlador usando o ambiente virtual - Windows
REM Exemplos: run.bat, run.bat -u 35 -t 30, run.bat --mostrar
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Ambiente virtual nao encontrado. Rode primeiro: setup.bat
  pause
  exit /b 1
)
".venv\Scripts\python.exe" irrigacao_fuzzy.py %*
