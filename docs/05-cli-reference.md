# 05 · Referência da CLI

Nível: intermediário · Verificado em **16/09/2026**

Consulta rápida, organizada por tarefa. Todo comando roda a partir da raiz do
repositório e não exige instalação.

---

## Por tarefa

| Quero… | Comando |
|---|---|
| saber se esta máquina publica | `python3 tools/publish-course.py --doctor` |
| escolher onde os cursos ficam | `echo ~/Documentos/cursos > COURSES_PATH` |
| conferir o kit de marca | `python3 tools/sync-brand.py --check` |
| ver de onde vem cada cor | `python3 tools/sync-brand.py --colors` |
| recolorir a marca | editar `BRAND_COLOR_*` no `brand.env`, depois `--palette` |
| começar uma marca do zero | `python3 tools/sync-brand.py --from-template` |
| publicar um curso | `python3 tools/publish-course.py <assunto>` |
| só o livro / só as aulas | `... --only book` / `... --only slides` |
| publicar tudo | `python3 tools/publish-all.py --jobs 6` |
| ver o que faltou numa rodada | `python3 tools/repair-publication.py --check` |
| refazer só o que faltou | `python3 tools/repair-publication.py courses` |
| rascunhar as aulas de um curso pronto | `python3 tools/generate-lectures.py courses/<pasta>` |
| mudar o estilo de todos os cursos | editar `*.base.json` no kit, depois `publish-all.py --reset-config` |
| gerar só o LaTeX, sem compilar | `python3 tools/publish-course.py <assunto> --no-pdf` |

---

## `publish-course.py` — publica um curso

```
python3 tools/publish-course.py [curso] [opções]
```

O argumento aceita três formas, da mais curta para a mais explícita:

```bash
python3 tools/publish-course.py docker                       # só o assunto
python3 tools/publish-course.py docker-2026-08-11            # com a data
python3 tools/publish-course.py courses/docker-2026-08-11    # o caminho
```

Só o assunto? Ele procura em `./`, `./courses/` e `./cursos/`, e usa a data mais
recente se houver mais de uma — avisando qual escolheu.

| Opção | Padrão | O que faz |
|---|---|---|
| `--only {all,book,slides}` | `all` | que peça publicar |
| `--brand <caminho>` | o slot, depois `template/` | o kit de marca a usar |
| `--courses <caminho>` | o `COURSES_PATH`, depois `courses/` | onde procurar o curso |
| `--md2book <caminho>` | a cópia embarcada | outro md2book |
| `--doc-version <texto>` | `1.0` | versão impressa na capa e nos créditos |
| `--agent <texto>` | `Claude Code (Anthropic)` | o agente creditado |
| `--ai-model <texto>` | vazio | **o modelo** — passe sempre; "IA" sem versão não é informação |
| `--advisor <nome>` | `BRAND_OWNER` do `brand.env` | autor e orientador |
| `--license <texto>` | `BRAND_COURSE_LICENSE` | linha de licença nos créditos |
| `--repo <texto>` | vazio | repositório de origem, nos créditos |
| `--note <texto>` | vazio | linha extra na capa e nos créditos |
| `--level <texto>` | `BRAND_COURSE_LEVEL` | linha de nível da capa |
| `--reset-config` | desligado | **reescreve** `livro.json` e `slides.json` a partir do kit |
| `--fonts {auto,system,repo,course}` | `auto` | de onde vêm as fontes — ver [04 §3.2](04-architecture.md) |
| `--no-pdf` | desligado | gera o `.tex` e para |
| `--doctor` | — | diagnóstico da máquina, e sai |

**Códigos de saída:** `0` publicou · `1` nada saiu · `2` erro de uso (curso não
encontrado, kit de marca inválido, md2book ausente).

> `--reset-config` é a opção que mais confunde. Sem ela, o `livro.json` de um
> curso é **preservado** — é o que permite ajustar um curso específico sem
> perder o ajuste na próxima publicação. Com ela, o arquivo é refeito a partir
> do `*.base.json` do kit, e o ajuste local se perde. Mudou o kit e a mudança
> "não apareceu"? É isto.

---

## `publish-all.py` — a pasta inteira, em paralelo

```
python3 tools/publish-all.py [pasta] [opções]
```

| Opção | Padrão | O que faz |
|---|---|---|
| `--jobs N` | `4` | cursos em paralelo |
| `--only {all,book,slides}` | `all` | que peça publicar |
| `--brand <caminho>` | o slot | repassado a cada curso |
| `--agent`, `--ai-model`, `--doc-version`, `--reset-config` | — | repassados a cada curso |
| `--force-lectures` | desligado | regera os decks de rascunho mesmo se já existirem |
| `--skip-done` | desligado | pula curso que já tem livro e aulas em PDF |
| `--filter <texto>` | vazio | publica só os cursos cujo nome contenha o texto |
| `--report <arquivo>` | `<pasta>/.publication.json` | onde gravar o relatório |

O relatório JSON traz, por curso: páginas do livro, número de aulas, total de
slides, documentos, tempo e a lista de avisos e erros.

**Quantos jobs?** Um por núcleo físico é agressivo — o XeLaTeX é pesado de
memória. `--jobs 6` em uma máquina de 8 núcleos e 16 GB é um ponto seguro.

---

## `repair-publication.py` — completa o que faltou

```
python3 tools/repair-publication.py [pasta] [--check]
```

Livro sem PDF → republica o livro. Deck sem PDF → compila aquele `.tex` e
junta o PDF único de novo. Nada mais.

`--check` só relata, e é o que se roda primeiro:

```
Courses to repair: 2
  docker-2026-08-11          book ok · 3 lecture(s) with no PDF
  redes-2026-09-08           book missing
```

---

## `generate-lectures.py` — rascunho dos decks

```
python3 tools/generate-lectures.py <pasta-do-curso> [--force] [--title "Nome"]
```

Um arquivo do curso vira uma aula; um `##` vira tela de transição; um `###`
vira slide; a prosa vai para as notas do professor.

**É rascunho, e cada deck diz isso no cabeçalho.** Serve para cobrir material
já escrito. Curso novo tem aula escrita à mão — ver [06](06-lectures.md).

Escreve **só** em `97-publicacao/slides/md/`, e se recusa a sobrescrever decks
existentes sem `--force`.

---

## `sync-brand.py` — o slot de marca

```
python3 tools/sync-brand.py [ação] [--dry-run] [--force]
```

| Ação | O que faz |
|---|---|
| *(nenhuma)* ou `--check` | confere o kit instalado contra o contrato |
| `--colors` | mostra qual cor vence e qual declaração virou letra morta |
| `--palette` | regera `palette/tokens.json` e `tokens.css` a partir do `brand.env` |
| `--from-template` | copia o pré-molde para a raiz do slot, para você tornar seu |
| `--install <caminho>` | copia um kit de outra pasta para o slot |
| `--md2book <caminho>` | atualiza a cópia embarcada do md2book |
| `--brand <caminho>` | confere **esse** caminho em vez do slot |

`--dry-run` diz o que mudaria sem mudar nada. `--force` sobrescreve um kit já
instalado. A direção é sempre de fora para dentro: a origem nunca é escrita.

---

## Onde a marca é apontada

| Forma | Alcance | Quando usar |
|---|---|---|
| `--brand <caminho>` | uma chamada | teste pontual, comparar duas marcas |
| `COURSE_FACTORY_BRAND` | um shell | script, CI |
| `tools/course-factory-brand/BRAND_PATH` | **a máquina** | **o padrão** quando a marca tem repositório próprio |
| o kit dentro do slot | a máquina | quando a marca vive dentro da árvore |

```bash
echo ~/sua-marca > tools/course-factory-brand/BRAND_PATH
python3 tools/sync-brand.py --check     # deve dizer: (pointer)
```

## Onde os cursos são procurados

| Forma | Alcance | Quando usar |
|---|---|---|
| `--courses <caminho>` | uma chamada | teste pontual |
| `COURSE_FACTORY_COURSES` | um shell | script, CI |
| **`COURSES_PATH` na raiz do repo** | **a máquina** | **o padrão** |
| `courses/` | — | quando nada foi dito |

```bash
echo ~/Documentos/cursos > COURSES_PATH
python3 tools/publish-course.py --doctor | grep Courses
```

`publish-all.py` e `repair-publication.py` passam a rodar sem argumento de pasta.

## Variáveis de ambiente

| Variável | Para quê |
|---|---|
| `COURSE_FACTORY_BRAND` | caminho do kit de marca, quando ele mora fora do slot |
| `COURSE_FACTORY_COURSES` | onde os cursos ficam, quando não é `courses/` |
| `MD2BOOK` | caminho de outro md2book |

---

## Autoteste

1. O que `publish-course.py docker` faz se existirem duas pastas `docker-*`?
2. Por que `livro.json` é preservado entre publicações?
3. Qual comando roda primeiro quando uma rodada em lote teve falhas?
4. O que `--dry-run` garante em `sync-brand.py`?
5. Qual opção você nunca deve esquecer ao publicar material creditado a uma IA?
