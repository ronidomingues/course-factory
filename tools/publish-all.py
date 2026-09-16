#!/usr/bin/env python3
"""publish-all.py — publishes EVERY course in a folder, in parallel.

    python3 tools/publish-all.py
    python3 tools/publish-all.py courses --jobs 6 --only book
    python3 tools/publish-all.py courses --skip-done

For each course: drafts the lectures (when none exist yet), generates the book
and the slides in LaTeX, compiles the PDFs and sorts the result. At the end it
writes a JSON report with pages, lectures and failures — that report is what
feeds the catalogue update.

Parallelism: one course per process. The shared fonts are seeded BEFORE the
pool opens — two processes copying the same font file at once would leave a
half-written file for a third one to read.
"""

import argparse
import concurrent.futures as futuros
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common                                    # noqa: E402

TOOLS = Path(__file__).resolve().parent
PUBLISH = TOOLS / "publish-course.py"
GENERATE = TOOLS / "generate-lectures.py"
RE_CURSO = re.compile(r"^(?P<slug>.+)-(?P<data>\d{4}-\d{2}-\d{2})$")


def paginas(pdf: Path) -> int:
    if not pdf or not pdf.is_file():
        return 0
    saida = subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                           text=True).stdout
    for linha in saida.splitlines():
        if linha.startswith("Pages:"):
            return int(linha.split()[1])
    return 0


def publicar_um(curso: Path, args) -> dict:
    """Publica um curso e devolve o que saiu dele."""
    inicio = time.time()
    slug = RE_CURSO.match(curso.name).group("slug") if RE_CURSO.match(curso.name) \
        else curso.name
    resultado = {"curso": curso.name, "slug": slug, "erros": []}
    pub = curso / "97-publicacao"

    # ---------------------------------------------------------- aulas ------
    if args.only in ("all", "slides"):
        decks = list((pub / "slides" / "md").glob("aula-*.md"))
        if not decks or args.force_lectures:
            cmd = [sys.executable, str(GENERATE), str(curso)]
            if args.force_lectures:
                cmd.append("--force")
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                resultado["erros"].append("generate-lectures: %s"
                                          % r.stderr.strip()[:300])

    # ------------------------------------------------------ publicação -----
    cmd = [sys.executable, str(PUBLISH), str(curso),
           "--only", args.only,
           "--agent", args.agent,
           "--doc-version", args.doc_version]
    if args.ai_model:
        cmd += ["--ai-model", args.ai_model]
    if args.brand:
        cmd += ["--brand", args.brand]
    if args.reset_config:
        cmd.append("--reset-config")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        resultado["erros"].append("publish-course: exit code %d" % r.returncode)
    resultado["avisos"] = [l for l in r.stderr.splitlines()
                           if l.startswith("WARNING")][:200]

    # ---------------------------------------------------------- balanço ----
    livros = sorted((pub / "livro" / "pdf").glob("*.pdf"))
    livro = livros[0] if livros else None
    unico = "%s-slides-completo.pdf" % slug
    aulas = sorted(p for p in (pub / "slides" / "pdf").glob("*.pdf")
                   if p.name != unico)
    resultado.update({
        "livro": livro.name if livro else "",
        "paginas": paginas(livro),
        "aulas": len(aulas),
        "slides": sum(paginas(a) for a in aulas),
        "pdf_unico": unico if (pub / "slides" / "pdf" / unico).is_file() else "",
        "documentos": len([m for m in curso.rglob("*.md")
                           if "97-publicacao" not in m.parts]),
        "segundos": round(time.time() - inicio, 1),
    })
    return resultado


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Publishes every course in a folder, in parallel.")
    p.add_argument("folder", nargs="?", default="",
                   help="folder holding the courses (default: the COURSES_PATH "
                        "pointer, else courses/)")
    p.add_argument("--jobs", type=int, default=4, help="courses in parallel")
    p.add_argument("--only", choices=["all", "book", "slides"], default="all")
    p.add_argument("--brand", default="", help="path to the brand kit")
    p.add_argument("--agent", default="Claude Code (Anthropic)")
    p.add_argument("--ai-model", default="")
    p.add_argument("--doc-version", default="1.0")
    p.add_argument("--reset-config", action="store_true")
    p.add_argument("--force-lectures", action="store_true",
                   help="regenerate the decks even when they already exist")
    p.add_argument("--skip-done", action="store_true",
                   help="do not republish a course that already has book and lectures in PDF")
    p.add_argument("--report", default="", help="where to write the JSON report")
    p.add_argument("--filter", default="", help="publish only matching names")
    args = p.parse_args(argv)

    raiz = common.courses_root(args.folder)
    if not raiz.is_dir():
        print("ERROR: folder not found: %s" % raiz, file=sys.stderr)
        return 2

    # A course is a folder with Markdown in it. Requiring 00-MAPA.md would
    # leave out older courses that use a different index name — and a course
    # that does not publish is a course that vanishes from the catalogue.
    cursos = sorted(c for c in raiz.iterdir()
                    if c.is_dir() and not c.name.startswith(".")
                    and any(c.glob("**/*.md")))
    if args.filter:
        cursos = [c for c in cursos if args.filter in c.name]
    if args.skip_done:
        def pronto(c):
            pub = c / "97-publicacao"
            return (any((pub / "livro" / "pdf").glob("*.pdf"))
                    and any((pub / "slides" / "pdf").glob("aula-*.pdf")))
        cursos = [c for c in cursos if not pronto(c)]

    if not cursos:
        print("Nothing to publish.")
        return 0

    print("Courses to publish: %d · parallelism: %d" % (len(cursos), args.jobs))

    # Seed the theme and the shared fonts with ONE course, serially, before
    # opening the pool: this avoids two processes writing the same .ttf at once.
    print("Seeding theme and fonts with %s..." % cursos[0].name)
    seed = [sys.executable, str(PUBLISH), str(cursos[0]),
            "--only", "book", "--no-pdf"]
    if args.brand:
        seed += ["--brand", args.brand]
    subprocess.run(seed, capture_output=True)

    resultados, falhas = [], 0
    inicio = time.time()
    with futuros.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        tarefas = {pool.submit(publicar_um, c, args): c for c in cursos}
        for i, tarefa in enumerate(futuros.as_completed(tarefas), 1):
            curso = tarefas[tarefa]
            try:
                r = tarefa.result()
            except Exception as erro:                      # noqa: BLE001
                r = {"curso": curso.name, "erros": [repr(erro)], "paginas": 0,
                     "aulas": 0, "slides": 0}
            resultados.append(r)
            if r["erros"] or not r.get("paginas"):
                falhas += 1
            print("[%2d/%d] %-52s book %4d pp · %2d lectures · %4d slides · %5.0fs%s"
                  % (i, len(cursos), r["curso"], r.get("paginas", 0),
                     r.get("aulas", 0), r.get("slides", 0),
                     r.get("segundos", 0),
                     "  ERROR" if r["erros"] else ""), flush=True)

    resultados.sort(key=lambda r: r["curso"])
    destino = Path(args.report) if args.report else raiz / ".publication.json"
    destino.write_text(json.dumps(resultados, indent=2, ensure_ascii=False),
                       encoding="utf-8")

    print("\n== Summary ==")
    print("Courses published : %d (%d with errors)" % (len(resultados), falhas))
    print("Book pages        : %d" % sum(r.get("paginas", 0) for r in resultados))
    print("Lectures          : %d" % sum(r.get("aulas", 0) for r in resultados))
    print("Slides            : %d" % sum(r.get("slides", 0) for r in resultados))
    print("Time              : %.1f min" % ((time.time() - inicio) / 60))
    print("Report            : %s" % destino)
    for r in resultados:
        for e in r["erros"]:
            print("  ERROR in %s: %s" % (r["curso"], e))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
