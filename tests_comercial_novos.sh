#!/usr/bin/env bash
set -e
for d in comercial/cap13_encomenda_casamento comercial/cap30_projeto_final; do
  (cd "$d" && python -m pytest -q)
done
