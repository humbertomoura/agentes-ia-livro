#!/usr/bin/env bash
# Publica este repositório no GitHub (rode uma vez, na pasta do repositório).
# Requer: git e GitHub CLI (https://cli.github.com), com "gh auth login" já feito.
set -euo pipefail
NOME="${1:-agentes-ia-livro}"

git init -b main
git add .
git commit -m "Código e testes das Partes I a V (versões técnica e comercial)"
gh repo create "$NOME" --private --source=. --remote=origin --push

echo "Pronto: repositório privado '$NOME' criado e enviado."
echo "Os testes rodam automaticamente no GitHub Actions a cada push."
