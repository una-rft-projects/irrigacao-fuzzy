#!/usr/bin/env bash
# Cria o ambiente virtual (.venv) e instala as dependências — macOS e Linux
set -e
cd "$(dirname "$0")"

PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python

echo "Criando ambiente virtual em .venv ..."
"$PY" -m venv .venv

echo "Instalando dependências ..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo
echo "Pronto! Para rodar:"
echo "  source .venv/bin/activate"
echo "  python irrigacao_fuzzy.py"
echo "ou simplesmente: ./run.sh"
