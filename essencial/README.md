# Versão comercial essencial — fonte

Cada capítulo é um arquivo de marcação em `cap/`. `make.py` monta o docx a partir deles,
reaproveitando estilos, figuras e trechos do comercial v1 (`@KEEP`, `@SUB`, `@FIG`).

    python make.py saida.docx

Requer o arquivo `Livro_Agentes_Partes_I_a_V_Comercial_v1.docx` e os índices extraídos dele
(ver o início de `build.py` para os caminhos). O código dos capítulos "Mão na massa" novos
está em `comercial/cap13_encomenda_casamento` e `comercial/cap30_projeto_final`, com testes
que conferem a saída impressa no livro.
