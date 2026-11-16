#!/usr/bin/env bash
# Roda o controlador usando o ambiente virtual — macOS e Linux
# Exemplos: ./run.sh    ,    ./run.sh -u 35 -t 30    ,    ./run.sh --mostrar
set -e
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "Ambiente virtual não encontrado. Rode primeiro: ./setup.sh"
  exit 1
fi
.venv/bin/python irrigacao_fuzzy.py "$@"
