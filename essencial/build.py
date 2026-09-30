"""Gerador do livro comercial essencial a partir de uma marcação simples.

Reaproveita estilos, cabeçalho, rodapé, figuras e formatação do docx comercial v1.
Marcação (um elemento por bloco, separados por linha em branco):
  @PART I|Título|descrição
  @CHAPTER n|Título|Subtítulo
  ## Seção        ### Subseção
  - item de lista
  @BOX TIPO|Título   (linhas seguintes = parágrafos; '- ' = lista)  @END
  @RESUMO / @MAO  (linhas)  @END
  @TABLE (linhas 'a | b | c', a primeira é o cabeçalho)  @END
  @CODE (linhas de código)  @END
  @FIG n.m|legenda|chave-da-figura-original
  @KEEP i        copia o elemento i do docx original
  texto comum com **negrito**, *itálico* e `código`
"""
import html, pickle, re, sys, zipfile, shutil, os

SRC = '/mnt/user-data/uploads/Livro_Agentes_Partes_I_a_V_Comercial_v1.docx'
ELS = pickle.load(open('/home/claude/com_els.pkl', 'rb'))
TPL = pickle.load(open('/home/claude/com_tbl_tpl.pkl', 'rb'))

def esc(s): return html.escape(s, quote=False)

RUN_BASE = ''
def runs(text, base=RUN_BASE, size=None):
    """converte **b**, *i*, `c` em runs."""
    out = []
    sz = f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>' if size else ''
    for part in re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', text):
        if not part: continue
        rpr = base + sz
        if part.startswith('**'):
            rpr = base + '<w:b/><w:bCs/>' + sz; part = part[2:-2]
        elif part.startswith('*'):
            rpr = base + '<w:i/><w:iCs/>' + sz; part = part[1:-1]
        elif part.startswith('`'):
            rpr = ('<w:rFonts w:ascii="Consolas" w:cs="Consolas" w:eastAsia="Consolas" '
                   'w:hAnsi="Consolas"/>' + (sz or '<w:sz w:val="19"/><w:szCs w:val="19"/>'))
            part = part[1:-1]
        out.append(f'<w:r>{"<w:rPr>"+rpr+"</w:rPr>" if rpr else ""}'
                   f'<w:t xml:space="preserve">{esc(part)}</w:t></w:r>')
    return ''.join(out)

P_BODY = '<w:pPr><w:spacing w:after="140" w:line="300"/><w:jc w:val="both"/></w:pPr>'
def para(t): return f'<w:p>{P_BODY}{runs(t)}</w:p>'
def h2(t): return f'<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr>{runs(t)}</w:p>'
def h3(t): return f'<w:p><w:pPr><w:pStyle w:val="Heading3"/></w:pPr>{runs(t)}</w:p>'
def bullet(t):
    return ('<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/>'
            '<w:numId w:val="2"/></w:numPr><w:spacing w:after="80" w:line="290"/>'
            f'<w:jc w:val="left"/></w:pPr>{runs(t)}</w:p>')
BR = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
SP60 = '<w:p><w:pPr><w:spacing w:after="60"/></w:pPr></w:p>'
SP160 = '<w:p><w:pPr><w:spacing w:after="160"/></w:pPr></w:p>'
ARIAL = '<w:rFonts w:ascii="Arial" w:cs="Arial" w:eastAsia="Arial" w:hAnsi="Arial"/>'
GEORGIA = '<w:rFonts w:ascii="Georgia" w:cs="Georgia" w:eastAsia="Georgia" w:hAnsi="Georgia"/>'

def part_open(num, title, desc):
    return (BR + '<w:p><w:pPr><w:spacing w:after="200" w:before="2600"/><w:jc w:val="center"/></w:pPr>'
            f'<w:r><w:rPr>{ARIAL}<w:b/><w:bCs/><w:color w:val="E07A1F"/><w:spacing w:val="60"/>'
            f'<w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr><w:t xml:space="preserve">PARTE {esc(num)}</w:t></w:r></w:p>'
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/><w:pBdr><w:bottom w:val="single" w:color="E07A1F" '
            'w:sz="8" w:space="16"/></w:pBdr><w:spacing w:after="500"/><w:jc w:val="center"/></w:pPr>'
            f'<w:r><w:rPr><w:sz w:val="52"/><w:szCs w:val="52"/></w:rPr><w:t xml:space="preserve">{esc(title)}</w:t></w:r></w:p>'
            '<w:p><w:pPr><w:spacing w:line="320"/><w:ind w:left="400" w:right="400"/><w:jc w:val="center"/></w:pPr>'
            f'<w:r><w:rPr>{GEORGIA}<w:i/><w:iCs/><w:color w:val="6B7280"/><w:sz w:val="23"/><w:szCs w:val="23"/>'
            f'</w:rPr><w:t xml:space="preserve">{esc(desc)}</w:t></w:r></w:p>')

def chapter_open(label, title, sub):
    return (BR + '<w:p><w:pPr><w:spacing w:after="120" w:before="1400"/></w:pPr>'
            f'<w:r><w:rPr>{ARIAL}<w:b/><w:bCs/><w:color w:val="E07A1F"/><w:spacing w:val="40"/>'
            f'<w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr><w:t xml:space="preserve">{esc(label)}</w:t></w:r></w:p>'
            f'<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t xml:space="preserve">{esc(title)}</w:t></w:r></w:p>'
            + ('<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:color="0E7C7B" w:sz="6" w:space="12"/></w:pBdr>'
               f'<w:spacing w:after="480"/></w:pPr><w:r><w:rPr>{GEORGIA}<w:i/><w:iCs/><w:color w:val="6B7280"/>'
               f'<w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr><w:t xml:space="preserve">{esc(sub)}</w:t></w:r></w:p>'
               if sub else ''))

# ---------- caixas ----------
def _box_tpl(label):
    for k, v in TPL.items():
        if k.startswith(label): return v
    raise KeyError(label)
def box(label, title, lines):
    t = _box_tpl(label)
    head_end = t.find('</w:p>') + 6
    p0 = t.find('<w:p>', t.find('<w:tc>'))
    head = t[p0:head_end]
    if title:
        head = re.sub(r'(<w:t xml:space="preserve">)  ·  [^<]*(</w:t>)', r'\1  ·  ' + esc(title).replace('\\', r'\\') + r'\2', head)
    else:
        head = re.sub(r'<w:r><w:rPr>(?:(?!</w:r>).)*<w:t xml:space="preserve">  ·  [^<]*</w:t></w:r>', '', head)
    bodyp = []
    for ln in lines:
        if ln.startswith('- '):
            bodyp.append('<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/>'
                         '<w:numId w:val="3"/></w:numPr><w:spacing w:after="60" w:line="276"/></w:pPr>'
                         + runs(ln[2:], size=20) + '</w:p>')
        else:
            bodyp.append('<w:p><w:pPr><w:spacing w:after="80" w:line="276"/></w:pPr>' + runs(ln, size=20) + '</w:p>')
    end = t.rfind('</w:tc>')
    return SP60 + t[:p0] + head + ''.join(bodyp) + t[end:] + SP160

# ---------- tabelas ----------
def table(rows):
    ncol = len(rows[0])
    tpl = TPL['TABELA3' if ncol == 3 else 'TABELA2']
    widths = [int(w) for w in re.findall(r'<w:gridCol w:w="(\d+)"/>', tpl)]
    cell_hdr = re.search(r'(<w:tc>.*?</w:tc>)', tpl, re.S).group(1)
    trs = re.findall(r'<w:tr>.*?</w:tr>', tpl, re.S)
    body_cells = re.findall(r'<w:tc>.*?</w:tc>', trs[1], re.S)
    def fill(cell, w, text):
        cell = re.sub(r'w:w="\d+"', f'w:w="{w}"', cell, count=1)
        prefix = cell[:cell.find('<w:r>')]
        rpr = re.search(r'<w:rPr>(.*?)</w:rPr>', cell[cell.find('<w:r>'):], re.S).group(1)
        return prefix + runs(text, base=rpr) + '</w:p></w:tc>'
    head = trs[0][:trs[0].find('<w:tc>')]
    out = tpl[:tpl.find('<w:tr>')]
    out = re.sub(r'<w:tblGrid>.*?</w:tblGrid>', '<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>', out)
    def row(cells_tpl, vals, trhead):
        return trhead + ''.join(fill(cells_tpl[min(i, len(cells_tpl) - 1)], widths[i], v) for i, v in enumerate(vals)) + '</w:tr>'
    hdr_cells = re.findall(r'<w:tc>.*?</w:tc>', trs[0], re.S)
    out += row(hdr_cells, rows[0], head)
    bhead = trs[1][:trs[1].find('<w:tc>')]
    for r in rows[1:]: out += row(body_cells, r, bhead)
    return SP60 + out + '</w:tbl>' + SP160

# ---------- código ----------
CODE_RPR = ('<w:rPr><w:rFonts w:ascii="Consolas" w:cs="Consolas" w:eastAsia="Consolas" w:hAnsi="Consolas"/>'
            '<w:color w:val="1F2933"/><w:sz w:val="16"/><w:szCs w:val="16"/></w:rPr>')
def code(lines):
    out = []
    for i, ln in enumerate(lines):
        before = '120' if i == 0 else '0'
        after = '120' if i == len(lines) - 1 else '0'
        out.append('<w:p><w:pPr><w:keepLines/><w:shd w:fill="F3F4F6" w:color="auto" w:val="clear"/>'
                   f'<w:spacing w:after="{after}" w:before="{before}" w:line="240"/>'
                   '<w:ind w:left="120" w:right="120"/></w:pPr>'
                   f'<w:r>{CODE_RPR}<w:t xml:space="preserve">{esc(ln) if ln else " "}</w:t></w:r></w:p>')
    return ''.join(out) + SP60

# ---------- figuras ----------
def figure(num, caption, orig_caption_start):
    for i, e in enumerate(ELS):
        if '<w:drawing' in e:
            cap = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', ELS[i + 1]))
            if cap.startswith(orig_caption_start):
                capx = ELS[i + 1]
                capx = re.sub(r'<w:t xml:space="preserve">.*?</w:t>',
                              f'<w:t xml:space="preserve">Figura {esc(num)} — {esc(caption)}</w:t>', capx, count=1, flags=re.S)
                capx = re.sub(r'(</w:t></w:r>)<w:r>.*?(</w:p>)', r'\1\2', capx, flags=re.S)
                return e + capx
    raise KeyError(orig_caption_start)

# ---------- parser ----------
def parse(md):
    out = []
    blocks = re.split(r'\n\s*\n', md.strip('\n'))
    i = 0
    lines = md.split('\n')
    k = 0
    subs = []
    while k < len(lines):
        ln = lines[k]
        if not ln.strip(): k += 1; continue
        if ln.startswith('@SUB '):
            a, b = ln[5:].split('=>'); subs.append((esc(a), esc(b))); k += 1; continue
        if ln.startswith('@PART '):
            a = ln[6:].split('|'); out.append(part_open(*a)); k += 1
        elif ln.startswith('@CHAPTER '):
            a = ln[9:].split('|'); out.append(chapter_open(*a)); k += 1
        elif ln.startswith(('@BOX ', '@RESUMO', '@MAO', '@TABLE', '@CODE')):
            j = k + 1; buf = []
            while lines[j].strip() != '@END': buf.append(lines[j]); j += 1
            if ln.startswith('@BOX '):
                lab, tit = (ln[5:].split('|') + [''])[:2]
                out.append(box(lab.strip(), tit.strip(), [b for b in buf if b.strip()]))
            elif ln.startswith('@RESUMO'):
                out.append(box('RESUMO RÁPIDO', '', ['- ' + b.lstrip('- ') for b in buf if b.strip()]))
            elif ln.startswith('@MAO'):
                out.append(box('MÃO NA MASSA', '', [b for b in buf if b.strip()]))
            elif ln.startswith('@TABLE'):
                out.append(table([[c.strip() for c in b.split('|')] for b in buf if b.strip()]))
            else:
                out.append(code(buf))
            k = j + 1
        elif ln.startswith('@IMG '):
            a = ln[5:].split('|'); out.append(new_figure(*a)); k += 1
        elif ln.startswith('@FIG '):
            a = ln[5:].split('|'); out.append(SP60 + figure(*a)); k += 1
        elif ln.startswith('@KEEP '):
            got = []
            for idx in ln[6:].split(','):
                if '-' in idx:
                    a, b = map(int, idx.split('-')); got.extend(ELS[a:b + 1])
                else: got.append(ELS[int(idx)])
            blob = ''.join(got)
            for a, b in subs:
                if a not in blob: raise SystemExit(f'@SUB sem alvo: {a!r} em {ln}')
                blob = blob.replace(a, b)
            subs = []
            out.append(blob)
            k += 1
        elif ln.startswith('### '): out.append(h3(ln[4:])); k += 1
        elif ln.startswith('## '): out.append(h2(ln[3:])); k += 1
        elif ln.startswith('- '): out.append(bullet(ln[2:])); k += 1
        else: out.append(para(ln.strip())); k += 1
    return ''.join(out)

def build(chapter_files, out_path, front_md):
    work = '/home/claude/ess/unz'
    shutil.rmtree(work, ignore_errors=True)
    zipfile.ZipFile(SRC).extractall(work)
    x = open(f'{work}/word/document.xml', encoding='utf8').read()
    start = x.find('<w:body>') + 8
    sect_last = x.rfind('<w:sectPr')
    # parágrafo com a quebra de seção após o sumário (índice no ELS)
    sect_para = [e for e in ELS if '<w:sectPr' in e][0]
    front = parse(front_md['title']) + parse(front_md['toc']) + sect_para
    body = ''.join(parse(open(f).read()) for f in chapter_files)
    x = x[:start] + front + parse(front_md['intro']) + body + x[sect_last:]
    open(f'{work}/word/document.xml', 'w', encoding='utf8').write(x)
    # comentários vazios / core
    core = f'{work}/docProps/core.xml'
    if os.path.exists(core):
        c = open(core, encoding='utf8').read()
        c = re.sub(r'<dc:title>.*?</dc:title>', '<dc:title>Agentes de Inteligência Artificial</dc:title>', c)
        open(core, 'w', encoding='utf8').write(c)
    if os.path.exists(out_path): os.remove(out_path)
    cwd = os.getcwd(); os.chdir(work)
    os.system(f'zip -qXr "{out_path}" .'); os.chdir(cwd)


def _retext(el, text):
    return re.sub(r'<w:t xml:space="preserve">.*?</w:t>', lambda m: f'<w:t xml:space="preserve">{esc(text)}</w:t>', el, count=1, flags=re.S)

def title_page(l1, l2, s1, s2, parts, author, edition):
    e = ELS
    p4 = e[4]
    first_run = re.search(r'<w:r>.*?</w:r>', p4, re.S).group(0)
    rpr = re.search(r'<w:rPr>.*?</w:rPr>', first_run, re.S).group(0)
    runs_ = ''.join((f'<w:r>{rpr}<w:t xml:space="preserve">{esc(p)}</w:t></w:r>' if i == 0 else
                     f'<w:r>{rpr}<w:br/><w:t xml:space="preserve">{esc(p)}</w:t></w:r>') for i, p in enumerate(parts))
    p4 = p4[:p4.find('<w:r>')] + runs_ + '</w:p>'
    return (_retext(e[0], l1) + _retext(e[1], l2) + _retext(e[2], s1) + _retext(e[3], s2) + p4 +
            _retext(e[5], author) + _retext(e[6], edition))

def toc(items):
    """items: lista de ('part'|'item', texto)"""
    out = [ELS[7], ELS[8]]
    for kind, t in items:
        out.append(_retext(ELS[10] if kind == 'part' else ELS[11], t))
    return ''.join(out)

def build2(chapter_files, out_path, title_xml, toc_xml):
    work = '/home/claude/ess/unz'
    shutil.rmtree(work, ignore_errors=True)
    zipfile.ZipFile(SRC).extractall(work)
    x = open(f'{work}/word/document.xml', encoding='utf8').read()
    start = x.find('<w:body>') + 8
    sect_last = x.rfind('<w:sectPr')
    sect_para = [e for e in ELS if '<w:sectPr' in e][0]
    body = ''.join(parse(open(f, encoding='utf8').read()) for f in chapter_files)
    # o primeiro capítulo não deve começar com quebra de página extra depois da seção
    x = x[:start] + title_xml + toc_xml + sect_para + body + x[sect_last:]
    x = postprocess(x)
    open(f'{work}/word/document.xml', 'w', encoding='utf8').write(x)
    install_images(work)
    NEW_IMAGES.clear()
    hdr = f'{work}/word/header1.xml'
    h = open(hdr, encoding='utf8').read()
    open(hdr, 'w', encoding='utf8').write(h)
    core = f'{work}/docProps/core.xml'
    if os.path.exists(core):
        c = open(core, encoding='utf8').read()
        c = re.sub(r'<dc:title>.*?</dc:title>', '<dc:title>Agentes de Inteligência Artificial</dc:title>', c)
        open(core, 'w', encoding='utf8').write(c)
    if os.path.exists(out_path): os.remove(out_path)
    cwd = os.getcwd(); os.chdir(work)
    os.system(f'zip -qXr "{out_path}" .'); os.chdir(cwd)


# ---------------- pós-processamento para Kindle e acessibilidade ----------------
def _txt(el):
    return html.unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', el)))

def fix_alt_text(body):
    """o texto alternativo das figuras passa a ser a legenda renumerada"""
    parts = re.split(r'(<w:p>(?:(?!</w:p>).)*?<w:drawing>.*?</w:p>)', body, flags=re.S)
    for i in range(1, len(parts), 2):
        nxt = parts[i + 1] if i + 1 < len(parts) else ''
        m = re.search(r'<w:p>.*?</w:p>', nxt, re.S)
        cap = _txt(m.group(0)) if m else ''
        if cap.startswith('Figura'):
            capx = html.escape(cap, quote=True)
            parts[i] = re.sub(r'descr="[^"]*"', f'descr="{capx}"', parts[i])
            parts[i] = re.sub(r'(<wp:docPr [^>]*?)title="[^"]*"', rf'\1title="{capx}"', parts[i])
    return ''.join(parts)

def boxes_to_paragraphs(body):
    """caixas de uma célula viram parágrafos com borda e fundo (reflowable)"""
    def conv(m):
        t = m.group(0)
        if t.count('<w:gridCol') != 1 or t.count('<w:tc>') != 1:
            return t
        fill = re.search(r'<w:shd [^>]*w:fill="([0-9A-Fa-f]{6})"', t)
        fill = fill.group(1) if fill else 'F3F4F6'
        bcol = re.search(r'<w:left [^>]*w:color="([0-9A-Fa-f]{6})"', t) or re.search(r'w:color="([0-9A-Fa-f]{6})"', t)
        bcol = bcol.group(1) if bcol else '0E7C7B'
        lw = re.search(r'<w:left [^>]*w:sz="(\d+)"', t)
        lw = lw.group(1) if lw else '18'
        cell = t[t.find('<w:tc>'):t.rfind('</w:tc>')]
        paras = re.findall(r'<w:p>.*?</w:p>|<w:p .*?</w:p>', cell, re.S)
        out = []
        n = len(paras)
        for k, p in enumerate(paras):
            bdr = (f'<w:pBdr><w:top w:val="single" w:sz="4" w:space="6" w:color="{fill}"/>'
                   f'<w:left w:val="single" w:sz="{lw}" w:space="8" w:color="{bcol}"/>'
                   f'<w:bottom w:val="single" w:sz="4" w:space="6" w:color="{fill}"/>'
                   f'<w:right w:val="single" w:sz="4" w:space="8" w:color="{fill}"/></w:pBdr>'
                   f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>')
            keep = '<w:keepNext/>' if k < n - 1 else ''
            ind = '<w:ind w:left="200" w:right="200"/>'
            if '<w:pPr>' in p:
                pp = re.search(r'<w:pPr>(.*?)</w:pPr>', p, re.S).group(1)
                pp = re.sub(r'<w:pBdr>.*?</w:pBdr>|<w:shd [^>]*/>|<w:ind [^>]*/>', '', pp, flags=re.S)
                # ordem do schema: pStyle, keepNext, numPr, pBdr, shd, spacing, ind, jc
                style = re.search(r'<w:pStyle [^>]*/>', pp); style = style.group(0) if style else ''
                num = re.search(r'<w:numPr>.*?</w:numPr>', pp, re.S); num = num.group(0) if num else ''
                spc = re.search(r'<w:spacing [^>]*/>', pp); spc = spc.group(0) if spc else ''
                jc = re.search(r'<w:jc [^>]*/>', pp); jc = jc.group(0) if jc else ''
                rpr = re.search(r'<w:rPr>.*?</w:rPr>', pp, re.S); rpr = rpr.group(0) if rpr else ''
                newp = f'<w:pPr>{style}{keep}{num}{bdr}{spc}{ind}{jc}{rpr}</w:pPr>'
                p = re.sub(r'<w:pPr>.*?</w:pPr>', lambda _: newp, p, count=1, flags=re.S)
            else:
                p = p.replace('<w:p>', f'<w:p><w:pPr>{keep}{bdr}{ind}</w:pPr>', 1)
            out.append(p)
        return ''.join(out)
    return re.sub(r'<w:tbl>.*?</w:tbl>', conv, body, flags=re.S)

def header_rows(body):
    """primeira linha de tabelas reais marcada como cabeçalho (repete na página)"""
    def conv(m):
        t = m.group(0)
        if t.count('<w:gridCol') < 2 or '<w:tblHeader/>' in t:
            return t
        i = t.find('<w:tr>')
        if i < 0: return t
        j = i + len('<w:tr>')
        if t[j:j + 8] == '<w:trPr>':
            return t[:j + 8] + '<w:tblHeader/>' + t[j + 8:]
        return t[:j] + '<w:trPr><w:tblHeader/></w:trPr>' + t[j:]
    return re.sub(r'<w:tbl>.*?</w:tbl>', conv, body, flags=re.S)

def link_toc(body):
    """marca capítulos com bookmarks e liga as entradas do sumário a eles"""
    heads = {}
    k = [0]
    def bm(m):
        p = m.group(0)
        t = _txt(p).strip()
        if not t or t.lower() in heads: return p
        k[0] += 1; name = f'_cap{k[0]}'; heads[t.lower()] = name
        return re.sub(r'(<w:pPr>.*?</w:pPr>)', lambda mm: mm.group(1) + f'<w:bookmarkStart w:id="{9000+k[0]}" w:name="{name}"/>', p, count=1, flags=re.S).replace('</w:p>', f'<w:bookmarkEnd w:id="{9000+k[0]}"/></w:p>')
    # só títulos de capítulo/fechamento (Heading1 fora do sumário)
    toc_end = body.find('<w:sectPr')
    head, rest = body[:toc_end], body[toc_end:]
    rest = re.sub(r'<w:p><w:pPr><w:pStyle w:val="Heading1"/>.*?</w:p>', bm, rest, flags=re.S)
    def link(m):
        p = m.group(0); t = _txt(p).strip()
        key = re.sub(r'^(\d+\.\s*|Apêndice [A-Z]: )', '', t).lower()
        name = heads.get(key)
        if not name: return p
        runs = re.findall(r'<w:r>.*?</w:r>', p, re.S)
        pre = p[:p.find('<w:r>')]
        return pre + f'<w:hyperlink w:anchor="{name}" w:history="1">' + ''.join(runs) + '</w:hyperlink></w:p>'
    head = re.sub(r'<w:p>(?:(?!</w:p>).)*?</w:p>', lambda m: link(m) if re.search(r'\d+\. |Fechando|Antes de começar|Apêndice|Glossário', _txt(m.group(0))) and '<w:r>' in m.group(0) else m.group(0), head, flags=re.S)
    return head + rest

def postprocess(x):
    start = x.find('<w:body>') + 8
    end = x.rfind('<w:sectPr')
    body = x[start:end]
    body = fix_alt_text(body)
    body = header_rows(body)
    body = boxes_to_paragraphs(body)
    body = link_toc(body)
    return x[:start] + body + x[end:]


# ---------------- figuras novas (@IMG caminho|n.m|legenda) ----------------
NEW_IMAGES = []

def new_figure(path, num, caption):
    from PIL import Image
    idx = next(i for i, e in enumerate(ELS) if '<w:drawing' in e)
    tpl, cap_tpl = ELS[idx], ELS[idx + 1]
    k = len(NEW_IMAGES) + 1
    rid = f'rIdNovaFig{k}'
    NEW_IMAGES.append((rid, path))
    w, h = Image.open(path).size
    cx = int(re.search(r'<wp:extent cx="(\d+)"', tpl).group(1))
    cx = min(cx, 3900000)
    cy = int(cx * h / w)
    d = re.sub(r'r:embed="[^"]+"', f'r:embed="{rid}"', tpl)
    d = re.sub(r'<wp:extent cx="\d+" cy="\d+"/>', f'<wp:extent cx="{cx}" cy="{cy}"/>', d)
    d = re.sub(r'<a:ext cx="\d+" cy="\d+"/>', f'<a:ext cx="{cx}" cy="{cy}"/>', d)
    d = re.sub(r'(<wp:docPr [^>]*?)id="\d+"', rf'\g<1>id="{7000 + k}"', d)
    d = re.sub(r'(<pic:cNvPr [^>]*?)id="\d+"', rf'\g<1>id="{7000 + k}"', d)
    d = re.sub(r'name="[^"]*\.png"', f'name="nova_{k}.png"', d)
    capx = re.sub(r'<w:t xml:space="preserve">.*?</w:t>',
                  f'<w:t xml:space="preserve">Figura {esc(num)} — {esc(caption)}</w:t>', cap_tpl, count=1, flags=re.S)
    capx = re.sub(r'(</w:t></w:r>)<w:r>.*?(</w:p>)', r'\1\2', capx, flags=re.S)
    return SP60 + d + capx

def install_images(work):
    if not NEW_IMAGES: return
    rels = f'{work}/word/_rels/document.xml.rels'
    r = open(rels, encoding='utf8').read()
    add = ''
    for rid, path in NEW_IMAGES:
        name = 'nova_' + os.path.basename(path)
        shutil.copy(path, f'{work}/word/media/{name}')
        add += (f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                f'relationships/image" Target="media/{name}"/>')
    r = r.replace('</Relationships>', add + '</Relationships>')
    open(rels, 'w', encoding='utf8').write(r)
