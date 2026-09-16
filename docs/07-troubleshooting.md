# 07 · Problemas

Nível: iniciante a intermediário · Verificado em **16/09/2026**

Mensagens literais, causa provável e correção. Procure pela mensagem, não pelo
sintoma.

---

## 1. Antes de qualquer coisa

```bash
python3 tools/publish-course.py --doctor
```

Ele responde, em uma tela, o que a máquina tem e o que falta. A maioria dos
problemas desta página aparece aí primeiro.

---

## 2. Instalação e ambiente

| Mensagem | Causa provável | Correção |
|---|---|---|
| `bash: python3: command not found` | Python não instalado, ou fora do PATH | Instale (ver [01](01-install.md)). No Windows nativo o comando é `python`, não `python3`. |
| `xelatex   MISSING` no `--doctor` | LaTeX ausente | `sudo apt install texlive-xetex texlive-latex-extra texlive-lang-portuguese` |
| `xelatex` instalado mas não encontrado (macOS) | o PATH do TeX só vale em sessões novas | Abra outro terminal, ou `eval "$(/usr/libexec/path_helper)"` |
| `! LaTeX Error: File 'fancyhdr.sty' not found.` | falta `texlive-latex-extra` (ou o `collection-latexextra`) | Instale o pacote; no MiKTeX, ative a instalação automática |
| `pdfunite/gs   MISSING` | poppler ausente | `sudo apt install poppler-utils`. Sem ele as aulas saem em PDFs separados, sem o PDF único — não é fatal |
| `latexmk   MISSING` | opcional | O md2book chama o motor direto. O sumário pode exigir uma segunda publicação para estabilizar |

---

## 3. Kit de marca

| Mensagem | Causa | Correção |
|---|---|---|
| `ERROR: no brand kit found.` | o slot está vazio e o `template/` sumiu | `python3 tools/sync-brand.py --from-template`, ou `--brand <caminho>` |
| `ERROR: the brand kit at ... does not meet the contract. Missing: BRAND-MANUAL.md` | falta um arquivo obrigatório | Crie-o. A lista inteira está em [03 §3](03-brand-kit.md) |
| `A kit is already installed at ... Use --force` | proteção contra sobrescrever | `--dry-run` para ver o que mudaria; `--force` para aceitar |
| `WARNING: ...BRAND_PATH points at ..., which is not a brand kit` | o ponteiro aponta para pasta errada, ou o kit mudou de lugar | Corrija o caminho no arquivo. Confira com `sync-brand.py --check` |
| `--check` diz `(template)` quando deveria dizer `(pointer)` | o `BRAND_PATH` não existe, está vazio ou só tem comentário | `echo ~/sua-marca > tools/course-factory-brand/BRAND_PATH` |
| `WARNING: brand fonts not found at ... the material will come out in DejaVu` | o `fonts.json` declara famílias, mas os arquivos não estão lá | Ponha os `.ttf` em `fonts/`, ou remova o `fonts.json` e declare as famílias nos `*.base.json` |
| `brand fonts MISSING` no `--doctor` | o kit não distribui fonte | **Não é erro** se as famílias declaradas estão instaladas. É o caso do pré-molde |

### Mudei a cor e nada mudou

Rode `python3 tools/sync-brand.py --colors`. Ele diz, cor por cor, quem vence:

| Diz | Significa |
|---|---|
| `brand.env (the .sty value is dead)` | você editou o `.sty`; quem manda é o `brand.env` |
| `brand.env wins; the JSON value is dead` | idem, para as cores do conversor |
| `.sty (not in brand.env)` | essa cor ainda não está no `brand.env` |

Mudou o `brand.env` e o **slide** continua igual? O tema Beamer pode estar
atribuindo os papéis (`\colorlet`) **antes** de ler o `brand-env.tex` — aí o
papel congela a cor padrão. Ver [03 §3.5](03-brand-kit.md).

E, em qualquer caso: republique. O tema é copiado para dentro de cada curso.

### A marca mudou e o PDF não

O tema é **copiado** para dentro de cada curso em `97-publicacao/tema/`, e o
PDF antigo foi compilado de lá. Republique:

```bash
python3 tools/publish-all.py courses --reset-config --jobs 6
```

Sem `--reset-config`, o `livro.json` do curso é preservado — e mudanças feitas
nos `*.base.json` do kit não chegam. É a causa nº 1 de "mudei e não mudou".

---

## 4. Curso não encontrado

| Mensagem | Causa | Correção |
|---|---|---|
| `ERROR: course folder not found: docker` | nome errado, ou os cursos não estão onde a fábrica procura | A mensagem lista as pastas consultadas. Aponte o destino: `echo <caminho> > COURSES_PATH`, ou passe `--courses <caminho>` |
| `WARNING: more than one course named docker; using the most recent` | duas gerações do mesmo assunto | É o comportamento esperado. Para escolher outra, passe a pasta com a data |
| `WARNING: ... has no 00-MAPA.md — the title will come from the folder name.` | curso sem mapa | Crie o `00-MAPA.md`. O título e o subtítulo da capa saem dele |

---

## 5. Compilação do LaTeX

| Mensagem | Causa | Correção |
|---|---|---|
| `! Text line contains an invalid character` | caractere de controle dentro de um bloco de código do Markdown | Abra o `.md` e remova o byte. `grep -nP '[\x00-\x08\x0b\x0c\x0e-\x1f]' arquivo.md` acha |
| `! LaTeX Error: Too deeply nested` | lista com aninhamento acima de quatro níveis | Reduza no Markdown — não cabe numa página impressa de qualquer forma |
| `! TeX capacity exceeded, sorry [main memory size=...]` | curso muito grande num único `main.tex` | Publique `--only book` e `--only slides` separadamente; se persistir, divida o curso |
| `! File ended while scanning use of \@writefile` | compilação anterior interrompida deixou um `.aux` truncado | `python3 tools/repair-publication.py courses` — ele apaga o rastro antes de refazer |
| `! Package fontspec Error: The font "Inter" cannot be found.` | a família declarada não está instalada nem embarcada | Instale a fonte, ou use `--fonts repo` com os arquivos em `fonts/`, ou troque a família no `*.base.json` do kit |
| `WARNING: md2book exited with code 1 on the book.` | erro de compilação | O motivo está em `97-publicacao/livro/latex/main.log`. Procure a primeira linha iniciada por `!` |

### O log é o que importa

```bash
grep -n '^!' courses/<pasta>/97-publicacao/livro/latex/main.log | head
```

A **primeira** linha com `!` é a causa. As seguintes costumam ser consequência.

---

## 6. Slides

| Sintoma | Causa | Correção |
|---|---|---|
| aviso de slide grande demais | mais de 12 linhas na tela | Divida em dois `###`, ou aceite e justifique |
| uma aula sem PDF, o resto ok | falhou só aquele `.tex` | `python3 tools/repair-publication.py courses` compila só o que faltou |
| PDF de uma aula que não existe mais | resto de deck renomeado | A fábrica apaga sozinha na próxima publicação de slides |
| `no lectures written yet: put the decks in ...` | não há deck nenhum | Escreva o primeiro, ou gere o rascunho com `generate-lectures.py` |
| o PDF único não saiu | falta `pdfunite` e `gs` | `sudo apt install poppler-utils` |

---

## 7. Publicação em lote

| Sintoma | Correção |
|---|---|
| a rodada demorou horas e alguns cursos falharam | `python3 tools/repair-publication.py courses --check` lista; sem `--check`, refaz |
| a máquina travou com `--jobs 12` | XeLaTeX é pesado de memória. Use `--jobs 4` a `6` |
| quero republicar só um assunto | `--filter docker` |
| quero pular o que já está pronto | `--skip-done` |

O relatório de cada rodada fica em `courses/.publication.json`, com páginas,
aulas, avisos e erros por curso.

---

## 8. Git

| Sintoma | Causa | Correção |
|---|---|---|
| o `git status` quer subir centenas de PDFs | `courses/` fora do `.gitignore` | Confira o `.gitignore`; `git rm -r --cached courses/` tira do índice sem apagar do disco |
| o kit de marca privado apareceu no `git status` | ele foi instalado fora do slot | Mova para `tools/course-factory-brand/`, que é ignorado — ou acrescente o caminho ao `.gitignore` |

> **Se um kit privado chegou a ser commitado**, tirar no commit seguinte não
> resolve: o conteúdo continua no histórico. Reescrever o histórico é a única
> saída, e se o commit já foi empurrado para um repositório público, trate a
> identidade como exposta.

---

## 9. Quando nada disso serve

1. Rode `--doctor` e guarde a saída.
2. Rode o caso mínimo: publique o curso de teste mais simples que você tiver,
   com `--brand tools/course-factory-brand/template`. Se **o molde** funciona, o
   problema está no seu kit.
3. Publique com `--no-pdf`. Se o `.tex` sai e o PDF não, o problema é LaTeX, não
   fábrica.
4. Abra o `main.log` e procure a primeira linha com `!`.

Essa sequência separa os três culpados possíveis — máquina, kit, material — em
poucos minutos.
