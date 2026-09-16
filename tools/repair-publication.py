#!/usr/bin/env python3
"""repair-publication.py — completes whatever a batch publication left out.

    python3 tools/repair-publication.py
    python3 tools/repair-publication.py courses --check   # report only

In a run of dozens of courses some compilation always falls over: a control
character inside a code block, tight memory, a LaTeX counter that overflowed.
Republishing everything because of that costs hours. This program looks at what
is **missing** and redoes only that:

  * book with no PDF        -> republishes the course book;
  * deck with no PDF        -> compiles that `.tex` and publishes the PDF;
  * stale combined PDF      -> merges the lectures again.

Nothing here touches course material.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PUBLISH = TOOLS / "publish-course.py"
PASTA_PUBLICACAO = "97-publicacao"


def paginas(pdf: Path) -> int:
    if not pdf.is_file():
        return 0
    saida = subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                           text=True).stdout
    for linha in saida.splitlines():
        if linha.startswith("Pages:"):
            return int(linha.split()[1])
    return 0


def diagnosticar(curso: Path) -> dict:
    pub = curso / PASTA_PUBLICACAO
    decks = sorted((pub / "slides" / "md").glob("aula-*.md"))
    pdfs = {p.stem for p in (pub / "slides" / "pdf").glob("aula-*.pdf")}
    return {
        "curso": curso,
        "livro": bool(list((pub / "livro" / "pdf").glob("*.pdf"))),
        "decks": decks,
        "faltando": [d for d in decks if d.stem not in pdfs],
    }


def compilar_deck(curso: Path, deck: Path, verboso=True) -> bool:
    """Compiles a lecture `.tex` that was already generated, and publishes the PDF."""
    pub = curso / PASTA_PUBLICACAO
    tex = pub / "slides" / "latex" / (deck.stem + ".tex")
    if not tex.is_file():
        return False
    env = dict(os.environ)
    tema = (pub / "tema").resolve()
    env["TEXINPUTS"] = "%s:%s" % (tema, env.get("TEXINPUTS", ""))
    for _ in range(2):                      # two passes: total slide count
        proc = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-file-line-error",
             tex.name],
            cwd=tex.parent, capture_output=True, text=True, env=env)
    gerado = tex.with_suffix(".pdf")
    if not gerado.is_file():
        if verboso:
            erro = [l for l in proc.stdout.splitlines() if l.startswith("!")]
            print("      failed: %s" % (erro[:1] or ["reason is in the .log"])[0])
        return False
    destino = pub / "slides" / "pdf" / gerado.name
    shutil.copyfile(gerado, destino)
    for lixo in ("aux", "log", "nav", "out", "snm", "toc", "vrb", "xdv", "pdf"):
        alvo = tex.with_suffix("." + lixo)
        if alvo.is_file():
            alvo.unlink()
    return True


def unir(curso: Path, slug: str) -> bool:
    pub = curso / PASTA_PUBLICACAO / "slides" / "pdf"
    aulas = sorted(p for p in pub.glob("aula-*.pdf"))
    if len(aulas) < 2:
        return False
    destino = pub / ("%s-slides-completo.pdf" % slug)
    if shutil.which("pdfunite"):
        cmd = ["pdfunite"] + [str(a) for a in aulas] + [str(destino)]
    elif shutil.which("gs"):
        cmd = ["gs", "-dBATCH", "-dNOPAUSE", "-q", "-sDEVICE=pdfwrite",
               "-sOutputFile=%s" % destino] + [str(a) for a in aulas]
    else:
        return False
    return subprocess.run(cmd, capture_output=True).returncode == 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Completes a batch publication.")
    p.add_argument("folder", nargs="?", default="courses",
                   help="folder holding the courses (default: courses)")
    p.add_argument("--check", action="store_true", help="report only")
    p.add_argument("--brand", default="", help="path to the brand kit")
    p.add_argument("--ai-model", default="")
    p.add_argument("--agent", default="Claude Code (Anthropic)")
    args = p.parse_args(argv)

    raiz = Path(args.folder).expanduser().resolve()
    cursos = sorted(c for c in raiz.iterdir()
                    if c.is_dir() and not c.name.startswith("."))

    pendentes = [diagnosticar(c) for c in cursos]
    pendentes = [d for d in pendentes if not d["livro"] or d["faltando"]]

    if not pendentes:
        print("Nothing to repair: every course has its book and all lectures.")
        return 0

    print("Courses to repair: %d" % len(pendentes))
    for d in pendentes:
        print("  %-50s %s%s" % (
            d["curso"].name,
            "book missing" if not d["livro"] else "book ok",
            " · %d lecture(s) with no PDF" % len(d["faltando"]) if d["faltando"] else ""))
    if args.check:
        return 0

    reparados_livro = reparados_aula = 0
    for d in pendentes:
        curso = d["curso"]
        print("\n== %s ==" % curso.name)
        if not d["livro"]:
            print("  republishing the book...")
            # An interrupted compilation leaves a truncated .aux, and LaTeX
            # dies on the next run with "File ended while scanning use of
            # \\@writefile". Before redoing it, wipe the previous attempt.
            for lixo in (curso / PASTA_PUBLICACAO / "livro" / "latex").glob("main.*"):
                if lixo.suffix in (".aux", ".toc", ".out", ".log", ".fls",
                                   ".fdb_latexmk", ".xdv", ".pdf", ".lof",
                                   ".lot", ".idx"):
                    lixo.unlink()
            cmd = [sys.executable, str(PUBLISH), str(curso),
                   "--only", "book", "--agent", args.agent]
            if args.ai_model:
                cmd += ["--ai-model", args.ai_model]
            if args.brand:
                cmd += ["--brand", args.brand]
            subprocess.run(cmd, capture_output=True, text=True)
            if list((curso / PASTA_PUBLICACAO / "livro" / "pdf").glob("*.pdf")):
                reparados_livro += 1
                print("  book done.")
            else:
                print("  book STILL failed — check the course's main.log.")
        for deck in d["faltando"]:
            print("  compiling %s..." % deck.name)
            if compilar_deck(curso, deck):
                reparados_aula += 1
        if d["faltando"]:
            slug = curso.name
            import re
            m = re.match(r"^(.+)-\d{4}-\d{2}-\d{2}$", curso.name)
            if m:
                slug = m.group(1)
            unir(curso, slug)

    print("\n== Repair summary ==")
    print("Books recovered   : %d" % reparados_livro)
    print("Lectures recovered: %d" % reparados_aula)
    return 0


if __name__ == "__main__":
    sys.exit(main())
