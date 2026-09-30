#!/usr/bin/env bash
# ATENÇÃO: rode este script UMA VEZ, numa pasta vazia, para criar o repositório.
# NÃO rode dentro de um clone existente — o "git init" sobrescreve o histórico.
#
# Requer: git e GitHub CLI (https://cli.github.com) com "gh auth login" já feito.
set -euo pipefail
NOME="${1:-agentes-ia-livro}"

git init -b main
git add .
git commit -m "Código e testes das Partes I a V (versões técnica e comercial)"
gh repo create "$NOME" --private --source=. --remote=origin --push

echo "Pronto: repositório privado '$NOME' criado e enviado."
echo "Os testes rodam automaticamente no GitHub Actions a cada push."
