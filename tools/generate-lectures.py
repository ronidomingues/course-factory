#!/usr/bin/env python3
"""generate-lectures.py — writes a DRAFT of the lecture decks from the course.

    python3 tools/generate-lectures.py <course>
    python3 tools/generate-lectures.py <course> --force   # overwrite existing

Um arquivo do curso vira uma aula; um `##` do arquivo vira uma tela de transição;
um `###` vira um slide. A prosa não vai para o slide: vai para o bloco de notas,
que é o roteiro de quem fala. O slide fica com o que já é curto no material —
listas, tabelas pequenas, código recortado e a frase-chave de cada parágrafo.

**Isto é um rascunho, e o arquivo diz isso no cabeçalho.** Slide bom se escreve;
o que este programa faz é tirar do zero, cobrir 100% do material e deixar a
revisão em cima de algo pronto. Para um curso novo, escreva as aulas à mão — a
régua está no EDITORIAL-STANDARD.md do kit de marca.

O programa **nunca toca no material do curso**: escreve apenas em
`97-publicacao/slides/md/`.
"""

import argparse
import os
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PASTA_PUBLICACAO = "97-publicacao"

# ------------------------------------------------- reaproveitar o md2book ---


def _carregar_blocks():
    """Usa o analisador de Markdown do md2book em vez de escrever outro."""
    sys.path.insert(0, str(TOOLS))
    import common
    src = common.find_md2book_source()
    if src is None:
        print("ERROR: md2book not found. It should be vendored at "
              "%s; ou aponte a variável MD2BOOK para a pasta dele."
              % (TOOLS / "md2book"), file=sys.stderr)
        sys.exit(2)
    sys.path.insert(0, str(src))
    from md2book import blocks
    return blocks


B = _carregar_blocks()

# ------------------------------------------------------------- parâmetros ---

LINHAS_POR_SLIDE = 9          # antes de quebrar em continuação
ITENS_POR_SLIDE = 6
LARGURA_ITEM = 130            # caracteres de um item de lista
LINHAS_CODIGO = 12           # linhas de código que cabem sem apertar a tela
LINHAS_TABELA = 6            # linhas de dados de uma tabela projetada
MAX_SLIDES_POR_AULA = 40      # acima disso, a aula vira "parte 1", "parte 2"
NOTAS_MAXIMO = 700

# Arquivos que não viram aula própria.
IGNORAR = {"LEIA-ME.md", "README.md"}

_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
_IMAGEM = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_NUMERO_TITULO = re.compile(r"^\s*\d{1,3}(\.\d+)*\s*[·.:)\-–—]\s+")
_FIM_FRASE = re.compile(r"(?<=[.!?;:])\s")


def limpar(texto: str) -> str:
    """Tira o que não funciona na projeção: imagem, link longo, espaço duplo."""
    texto = _IMAGEM.sub(lambda m: m.group(1) or "", texto)
    texto = _LINK.sub(lambda m: m.group(1) or m.group(2), texto)
    texto = texto.replace("\n", " ")
    return re.sub(r"\s+", " ", texto).strip()


def encurtar(texto: str, limite: int = LARGURA_ITEM) -> str:
    """Corta no fim de uma frase; só corta no meio quando não há frase."""
    texto = limpar(texto)
    if len(texto) <= limite:
        return texto
    trecho = texto[:limite]
    partes = _FIM_FRASE.split(trecho)
    if len(partes) > 1 and len(partes[0]) >= 40:
        return partes[0].strip()
    for marca in (" — ", " – ", ", ", " ("):
        pos = trecho.rfind(marca)
        if pos >= 40:
            return trecho[:pos].strip(" ,;:—–(") + "…"
    return trecho.rsplit(" ", 1)[0].rstrip(" ,;:—–(") + "…"


def frase_chave(texto: str) -> str:
    """A primeira frase de um parágrafo — o que ele afirma."""
    texto = limpar(texto)
    partes = _FIM_FRASE.split(texto, 1)
    return encurtar(partes[0] if partes else texto)


def titulo_limpo(texto: str) -> str:
    return encurtar(_NUMERO_TITULO.sub("", limpar(texto)), 90)


def escorregadio(nome: str) -> str:
    """Nome de arquivo em kebab-case, sem acento."""
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", nome)
    limpo = "".join(c for c in nfkd if not unicodedata.combining(c))
    limpo = re.sub(r"[^a-zA-Z0-9]+", "-", limpo).strip("-").lower()
    return re.sub(r"-{2,}", "-", limpo)[:48] or "aula"


# ================================================================= modelo ===

class Slide:
    """Um slide em construção: título, linhas de conteúdo e notas."""

    def __init__(self, titulo=""):
        self.titulo = titulo
        self.linhas = []
        self.notas = []
        self.peso = 0

    def cabe(self, peso: int) -> bool:
        return self.peso + peso <= LINHAS_POR_SLIDE or not self.linhas

    def acrescentar(self, linhas, peso: int):
        self.linhas.extend(linhas)
        self.peso += peso

    def vazio(self) -> bool:
        return not self.linhas and not self.notas


class Aula:
    """Uma aula: título, seções e slides, na ordem em que serão projetados."""

    def __init__(self, titulo, origem):
        self.titulo = titulo
        self.origem = origem
        self.blocos = []          # ("secao", titulo, subtitulo) | ("slide", Slide)

    def secao(self, titulo, subtitulo=""):
        self.blocos.append(("secao", titulo, subtitulo))

    def slide(self, slide: Slide):
        if not slide.vazio():
            self.blocos.append(("slide", slide))

    @property
    def n_slides(self):
        return sum(1 for b in self.blocos if b[0] == "slide")


# =============================================================== conversão ===

def converter_documento(caminho: Path, titulo_curso: str) -> Aula:
    """Um arquivo do curso vira uma aula."""
    nos = B.analisar(caminho.read_text(encoding="utf-8"))
    titulo = caminho.stem
    aula = None
    atual = Slide()
    esperando_subtitulo = None

    def fechar():
        nonlocal atual
        if aula is not None:
            aula.slide(atual)
        atual = Slide(atual.titulo)
        atual.linhas = []
        atual.peso = 0
        atual.notas = []

    def novo_slide(titulo_slide):
        nonlocal atual
        if aula is not None:
            aula.slide(atual)
        atual = Slide(titulo_slide)

    for no in nos:
        # ------------------------------------------------------ títulos ----
        if isinstance(no, B.Cabecalho):
            if no.nivel == 1 and aula is None:
                titulo = titulo_limpo(no.texto)
                aula = Aula(titulo, caminho.name)
                atual = Slide("Do que trata esta aula")
                continue
            if aula is None:
                aula = Aula(titulo_limpo(titulo), caminho.name)
                atual = Slide("Do que trata esta aula")
            if no.nivel == 2:
                if atual and not atual.vazio():
                    aula.slide(atual)
                    atual = Slide()
                aula.secao(titulo_limpo(no.texto))
                esperando_subtitulo = len(aula.blocos) - 1
                atual = Slide(titulo_limpo(no.texto))
                continue
            if no.nivel == 3:
                novo_slide(titulo_limpo(no.texto))
                esperando_subtitulo = None
                continue
            # nível 4+: destaque dentro do slide
            if atual.cabe(1):
                atual.acrescentar(["**%s**" % titulo_limpo(no.texto)], 1)
            else:
                novo_slide(atual.titulo + " (cont.)")
                atual.acrescentar(["**%s**" % titulo_limpo(no.texto)], 1)
            continue

        if aula is None:                       # conteúdo antes de qualquer "#"
            aula = Aula(titulo_limpo(titulo), caminho.name)
            atual = Slide("Do que trata esta aula")

        # --------------------------------------------------- parágrafos ----
        if isinstance(no, B.Paragrafo):
            texto = limpar(no.texto)
            if not texto:
                continue
            if esperando_subtitulo is not None:
                tipo, t, _ = aula.blocos[esperando_subtitulo]
                aula.blocos[esperando_subtitulo] = (tipo, t, encurtar(texto, 110))
                esperando_subtitulo = None
                atual.notas.append(texto)
                continue
            atual.notas.append(texto)
            chave = frase_chave(texto)
            if chave and len(chave) > 25:
                if not atual.cabe(2):
                    novo_slide(_continuar(atual.titulo))
                atual.acrescentar(["- %s" % chave], 2)
            continue

        esperando_subtitulo = None

        # -------------------------------------------------------- listas ---
        if isinstance(no, B.Lista):
            itens = [_texto_do_item(i) for i in no.itens]
            itens = [i for i in itens if i]
            for pedaco in _lotes(itens, ITENS_POR_SLIDE):
                if not atual.cabe(len(pedaco)):
                    novo_slide(_continuar(atual.titulo))
                marca = "1." if no.ordenada else "-"
                atual.acrescentar(["%s %s" % (marca, i) for i in pedaco],
                                  len(pedaco))
            continue

        # ------------------------------------------------------ tabelas ----
        if isinstance(no, B.Tabela):
            linhas, peso = _tabela(no)
            if not atual.cabe(peso):
                novo_slide(_continuar(atual.titulo))
            atual.acrescentar(linhas, peso)
            continue

        # ------------------------------------------------------- código ----
        if isinstance(no, B.Codigo):
            linhas, peso = _codigo(no, caminho.name)
            if not atual.cabe(peso):
                novo_slide(_continuar(atual.titulo))
            atual.acrescentar(linhas, peso)
            continue

        # ----------------------------------------------------- citações ----
        if isinstance(no, B.Citacao):
            texto = limpar(" ".join(
                n.texto for n in no.filhos if isinstance(n, B.Paragrafo)))
            if not texto:
                continue
            if len(texto) <= 220:
                if not atual.cabe(3):
                    novo_slide(_continuar(atual.titulo))
                atual.acrescentar(["> %s" % texto], 3)
            else:
                atual.notas.append(texto)
            continue

    if aula is None:
        aula = Aula(titulo_limpo(titulo), caminho.name)
    aula.slide(atual)
    return aula


def _continuar(titulo: str) -> str:
    """Título do slide que continua o anterior — sem repetir o mesmo rótulo.

    Dois slides seguidos com o título idêntico fazem quem assiste achar que a
    apresentação voltou."""
    if not titulo or titulo.endswith("(cont.)"):
        return titulo
    return "%s (cont.)" % titulo


def _lotes(itens, tamanho):
    for i in range(0, len(itens), tamanho):
        yield itens[i:i + tamanho]


def _texto_do_item(item) -> str:
    partes = []
    for filho in item.filhos:
        if isinstance(filho, B.Paragrafo):
            partes.append(filho.texto)
        elif isinstance(filho, B.Lista):
            partes.extend(_texto_do_item(i) for i in filho.itens)
    texto = encurtar(" · ".join(p for p in partes if p))
    if item.tarefa is not None:
        texto = ("[x] " if item.tarefa else "[ ] ") + texto
    return texto


def _tabela(no):
    """Tabela pequena vai inteira; tabela grande vira as primeiras linhas."""
    colunas = no.cabecalho[:4]
    linhas_dados = no.linhas[:LINHAS_TABELA]
    cortada = len(no.linhas) > LINHAS_TABELA or len(no.cabecalho) > 4
    saida = ["| %s |" % " | ".join(encurtar(c, 40) for c in colunas),
             "|%s|" % "|".join("---" for _ in colunas)]
    for linha in linhas_dados:
        celulas = [encurtar(c, 60) for c in linha[:4]]
        celulas += [""] * (len(colunas) - len(celulas))
        saida.append("| %s |" % " | ".join(celulas))
    if cortada:
        saida.append("")
        saida.append("- Tabela completa no material do curso.")
    return saida, len(saida)


def _codigo(no, origem: str):
    linhas = no.codigo.rstrip("\n").split("\n")
    lingua = (no.linguagem or "").strip()
    if len(linhas) > LINHAS_CODIGO:
        linhas = linhas[:LINHAS_CODIGO - 1] + ["... (íntegra em %s)" % origem]
    bloco = ["```%s" % lingua] + linhas + ["```"]
    return bloco, len(linhas) + 1


# ================================================================ escrita ===

def escrever_deck(aula: Aula, destino: Path, numero: int, curso: str,
                  rotulo_extra: str = "", parte: int = 0) -> Path:
    # A parte entra no nome do arquivo: três aulas chamadas
    # "aula-04-manual-de-instalacao" e "aula-05-manual-de-instalacao" só se
    # distinguem pelo número, e quem procura o PDF certo erra.
    sufixo = "-parte-%d" % parte if parte else ""
    nome = "aula-%02d-%s%s.md" % (numero, escorregadio(aula.titulo), sufixo)
    caminho = destino / nome
    L = ["---",
         "aula: Aula %02d%s" % (numero, rotulo_extra),
         "curso: %s" % curso,
         "origem: %s" % aula.origem,
         "gerado: rascunho automático — revise antes de apresentar",
         "---",
         "",
         "# %s%s" % (aula.titulo, rotulo_extra),
         ""]
    for bloco in aula.blocos:
        if bloco[0] == "secao":
            L.append("## %s" % bloco[1])
            if bloco[2]:
                L.append("")
                L.append(bloco[2])
            L.append("")
            continue
        slide = bloco[1]
        L.append("### %s" % (slide.titulo or aula.titulo))
        L.append("")
        L.extend(slide.linhas)
        if slide.notas:
            texto = " ".join(slide.notas)
            if len(texto) > NOTAS_MAXIMO:
                texto = texto[:NOTAS_MAXIMO].rsplit(" ", 1)[0] + "…"
            L.append("")
            L.append("```notas")
            L.append(texto)
            L.append("```")
        L.append("")
    caminho.write_text("\n".join(L).rstrip() + "\n", encoding="utf-8")
    return caminho


def dividir_aula(aula: Aula):
    """Aula grande demais vira partes, cortando em fronteira de seção."""
    if aula.n_slides <= MAX_SLIDES_POR_AULA:
        return [aula]
    partes, atual, contagem = [], Aula(aula.titulo, aula.origem), 0
    for bloco in aula.blocos:
        if (bloco[0] == "secao" and contagem >= MAX_SLIDES_POR_AULA * 0.6
                and atual.blocos):
            partes.append(atual)
            atual, contagem = Aula(aula.titulo, aula.origem), 0
        atual.blocos.append(bloco)
        if bloco[0] == "slide":
            contagem += 1
    if atual.blocos:
        partes.append(atual)
    return partes


def documentos_do_curso(curso: Path):
    """Todo arquivo do curso que vira aula, em ordem de leitura."""
    def chave(p: Path):
        partes = []
        for trecho in re.split(r"(\d+)", p.relative_to(curso).as_posix()):
            partes.append(int(trecho) if trecho.isdigit() else trecho.lower())
        return partes

    docs = []
    for md in curso.rglob("*.md"):
        if PASTA_PUBLICACAO in md.parts or ".git" in md.parts:
            continue
        if md.name in IGNORAR and md.parent == curso:
            continue
        docs.append(md)
    return sorted(docs, key=chave)


def escrever_cobertura(destino: Path, curso_titulo: str, mapa) -> None:
    """A tabela que prova que todo arquivo do curso virou aula."""
    L = ["# Aulas de %s" % curso_titulo,
         "",
         "Um arquivo por aula, nomeado `aula-NN-<tema>.md`.",
         "",
         "> **Estes decks são rascunho gerado do material do curso** "
         "(`generate-lectures.py`).",
         "> A prosa foi para as notas do professor; o slide ficou com listas, "
         "tabelas",
         "> e código recortado. Antes de apresentar, revise: uma ideia por "
         "slide, até",
         "> dez linhas, e o número sempre com unidade e data.",
         "",
         "## Cobertura",
         "",
         "| Arquivo do curso | Aula | Slides |",
         "|---|---|---|"]
    total = 0
    for origem, arquivo, n in mapa:
        L.append("| `%s` | `%s` | %d |" % (origem, arquivo, n))
        total += n
    L += ["", "**%d aulas · %d slides · cobertura de %d arquivos.**"
          % (len(mapa), total, len({m[0] for m in mapa})),
          "",
          "## Gerar os PDFs",
          "",
          "```bash",
          "python3 tools/publish-course.py <curso> --only slides",
          "```",
          ""]
    (destino / "LEIA-ME.md").write_text("\n".join(L), encoding="utf-8")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Generates the draft lecture decks of a course.")
    p.add_argument("course", help="course folder")
    p.add_argument("--force", action="store_true",
                   help="overwrite decks that already exist")
    p.add_argument("--title", default="", help="course name used on the slides")
    args = p.parse_args(argv)

    curso = Path(args.course).expanduser().resolve()
    if not curso.is_dir():
        print("ERROR: folder not found: %s" % curso, file=sys.stderr)
        return 2

    destino = curso / PASTA_PUBLICACAO / "slides" / "md"
    destino.mkdir(parents=True, exist_ok=True)

    existentes = [x for x in destino.glob("aula-*.md")]
    if existentes and not args.force:
        print("%d decks already exist in %s — use --force to overwrite."
              % (len(existentes), destino))
        return 0
    for velho in existentes:
        velho.unlink()

    titulo_curso = args.title or re.sub(r"-\d{4}-\d{2}-\d{2}$", "",
                                         curso.name).replace("-", " ").title()
    mapa, numero = [], 0
    for doc in documentos_do_curso(curso):
        aula = converter_documento(doc, titulo_curso)
        if aula.n_slides == 0:
            continue
        partes = dividir_aula(aula)
        for i, parte in enumerate(partes, 1):
            numero += 1
            extra = "" if len(partes) == 1 else " — parte %d" % i
            arquivo = escrever_deck(parte, destino, numero, titulo_curso,
                                    extra, i if len(partes) > 1 else 0)
            mapa.append((doc.relative_to(curso).as_posix(), arquivo.name,
                         parte.n_slides))
            print("  %-46s -> %s (%d slides)"
                  % (doc.relative_to(curso).as_posix(), arquivo.name,
                     parte.n_slides))

    escrever_cobertura(destino, titulo_curso, mapa)
    print("%d lectures, %d slides, %d files covered."
          % (len(mapa), sum(m[2] for m in mapa), len({m[0] for m in mapa})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
