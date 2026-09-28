# Pendências encontradas ao montar o repositório

## Versão técnica (v10 refinada)

1. **Cap. 33, seção 33.9 — fixture inexistente.** `test_cumulative_compaction(fake_client)` depende de uma fixture `fake_client` que o livro não define. No repositório, ela está em `tests/conftest.py` (um resumidor falso que devolve o resumo anterior mais as mensagens). **Sugestão:** acrescentar ao livro uma definição curta do cliente falso, ou mencionar que ela está no repositório.
2. **Cap. 15, seções 15.5 e 15.6 — trechos, não programa completo.** O trecho de validação usa `call`, `args`, `state` e `log_validation_error` fora de contexto, e o trace da seção 15.9 não é produzido por nenhum código do capítulo. No repositório entraram só o loop real (15.2) e o decisor simulado (15.4), que rodam sozinhos. **Sugestão:** deixar explícito no texto que 15.5 e 15.6 são fragmentos, ou completar o exemplo.

## Versão comercial (Partes I–V)

- Gerar a edição em EPUB 3 para Kindle: sumário com links, cores automáticas (modo escuro), caixas e código em estilos próprios, figuras com texto alternativo.
- Acrescentar: página de direitos autorais, aviso de marcas de terceiros, sobre o autor, apêndice "Prepare seu ambiente" e link para este repositório.
