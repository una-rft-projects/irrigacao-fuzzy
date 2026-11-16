@echo off
REM Cria o ambiente virtual (.venv) e instala as dependencias - Windows
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" goto instalar

echo Criando ambiente virtual em .venv ...
py -m venv .venv 2>nul || python -m venv .venv
if errorlevel 1 goto erro
if not exist ".venv\Scripts\python.exe" (
  echo Nao foi possivel criar o ambiente virtual. Verifique se o Python esta instalado.
  pause
  exit /b 1
)

:instalar
echo Instalando dependencias ...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto erro
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto erro
".venv\Scripts\python.exe" -c "import numpy, scipy, matplotlib.pyplot, skfuzzy, networkx"
if errorlevel 1 goto erro

echo.
echo Pronto! Para rodar:
echo   .venv\Scripts\activate
echo   python irrigacao_fuzzy.py
echo ou simplesmente: run.bat
pause
exit /b 0

:erro
echo.
echo Falha na configuracao. Confira o erro acima e a secao Problemas comuns do README.md.
pause
exit /b 1
