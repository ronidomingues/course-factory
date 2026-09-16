#!/usr/bin/env python3
"""publish-course.py — turns a Markdown course into a book and a slide deck,
in LaTeX and PDF, wearing the identity of the installed brand kit.

    python3 tools/publish-course.py courses/docker-2026-08-11
    python3 tools/publish-course.py docker --only slides
    python3 tools/publish-course.py docker --reset-config

What it does, in this order:

  1. reads the brand kit's `brand.env` and writes
     `97-publicacao/tema/brand-env.tex`;
  2. copies the theme (the `.sty` files and the logos in PDF) into
     `97-publicacao/tema/`;
  3. resolves the typefaces — installed on the system, or copied from the kit;
  4. writes `97-publicacao/livro/livro.json` and
     `97-publicacao/slides/slides.json` the first time (after that it keeps
     whatever is there);
  5. calls md2book to generate the LaTeX and compile the PDFs;
  6. sorts the result: `.tex` into `latex/`, `.pdf` into `pdf/`.

NON-NEGOTIABLE RULE: this program **never deletes or rewrites** course
material. It only creates and updates files inside `97-publicacao/`. The
course's Markdown is the source of truth; the book and the slides derive from
it.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common                                    # noqa: E402

BRAND = common.find_brand()                      # where the identity lives
PUBLICATION_DIR = "97-publicacao"

MESES = ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro")

# A course folder is <subject>-YYYY-MM-DD. The date suffix identifies the
# generation; the PDF name uses only the subject, so it stays readable.
RE_COURSE_DIR = re.compile(r"^(?P<slug>.+)-(?P<data>\d{4}-\d{2}-\d{2})$")

# Folder names that hold courses, newest convention first. Kept for the
# "is this course folder inside a courses root?" test; where the courses
# actually live is resolved by common.courses_root().
COURSE_ROOTS = (common.COURSES_DEFAULT, common.COURSES_LEGACY)


def partes_do_nome(nome: str):
    """Splits "docker-2026-08-11" into ("docker", "2026-08-11")."""
    m = RE_COURSE_DIR.match(nome)
    if m:
        return m.group("slug"), m.group("data")
    return nome, ""


def achar_curso(argumento: str, raiz=None) -> Path:
    """Accepts a path, a dated folder name, or just the subject ("docker").

    Without this, publishing a course would mean typing its generation date
    from memory.
    """
    alvo = Path(argumento).expanduser()
    if alvo.is_dir():
        return alvo.resolve()

    nome = alvo.name
    candidatas = ([alvo.parent] if alvo.parent != Path(".") else [])
    candidatas += ([raiz] if raiz else [])
    candidatas += [Path.cwd()] + [Path.cwd() / r for r in COURSE_ROOTS]
    bases, vistas = [], set()
    for base in candidatas:                  # a mesma pasta não se procura duas vezes
        chave = str(Path(base).resolve())
        if chave not in vistas:
            vistas.add(chave)
            bases.append(base)
    for base in bases:
        if not base.is_dir():
            continue
        direto = base / nome
        if direto.is_dir():
            return direto.resolve()
        candidatos = sorted(c for c in base.glob("%s-*" % nome)
                            if c.is_dir() and RE_COURSE_DIR.match(c.name))
        if candidatos:
            if len(candidatos) > 1:
                aviso("more than one course named %s; using the most recent: %s"
                      % (nome, candidatos[-1].name))
            return candidatos[-1].resolve()
    erro("course folder not found: %s\n"
         "  Looked in: %s\n"
         "  Courses live in %s — change it with COURSES_PATH at the repository\n"
         "  root, or pass --courses <path>."
         % (argumento, ", ".join(str(b) for b in bases),
            raiz or common.courses_root()))


# ------------------------------------------------------------------ helpers ---

def erro(msg, codigo=2):
    print("ERROR: %s" % msg, file=sys.stderr)
    sys.exit(codigo)


def aviso(msg):
    print("WARNING: %s" % msg, file=sys.stderr)


def ler_env(caminho: Path) -> dict:
    """Reads the brand's .env. One implementation, in common.py."""
    return common.read_env(caminho)


def fonte_instalada(familia: str) -> bool:
    """Is the family installed system-wide? Decides between using and shipping."""
    if not shutil.which("fc-list"):
        return False
    try:
        saida = subprocess.run(["fc-list", ":", "family"], capture_output=True,
                               text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    alvo = familia.replace(" ", "").lower()
    for linha in saida.splitlines():
        for nome in linha.split(","):
            if nome.strip().replace(" ", "").lower() == alvo:
                return True
    return False


def escapar_tex(texto: str) -> str:
    for de, para in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                     ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                     ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}")):
        texto = texto.replace(de, para)
    return texto


def data_extenso(d: date) -> str:
    return "%d de %s de %d" % (d.day, MESES[d.month - 1], d.year)


def data_extenso_iso(iso: str) -> str:
    """"2026-08-11" -> "11 de agosto de 2026". Empty stays empty."""
    if not iso:
        return ""
    try:
        ano, mes, dia = (int(x) for x in iso.split("-"))
        return "%d de %s de %d" % (dia, MESES[mes - 1], ano)
    except (ValueError, IndexError):
        return iso


# "X — mapa do curso": what follows the dash is a file label, not a book
# subtitle.
_ROTULO_MAPA = re.compile(r"^\s*(mapa|índice|indice|sumário|sumario|roteiro|"
                          r"map|index|outline)\b", re.I)
# Metadata lines at the top of the map: status, date, versions. Not subtitles.
_METADADO = re.compile(
    r"^\s*(\*\*)?\s*(n[íi]vel|data|status|[úu]ltima atualiza|vers|escrito em|"
    r"produzido em|verificado em|refer[êe]ncias? de vers|aviso|level|updated)",
    re.I)


def _limpar_marcacao(texto: str) -> str:
    texto = re.sub(r"\*\*(.+?)\*\*", r"\1", texto)
    texto = re.sub(r"[`*_]", "", texto)
    return re.sub(r"\s+", " ", texto).strip(" ·—–-")


def _encurtar(texto: str, limite: int = 200) -> str:
    """Cuts at the end of a sentence; blind truncation only as a last resort.

    A cover subtitle ending in "so that the..." is worse than a short one.
    """
    if len(texto) <= limite:
        return texto
    trecho = texto[:limite]
    for fim in (". ", "? ", "! ", "; "):
        pos = trecho.rfind(fim)
        if pos >= 60:
            return trecho[:pos + 1].strip()
    corte = trecho.rsplit(" ", 1)[0]
    return corte.rstrip(" ,;:·-") + "…"


def titulo_do_curso(curso: Path) -> tuple:
    """Title and subtitle, read from 00-MAPA.md (or from the folder name)."""
    mapa = curso / "00-MAPA.md"
    titulo = curso.name.replace("-", " ").strip().capitalize()
    subtitulo = ""
    if not mapa.is_file():
        return titulo, subtitulo

    linhas = mapa.read_text(encoding="utf-8").splitlines()
    inicio = 0
    for i, linha in enumerate(linhas):
        if linha.startswith("# "):
            bruto = linha[2:].strip()
            partes = re.split(r"\s+[—–]\s+", bruto, maxsplit=1)
            titulo = _limpar_marcacao(partes[0])
            if len(partes) > 1 and not _ROTULO_MAPA.match(partes[1]):
                subtitulo = _limpar_marcacao(partes[1])
            inicio = i + 1
            break

    if not subtitulo:
        # The first real paragraph — not metadata, not a table, not code.
        bloco = []
        for linha in linhas[inicio:inicio + 40]:
            crua = linha.strip()
            if crua.startswith(">"):
                crua = crua.lstrip("> ").strip()
            if not crua:
                if bloco:
                    break
                continue
            if (crua.startswith(("#", "|", "```", "---", "- ", "* ", "1."))
                    or _METADADO.match(crua)):
                if bloco:
                    break
                continue
            bloco.append(crua)
        subtitulo = _encurtar(_limpar_marcacao(" ".join(bloco)))

    titulo = titulo or curso.name
    return titulo, subtitulo


def contar_documentos(curso: Path) -> str:
    """"29 documentos · 12.400 linhas" — the real extent, for the cover."""
    documentos = [p for p in curso.rglob("*.md")
                  if PUBLICATION_DIR not in p.parts
                  and ".git" not in p.parts]
    linhas = 0
    for doc in documentos:
        try:
            linhas += len(doc.read_text(encoding="utf-8").splitlines())
        except OSError:
            pass
    return "%d documentos · %s linhas" % (
        len(documentos), "{:,}".format(linhas).replace(",", "."))


def mesclar(base: dict, extra: dict) -> dict:
    saida = json.loads(json.dumps(base))
    for chave, valor in extra.items():
        if isinstance(valor, dict) and isinstance(saida.get(chave), dict):
            saida[chave] = mesclar(saida[chave], valor)
        else:
            saida[chave] = valor
    return saida


def gravar_json(destino: Path, dados: dict, recriar: bool) -> bool:
    """Writes the config. True if written; False if preserved."""
    if destino.is_file() and not recriar:
        return False
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    return True


def achar_md2book(indicado=None) -> list:
    """How to call md2book on this machine (vendored copy first)."""
    cmd = common.find_md2book(indicado)
    if cmd:
        return cmd
    erro("md2book not found. It should be vendored at %s, or point the "
         "MD2BOOK variable at its folder, or pass --md2book <path>."
         % (common.tools_dir() / "md2book"))


def exigir_marca() -> None:
    """Refuses to publish with a brand kit that does not meet the contract."""
    if not BRAND.exists():
        erro("no brand kit found.\n"
             "  Expected at: %s\n"
             "  Install one (see docs/03-brand-kit.md) or pass --brand <path>.\n"
             "  The repository ships a neutral pre-mold at %s."
             % (common.tools_dir() / common.BRAND_SLOT,
                common.tools_dir() / common.BRAND_SLOT / common.BRAND_TEMPLATE))
    gaps = BRAND.missing()
    if gaps:
        erro("the brand kit at %s does not meet the contract.\n"
             "  Missing: %s\n"
             "  See docs/03-brand-kit.md." % (BRAND.root, ", ".join(gaps)))
    if BRAND.origin == "template":
        # The pre-mold publishes real PDFs, which is the point — but material
        # that leaves this machine wearing it is signed by nobody. Saying so
        # once per publication is cheaper than discovering it in a reader's
        # inbox.
        aviso("publishing with the neutral pre-mold — this material is signed "
              "by nobody.\n"
              "  Install your own kit: python3 tools/sync-brand.py "
              "--from-template\n"
              "  See docs/03-brand-kit.md.")


# ------------------------------------------------------------------- steps ---

def _caminho_relativo(destino: Path, partida: Path) -> str:
    """Path from `partida` to `destino`, in slashes, for fontspec."""
    return Path(os.path.relpath(destino, partida)).as_posix()


def preparar_tema(curso: Path, env: dict, meta: dict, politica: str) -> dict:
    """Copies the theme into the course and returns the font configuration.

    The theme is copied rather than referenced by absolute path because the PDF
    has to stay rebuildable on another machine and a year from now — including
    by someone who does not have the brand repository.
    """
    tema = curso / PUBLICATION_DIR / "tema"
    (tema / "assets").mkdir(parents=True, exist_ok=True)

    for sty in sorted(BRAND.latex.glob("*.sty")):
        shutil.copyfile(sty, tema / sty.name)
    if BRAND.assets.is_dir():
        for logo in sorted(BRAND.assets.glob("*.pdf")):
            shutil.copyfile(logo, tema / "assets" / logo.name)

    escrever_ambiente(tema / "brand-env.tex", env, meta)
    return resolver_fontes(curso, politica)


def resolver_fontes(curso: Path, politica: str) -> dict:
    """Decides where the brand typefaces come from on this machine.

    Three routes, and the choice matters: an installed font takes no repository
    space but vanishes when the course travels; a copied font travels along but
    weighs a few MB per copy. The `auto` default uses what is installed and,
    when nothing is, keeps **one** copy for every course in the repository —
    which is where the arithmetic works out.

    A brand kit that ships no font files gets `{}`: whatever its
    `book.base.json` declares is what the LaTeX will ask for.
    """
    tema = curso / PUBLICATION_DIR / "tema"
    spec = BRAND.font_spec()
    families = spec.get("families", {})

    if not families:
        print("  fonts: as declared by the brand kit (no files shipped)")
        _limpar_fontes_locais(tema)
        return {}

    sistema = dict(spec.get("system", {}))
    checar = spec.get("check") or [v for k, v in sistema.items()
                                   if k != "simbolos"]
    instaladas = all(fonte_instalada(f) for f in checar)

    if politica == "system" or (politica == "auto" and instaladas):
        if not instaladas:
            aviso("--fonts system, but %s are not installed: LaTeX will fail "
                  "or substitute the typeface." % ", ".join(checar))
        print("  fonts: the brand's, installed system-wide")
        _limpar_fontes_locais(tema)
        return sistema

    fontes_kit = BRAND.fonts
    if not fontes_kit.is_dir():
        aviso("brand fonts not found at %s — the material will come out in "
              "DejaVu, off-identity." % fontes_kit)
        return {"texto": "DejaVu Serif", "titulo": "DejaVu Sans",
                "mono": "DejaVu Sans Mono", "simbolos": "DejaVu Sans"}

    raiz_repo = raiz_do_repositorio(curso)
    embarcado = _dentro_de(fontes_kit, raiz_repo)

    if politica == "course":
        destino = tema / "fontes"
        onde = "inside the course itself (portable folder)"
    elif embarcado:
        # The kit lives inside the course repository: the fonts already travel
        # with the material. Copying again would be a second 3 MB truth.
        destino = fontes_kit
        onde = "the vendored kit's (%s)" % fontes_kit.name
        _limpar_fontes_locais(tema)
    else:                                   # "repo", and "auto" with no install
        destino = raiz_repo / ".course-factory-fonts"
        onde = "one copy for the whole repository"
        _limpar_fontes_locais(tema)

    if destino != fontes_kit:
        destino.mkdir(parents=True, exist_ok=True)
        for familia in families.values():
            for arquivo in familia.get("files", []):
                origem = fontes_kit / arquivo
                if origem.is_file():
                    shutil.copyfile(origem, destino / arquivo)
        for licenca in list(fontes_kit.glob("LICENCA-*.txt")) + \
                list(fontes_kit.glob("LICENSE-*.txt")):
            shutil.copyfile(licenca, destino / licenca.name)

    # The path is relative to the folder where LaTeX compiles, and the two
    # compile folders (livro/latex and slides/latex) sit at the same depth.
    referencia = curso / PUBLICATION_DIR / "livro" / "latex"
    print("  fonts: %s" % onde)
    embedded = dict(spec.get("embedded", sistema))
    config = {
        "diretorio": _caminho_relativo(destino, referencia),
        "extensao": spec.get("extension", ".ttf"),
    }
    config.update(embedded)
    for papel in ("texto", "titulo", "mono"):
        familia = families.get(embedded.get(papel, ""))
        if familia and familia.get("faces"):
            config["%s_faces" % papel] = familia["faces"]
    return config


def raiz_do_repositorio(curso: Path) -> Path:
    """The folder that holds every course — home of the single font copy."""
    if curso.parent.name in COURSE_ROOTS:
        return curso.parent.parent
    return curso.parent


def _dentro_de(alvo: Path, raiz: Path) -> bool:
    """Is `alvo` under `raiz`? (without requiring Python 3.9's is_relative_to)"""
    try:
        alvo.resolve().relative_to(raiz.resolve())
        return True
    except ValueError:
        return False


def _limpar_fontes_locais(tema: Path) -> None:
    """Removes font copies this same program left inside the course.

    Touches only what it generates: `97-publicacao/tema/fontes`. Never course
    material."""
    pasta = tema / "fontes"
    if pasta.is_dir():
        shutil.rmtree(pasta)


# The metadata macros a brand kit may rely on. Kept in one place because the
# .sty files and this list are two halves of the same contract.
MACROS_CURSO = ["cftitle", "cfsubtitle", "cfsubject", "cfversion", "cfdate",
                "cfproduced", "cfyear", "cflevel", "cfpiece", "cfadvisor",
                "cfagent", "cfaimodel", "cflicense", "cfrepo", "cfextent",
                "cfnote", "cfcourse", "cflecture"]


def cores_latex(env: dict) -> list:
    """The `\\definecolor` lines for every colour declared in brand.env.

    They land in `brand-env.tex`, which each `.sty` inputs **after** its own
    defaults — so what the kit's `brand.env` says wins, and recolouring a brand
    is editing one file instead of hunting fourteen `\\definecolor` across two
    style files and two JSONs. A kit that declares none keeps the `.sty`
    defaults, unchanged.
    """
    cores = common.brand_colors(env)
    if not cores:
        return []
    for chave, bruto in sorted(env.items()):
        if chave.startswith(common.COLOR_PREFIX) and not common.read_hex(bruto):
            aviso("%s is not a six-digit hex colour (%r) — ignored."
                  % (chave, bruto))
    linhas = ["%% ----------------------------------------------- brand colours --",
              "%% Declared in brand.env; they override the .sty defaults."]
    linhas += [r"\definecolor{%s}{HTML}{%s}" % (nome, valor)
               for nome, valor in sorted(cores.items())]
    return linhas


def escrever_ambiente(destino: Path, env: dict, meta: dict) -> None:
    """Translates the brand's .env and the course data into LaTeX macros."""
    def d(macro, valor):
        return r"\def\%s{%s}" % (macro, escapar_tex(str(valor or "")))

    # The same file is read by the book and by the slides, which define
    # different sets of macros. \providecommand covers the difference: whoever
    # really defined one keeps it, and the rest become ignored fields — instead
    # of leaking the value as text in the middle of the document.
    linhas = [
        "%% Generated by tools/publish-course.py — DO NOT EDIT.",
        "%% Brand data: brand.env of the installed brand kit.",
        "%% Course data: the course folder and the command line.",
        "%% ---------------------------------------------------------------",
        "%% Fields the current document does not know about become no-ops:",
    ] + [r"\providecommand{\%s}[1]{}" % m for m in MACROS_CURSO] + [
        "%% ---------------------------------------------------------------",
        d("cfBrand", env.get("BRAND_NAME", "")),
        d("cfBrandLower", env.get("BRAND_NAME_LOWER", "")),
        d("cfTagline", env.get("BRAND_TAGLINE", "")),
        d("cfDescriptor", env.get("BRAND_DESCRIPTOR", "")),
        d("cfOwner", env.get("BRAND_OWNER", "")),
        d("cfAuthor", env.get("BRAND_AUTHOR", "")),
        d("cfEmail", env.get("BRAND_EMAIL", "")),
        d("cfSite", env.get("BRAND_SITE", "")),
        d("cfSiteURL", env.get("BRAND_SITE_URL", "")),
        # The prompt is raw LaTeX by design: it is a graphic element, not text.
        r"\def\cfPrompt{%s}" % (env.get("BRAND_PROMPT", "") or r"\$"),
    ] + cores_latex(env) + [
        "%% ------------------------------------------------ course data ----",
        r"\cftitle{%s}" % escapar_tex(meta["titulo"]),
        r"\cfsubtitle{%s}" % escapar_tex(meta["subtitulo"]),
        r"\cfsubject{%s}" % escapar_tex(meta["assunto"]),
        r"\cfversion{%s}" % escapar_tex(meta["versao"]),
        r"\cfdate{%s}" % escapar_tex(meta["data"]),
        r"\cfproduced{%s}" % escapar_tex(meta.get("data_producao", "")),
        r"\cfyear{%s}" % escapar_tex(meta["ano"]),
        r"\cflevel{%s}" % escapar_tex(meta["nivel"]),
        r"\cfpiece{%s}" % escapar_tex(meta["peca"]),
        r"\cfadvisor{%s}" % escapar_tex(meta["orientador"]),
        r"\cfagent{%s}" % escapar_tex(meta["agente"]),
        r"\cfaimodel{%s}" % escapar_tex(meta["modelo"]),
        r"\cflicense{%s}" % escapar_tex(meta["licenca"]),
        r"\cfrepo{%s}" % escapar_tex(meta["repositorio"]),
        r"\cfextent{%s}" % escapar_tex(meta["documentos"]),
        r"\cfnote{%s}" % escapar_tex(meta["nota"]),
        "%% The slides use the same data under another name.",
        r"\cfcourse{%s}" % escapar_tex(meta["titulo"]),
        r"\endinput",
        "",
    ]
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(linhas), encoding="utf-8")


def publicar_livro(curso: Path, cmd_md2book: list, meta: dict,
                   config_fontes: dict, cores: dict, recriar: bool,
                   compilar: bool) -> Path:
    """Generates the book's LaTeX and compiles the PDF."""
    base = json.loads((BRAND.templates / "book.base.json").read_text("utf-8"))
    base.pop("_comentario", None)
    destino = curso / PUBLICATION_DIR / "livro"
    (destino / "pdf").mkdir(parents=True, exist_ok=True)

    slug = meta["slug"]
    config = mesclar(base, {
        "titulo": meta["titulo"],
        "subtitulo": meta["subtitulo"],
        "autor": meta["orientador"],
        "ano": meta["ano"],
        "nome_arquivo": "%s-livro" % slug,
        "nota_capa": meta["nota"],
        "fontes": mesclar(base.get("fontes", {}), config_fontes),
    })
    config.update(cores)          # brand.env wins over the kit's base JSON
    if gravar_json(destino / "livro.json", config, recriar):
        print("  livro.json written")
    else:
        print("  livro.json preserved (use --reset-config to rewrite)")

    comando = cmd_md2book + ["livro" if compilar else "tex",
                             "-c", str(destino / "livro.json"),
                             "--ambiente", "ignorar"]
    proc = subprocess.run(comando)
    if proc.returncode != 0:
        aviso("md2book exited with code %d on the book." % proc.returncode)
        return None
    if not compilar:
        return None

    gerado = destino / "latex" / ("%s-livro.pdf" % slug)
    if not gerado.is_file():
        aviso("the book PDF was not produced.")
        return None
    final = destino / "pdf" / gerado.name
    shutil.move(str(gerado), str(final))
    limpar_intermediarios(destino / "latex")
    return final


def publicar_slides(curso: Path, cmd_md2book: list, meta: dict,
                    config_fontes: dict, cores: dict, recriar: bool,
                    compilar: bool):
    """Generates the Beamer decks and compiles one PDF per lecture, plus the
    single combined PDF."""
    base = json.loads((BRAND.templates / "slides.base.json").read_text("utf-8"))
    base.pop("_comentario", None)
    destino = curso / PUBLICATION_DIR / "slides"
    (destino / "md").mkdir(parents=True, exist_ok=True)
    (destino / "pdf").mkdir(parents=True, exist_ok=True)

    slug = meta["slug"]
    fontes = dict(config_fontes)
    config = mesclar(base, {
        "curso": meta["titulo"],
        "subtitulo": meta["subtitulo"],
        "autor": meta["orientador"],
        "data": meta["data"],
        "pdf_unico": "%s-slides-completo.pdf" % slug,
        "fontes": mesclar(base.get("fontes", {}), fontes),
    })
    config.update(cores)          # brand.env wins over the kit's base JSON
    if gravar_json(destino / "slides.json", config, recriar):
        print("  slides.json written")
    else:
        print("  slides.json preserved (use --reset-config to rewrite)")

    escrever_guia_das_aulas(destino / "md", meta)
    decks = sorted(p for p in (destino / "md").glob("*.md")
                   if p.name not in ("README.md", "LEIA-ME.md"))
    if not decks:
        print("  no lectures written yet: put the decks in %s"
              % (destino / "md"))
        print("  deck template: %s" % common.example_deck())
        return []

    remover_aulas_fantasma(destino, decks)
    comando = cmd_md2book + ["slides" if compilar else "slides-tex",
                             "-c", str(destino / "slides.json")]
    proc = subprocess.run(comando)
    if proc.returncode != 0:
        aviso("md2book exited with code %d on the slides." % proc.returncode)
    limpar_intermediarios(destino / "latex")
    unico = config["pdf_unico"]
    # The PDF that bundles every lecture is not a lecture: counting it would
    # inflate the number in the report and in the course's LEIA-ME.
    return sorted(p for p in (destino / "pdf").glob("*.pdf") if p.name != unico)


def escrever_guia_das_aulas(pasta: Path, meta: dict) -> None:
    """Leaves the deck format next to where the lectures will be written.

    Whoever writes the lecture opens this folder, not the brand repository.
    This guide is course-facing material, so it is written in the language of
    the course."""
    destino = pasta / "LEIA-ME.md"
    if destino.is_file():
        return
    pasta.mkdir(parents=True, exist_ok=True)
    destino.write_text("""# Aulas de %s

Um arquivo por aula, nomeado `aula-NN-<tema>.md`. **Escreva os slides — não copie o
capítulo para dentro deles.** Se o slide tem parágrafo, está errado.

## A gramática inteira

| Marca | Vira |
|---|---|
| bloco `---` no topo, `chave: valor` | metadados (`aula`, `curso`, `subtitulo`, `duracao`) |
| `#` | título da aula — a capa |
| `##` | parte da aula — tela de transição |
| `###` | **um slide** |
| `####` e mais fundo | destaque em negrito dentro do slide |
| bloco de código da linguagem `notas` | roteiro do professor, invisível na projeção |
| `---` dentro de um slide | continua o slide na tela seguinte, com `(cont.)` |

Listas, tabelas, código, citações e imagens funcionam como em qualquer arquivo do curso.

## A régua

| Medida | Valor |
|---|---|
| Slides por aula | 12 a 25 |
| Linhas por slide | até 10 (o gerador avisa a partir de 12) |
| Ideias por slide | uma — se o título tem "e", são dois slides |
| Duração alvo | 30 a 50 min de fala |

## Cobertura

Toda aula sai de algum arquivo do curso, e **todo arquivo do curso aparece em alguma
aula**. Mantenha a tabela abaixo enquanto escreve:

| Arquivo do curso | Aula |
|---|---|
| ... | ... |

## Gerar os PDFs

```bash
python3 tools/publish-course.py %s --only slides
```

Gabarito de formato: `tools/example/aula-00-modelo.md`.
""" % (meta["titulo"], meta["assunto"]), encoding="utf-8")


def remover_aulas_fantasma(destino: Path, decks) -> None:
    """Deletes .tex and .pdf of lectures that no longer exist.

    Renaming or regrouping decks would leave the old lecture's PDF behind,
    looking like valid material. Whatever lost its source goes — and only
    that."""
    vivos = {d.stem for d in decks}
    for pasta, extensao in ((destino / "latex", "*.tex"),
                            (destino / "pdf", "*.pdf")):
        if not pasta.is_dir():
            continue
        for arquivo in pasta.glob(extensao):
            if arquivo.stem.startswith("aula-") and arquivo.stem not in vivos:
                arquivo.unlink()


def limpar_intermediarios(pasta: Path) -> None:
    """Strips compilation by-products from the LaTeX folder.

    The `.pdf` files are on the list on purpose: the PDF that counts already
    moved to `pdf/`, and leaving the copy here would double the repository's
    weight at every publication. The `.tex` files stay — they are deliverables,
    not litter."""
    if not pasta.is_dir():
        return
    for extensao in ("*.aux", "*.log", "*.nav", "*.out", "*.snm", "*.toc",
                     "*.fls", "*.fdb_latexmk", "*.vrb", "*.xdv", "*.lof",
                     "*.lot", "*.bbl", "*.blg", "*.idx", "*.pdf"):
        for lixo in pasta.glob(extensao):
            lixo.unlink()


def escrever_leiame(curso: Path, meta: dict, livro, decks) -> None:
    """Explains, inside the course, what each folder is and how to redo it."""
    base = curso / PUBLICATION_DIR
    # Publishing only one of the pieces must not make the other vanish from the
    # report: whatever is already on disk still counts.
    if livro is None:
        existentes = sorted((base / "livro" / "pdf").glob("*.pdf"))
        livro = existentes[0] if existentes else None
    if not decks:
        unico = "%s-slides-completo.pdf" % partes_do_nome(curso.name)[0]
        decks = sorted(p for p in (base / "slides" / "pdf").glob("*.pdf")
                       if p.name != unico)
    destino = base / "LEIA-ME.md"
    linhas = [
        "# Publicação — %s" % meta["titulo"],
        "",
        "> **Esta pasta é gerada.** A fonte da verdade é o Markdown do curso,",
        "> um nível acima. Nada aqui substitui aquilo, e nada lá é apagado por",
        "> causa daqui. Editar um `.tex` à mão funciona até a próxima publicação.",
        "",
        "Gerado em %s · v%s · %s" % (meta["data"], meta["versao"],
                                     meta["documentos"]),
        "",
        "| Pasta | O que tem dentro |",
        "|---|---|",
        "| `livro/latex/` | O livro em LaTeX: `main.tex` e um `.tex` por capítulo. |",
        "| `livro/pdf/` | O livro em PDF, pronto para ler, imprimir ou enviar. |",
        "| `slides/md/` | A fonte das aulas: um arquivo Markdown por aula. |",
        "| `slides/latex/` | Cada aula em Beamer (`.tex`). |",
        "| `slides/pdf/` | Um PDF por aula, mais o PDF único com todas. |",
        "| `tema/` | A identidade aplicada: `.sty`, logos e fontes. |",
        "",
        "## Refazer",
        "",
        "```bash",
        "python3 tools/publish-course.py %s" % meta["slug"],
        "```",
        "",
        "Só o livro: `--only book`. Só as aulas: `--only slides`.",
        "",
        "## Créditos",
        "",
    ]
    if meta["orientador"]:
        linhas.append("- **Autor e orientador:** %s" % meta["orientador"])
    linhas += [
        "- **Escrita e materialização:** %s%s" % (
            meta["agente"], " (%s)" % meta["modelo"] if meta["modelo"] else ""),
        "- **Publicação:** %s%s" % (
            meta["marca"], " — %s" % meta["tagline"] if meta["tagline"] else ""),
        "",
        "## Estado desta publicação",
        "",
        "- Livro: %s" % ("`%s`" % livro.name if livro else "não gerado"),
        "- Aulas em PDF: %d" % len(decks),
        "",
    ]
    destino.write_text("\n".join(linhas), encoding="utf-8")
    return livro, decks


# -------------------------------------------------------------------- main ---

def diagnostico(courses=None) -> int:
    """Says, in one screen, whether this machine can publish a course alone."""
    import shutil as sh
    print(BRAND.report())
    raiz = common.courses_root(courses)
    print("Courses  : %s (%s)%s"
          % (raiz, common.courses_origin(courses),
             "" if raiz.is_dir() else "  — folder does not exist yet"))
    print()
    md2book = common.find_md2book()
    linhas = [
        ("md2book", bool(md2book), " ".join(md2book) if md2book else
         "missing — no conversion without it"),
        ("brand kit", BRAND.exists() and not BRAND.missing(),
         "%s (%s)" % (BRAND.root, BRAND.origin) if BRAND.exists() else
         "missing — install one, see docs/03-brand-kit.md"),
        ("brand fonts", BRAND.has_fonts(),
         str(BRAND.fonts) if BRAND.has_fonts() else
         "kit ships none — it uses typefaces installed on the machine"),
        ("xelatex", bool(sh.which("xelatex")),
         sh.which("xelatex") or "missing — you get the .tex, not the PDF"),
        ("latexmk", bool(sh.which("latexmk")),
         sh.which("latexmk") or "missing — md2book drives the engine directly"),
        ("pdfunite/gs", bool(sh.which("pdfunite") or sh.which("gs")),
         sh.which("pdfunite") or sh.which("gs") or
         "missing — the lectures stay as separate PDFs"),
    ]
    for nome, ok, detalhe in linhas:
        print("  %-14s %-8s %s" % (nome, "ok" if ok else "MISSING", detalhe))

    essenciais = [linhas[0][1], linhas[1][1], sh.which("xelatex") is not None]
    print()
    if all(essenciais):
        print("This machine can publish a course on its own.")
        if not BRAND.has_fonts():
            print("The kit ships no font files; make sure the ones it declares "
                  "are installed.")
        return 0
    print("Something essential is missing. On Debian/Ubuntu:")
    print("  sudo apt install texlive-xetex texlive-latex-extra "
          "texlive-lang-portuguese latexmk poppler-utils")
    return 1


def main(argv=None) -> int:
    global BRAND
    p = argparse.ArgumentParser(
        description="Publishes a Markdown course as a book and slides "
                    "(LaTeX + PDF), wearing the installed brand kit.")
    p.add_argument("course", nargs="?", default="",
                   help="course folder (the one with 00-MAPA.md)")
    p.add_argument("--only", choices=["all", "book", "slides"],
                   default="all", help="what to publish (default: all)")
    p.add_argument("--brand", default="",
                   help="path to the brand kit (default: "
                        "tools/course-factory-brand, then its template/)")
    p.add_argument("--courses", default="",
                   help="folder holding the courses (default: the COURSES_PATH "
                        "pointer, else courses/)")
    p.add_argument("--md2book", help="path to md2book (repo or md2book.py)")
    p.add_argument("--doc-version", default="1.0",
                   help="version label of this publication")
    p.add_argument("--agent", default="Claude Code (Anthropic)",
                   help="the AI agent that wrote the material")
    p.add_argument("--ai-model", default="", help="model the agent ran on")
    p.add_argument("--advisor", default="",
                   help="author and advisor (default: BRAND_OWNER from brand.env)")
    p.add_argument("--license", default="",
                   help="licence line printed on the credits page")
    p.add_argument("--repo", default="", help="source repository, for credits")
    p.add_argument("--note", default="", help="extra line on cover/credits")
    p.add_argument("--level", default="",
                   help="level line printed on the cover "
                        "(default: BRAND_COURSE_LEVEL from brand.env)")
    p.add_argument("--reset-config", action="store_true",
                   help="rewrites the course's livro.json and slides.json")
    p.add_argument("--fonts", choices=["auto", "system", "repo", "course"],
                   default="auto",
                   help="where the brand typefaces come from: auto (use the "
                        "installed ones, else keep one copy in the repository); "
                        "system; repo (one copy for every course); "
                        "course (copy inside the course, portable folder)")
    p.add_argument("--no-pdf", action="store_true",
                   help="generate the LaTeX only, without compiling")
    p.add_argument("--doctor", action="store_true",
                   help="show what this machine has and lacks, then exit")
    args = p.parse_args(argv)

    if args.brand:
        BRAND = common.find_brand(args.brand)
    if args.doctor:
        return diagnostico(args.courses)
    if not args.course:
        p.error("name the course (or use --doctor)")
    exigir_marca()

    curso = achar_curso(args.course, common.courses_root(args.courses))
    slug, data_pasta = partes_do_nome(curso.name)
    if not (curso / "00-MAPA.md").is_file():
        aviso("%s has no 00-MAPA.md — the title will come from the folder name."
              % curso.name)

    env = ler_env(BRAND.env)
    titulo, subtitulo = titulo_do_curso(curso)
    hoje = date.today()
    meta = {
        "titulo": titulo,
        "subtitulo": subtitulo,
        "assunto": slug,
        "slug": slug,
        "pasta": curso.name,
        "data_producao": data_extenso_iso(data_pasta),
        "versao": args.doc_version,
        "data": data_extenso(hoje),
        "ano": str(hoje.year),
        "nivel": args.level or env.get("BRAND_COURSE_LEVEL", ""),
        "peca": "Livro do curso",
        "orientador": args.advisor or env.get("BRAND_OWNER", ""),
        "agente": args.agent,
        "modelo": args.ai_model,
        "licenca": args.license or env.get("BRAND_COURSE_LICENSE", ""),
        "repositorio": args.repo,
        "documentos": contar_documentos(curso),
        "nota": args.note,
        "marca": env.get("BRAND_NAME", ""),
        "tagline": env.get("BRAND_TAGLINE", ""),
    }

    print("Course: %s" % curso)
    print("Title : %s" % meta["titulo"])
    print("Brand : %s (%s)" % (BRAND.root.name, BRAND.origin))
    print("Preparing the brand theme...")
    config_fontes = preparar_tema(curso, env, meta, args.fonts)

    cmd = achar_md2book(args.md2book)
    livro, decks = None, []

    if args.only in ("all", "book"):
        print("\n== Book ==")
        livro = publicar_livro(curso, cmd, meta, config_fontes,
                               common.converter_colors(env, "BOOK"),
                               args.reset_config, not args.no_pdf)
    if args.only in ("all", "slides"):
        print("\n== Slides ==")
        decks = publicar_slides(curso, cmd, meta, config_fontes,
                                common.converter_colors(env, "SLIDES"),
                                args.reset_config, not args.no_pdf)

    livro, decks = escrever_leiame(curso, meta, livro, decks)

    print("\n== Result ==")
    print("Book   : %s" % (livro if livro else "not generated"))
    print("Lectures: %d PDF(s)" % len(decks))
    print("Theme  : %s" % (curso / PUBLICATION_DIR / "tema"))
    return 0 if (livro or decks or args.no_pdf) else 1


if __name__ == "__main__":
    sys.exit(main())
