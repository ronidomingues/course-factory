<!-- markdownlint-disable MD033 -->
# Course Factory

**Você escreve o nome de um assunto. Sai um curso completo — do zero absoluto ao
nível de pesquisa —, um livro em PDF e os slides de todas as aulas.**

Este repositório não é um projeto de software comum: é uma **linha de produção de
material didático operada por um agente de IA**. Um preset de comportamento
([`CLAUDE.md`](CLAUDE.md)) diz ao agente o que escrever, com que profundidade e
com que régua; um conversor embarcado transforma o Markdown resultante em livro
e em aulas, em LaTeX e PDF; e um **kit de marca plugável** decide como isso se
parece.

> <sup>**In English** — Course Factory turns a single subject name into a full
> course written by an AI agent (from absolute beginner to research level), then
> publishes it as a print-ready PDF book plus one Beamer slide deck per lecture.
> The brand identity is a swappable dependency, so the output carries *your*
> identity, not the tool's. MIT licensed. Docs are in Brazilian Portuguese,
> because the courses are.</sup>

<p align="center">
  <a href="docs/01-install.md">Instalação</a> ·
  <a href="docs/02-first-course.md">Primeiro curso</a> ·
  <a href="docs/03-brand-kit.md">Kit de marca</a> ·
  <a href="docs/04-architecture.md">Arquitetura</a> ·
  <a href="docs/05-cli-reference.md">CLI</a> ·
  <a href="INDEX.md">Catálogo</a>
</p>

---

## O que já saiu daqui

Números de **16/09/2026**, medidos por `publish-all.py` sobre a produção real
desta fábrica. Os cursos não são versionados neste repositório — ver
[Onde ficam os cursos](#onde-ficam-os-cursos).

| Métrica | Valor |
|---|---|
| Cursos produzidos | **47** |
| Documentos de curso | **1.486** arquivos Markdown · **~460.000** linhas |
| Livros publicados | **47** · **11.886 páginas** em PDF |
| Aulas em slides | **1.712** apresentações · **53.648** telas |
| Fonte LaTeX | gerada junto com cada PDF, ao lado dele |

O catálogo de assuntos está em [`INDEX.md`](INDEX.md).

---

## Como funciona

Três peças, e só a primeira precisa da sua atenção.

```
        você digita um assunto
                  │
                  ▼
   ┌──────────────────────────────┐
   │  CLAUDE.md — o preset        │  quem o agente é, o que deve produzir,
   │  (persona, estrutura, régua) │  em que profundidade, com que fontes
   └──────────────┬───────────────┘
                  ▼
   ┌──────────────────────────────┐
   │  Agente de IA                │  pesquisa na web, escreve os documentos,
   │  (Claude Code, ou outro)     │  monta os projetos, escreve as aulas
   └──────────────┬───────────────┘
                  ▼
   ┌──────────────────────────────┐
   │  courses/<assunto>-AAAA-MM-DD│  o curso em Markdown  ← a fonte da verdade
   │      └── 97-publicacao/      │  livro PDF + slides PDF + o LaTeX dos dois
   └──────────────┬───────────────┘
                  ▲
   ┌──────────────┴───────────────┐
   │  tools/course-factory-brand/ │  a identidade aplicada — uma DEPENDÊNCIA,
   │  (kit de marca instalado)    │  não uma parte da ferramenta
   └──────────────────────────────┘
```

O `CLAUDE.md` é lido automaticamente pelo agente ao abrir esta pasta. Ele define
a persona (professor universitário + profissional veterano + pesquisador
atualizado), a estrutura obrigatória de blocos, a curva de 12 camadas de
profundidade, a regra dos cinco porquês, quando pesquisar na web e o padrão de
publicação. **Mudar o `CLAUDE.md` muda a fábrica inteira.**

---

## Começar

```bash
git clone <url-deste-repositorio> course-factory && cd course-factory

python3 tools/publish-course.py --doctor        # esta máquina publica sozinha?
python3 tools/sync-brand.py --from-template     # instala a marca-molde

echo ~/Documentos/cursos > COURSES_PATH         # opcional: onde os cursos ficam
```

Abra um agente de programação nesta pasta e diga um assunto:

```
me ensina expressões regulares
```

O agente cria `courses/regex-2026-09-16/`, escreve o curso inteiro e publica.
Ou, se preferir escrever à mão, ponha o Markdown na pasta e rode:

```bash
python3 tools/publish-course.py regex --ai-model "Claude Opus 5"
```

Passo a passo completo: [`docs/02-first-course.md`](docs/02-first-course.md).

### Quanto tempo leva

| Tamanho do assunto | Documentos | Tempo do agente | Livro |
|---|---|---|---|
| Pontual (ex.: *optimistic locking*) | 8–12 | 20–40 min | 40–80 páginas |
| Médio (ex.: Docker, SQL) | 20–30 | 1–3 h | 150–300 páginas |
| Grande (ex.: JWT, pentest) | 30–45 | 3–6 h | 300–600 páginas |

---

## O que sai: anatomia de um curso

A pasta se chama **`<assunto>-AAAA-MM-DD`** — o assunto em kebab-case mais a
data de geração. A data está no nome porque material técnico envelhece: um curso
de `kubernetes-2026-09-15` diz, já no nome, contra qual realidade foi escrito.

```
courses/kubernetes-2026-09-15/
│
├── 00-MAPA.md                    índice, roteiro, status de cada bloco
│
│  BLOCO A · PORTA DE ENTRADA (01–09)
├── 01-introducao-leigo.md        o que é e por que existe, sem jargão
├── 02-pre-requisitos.md          o que saber antes, com rota de resgate
├── 03-instalacao.md              manual de campo: três SOs, versões testadas, erros literais
├── 04-como-comecar.md            do ambiente pronto ao primeiro resultado na tela
├── 05-manual-de-uso.md           referência consultável, organizada por tarefa
├── 06-exemplos.md                10+ exemplos completos, do trivial ao de produção
├── 07-projeto-modelo/            TRÊS ou mais aplicações completas e executáveis
│
│  BLOCO B · NÚCLEO (10–69)
├── 10-fundamentos.md             vocabulário e modelos mentais
├── 11-historia.md                que problema fez isso existir
├── …                             mecânica interna, sem caixa-preta
├── 60-teoria-avancada.md         provas, algoritmos, limites teóricos
├── 65-estado-da-arte.md          fronteira atual, com data
│
│  BLOCO C · PRÁTICA E ERROS (70–79)
├── 70-pratica.md · 75-armadilhas.md
│
│  BLOCO D · ECONOMIA (80–89)
├── 80-custos-e-licencas.md       preços com data, licença, custo oculto
├── 85-cursos-e-certificacoes.md  cursos gratuitos PT/EN/FR — pesquisados na web
│
│  BLOCO E · FONTES (90–96)
├── 90-bibliografia.md · 95-referencias.md · GLOSSARIO.md
│
│  BLOCO F · PUBLICAÇÃO (gerado)
└── 97-publicacao/
    ├── livro/{latex,pdf}/        o livro do curso
    ├── slides/{md,latex,pdf}/    as aulas: fonte, LaTeX e PDFs
    └── tema/                     a identidade aplicada, copiada para dentro
```

Cada arquivo traz o **nível** no topo, a **data** quando o conteúdo envelhece, e
um **autoteste** de 5 a 9 perguntas no fim.

---

## A marca é sua, não da ferramenta

`tools/course-factory-brand/` é um **slot de dependência**. Quem publica instala
ali a própria identidade — logotipo, paleta, tipografia, manual, `.sty` — e o
material sai assinado com ela.

```bash
# começar pelo molde neutro que vem no repositório
python3 tools/sync-brand.py --from-template

# ou apontar para a sua, num repositório separado (privado, se a marca for)
git clone git@github.com:voce/sua-marca.git ~/sua-marca
echo ~/sua-marca > tools/course-factory-brand/BRAND_PATH
python3 tools/sync-brand.py --check
```

O slot e o ponteiro são ignorados pelo git da fábrica: um kit privado convive
sem risco de subir junto. Sem um kit que cumpra o contrato, a fábrica **recusa
publicar** — nunca sai um PDF meio-marcado.

Trocar a identidade é editar **um arquivo**: nome, tagline, autor e as cores
vivem todos no `brand.env` do kit, e de lá alcançam o LaTeX e o conversor.
`tools/sync-brand.py --colors` mostra qual cor está de fato vencendo.

O que toda peça publicada traz, qualquer que seja a marca:

| Peça | O que aparece |
|---|---|
| Capa do livro | marca, título, **autor e orientador**, o **agente de IA** que escreveu, nível, versão, datas e extensão |
| Página de créditos | quem fez o quê — com crédito explícito ao agente, por decisão editorial |
| Rodapé de toda página | marca e título do curso |
| Colofão | símbolo, marca, tagline e os créditos outra vez |
| Capa e fecho de cada aula | curso, aula, autor/orientador e o agente |

Contrato completo: [`docs/03-brand-kit.md`](docs/03-brand-kit.md).

> **Por que creditar a IA.** Quem lê tem o direito de saber como o material foi
> produzido. Um livro de 300 páginas escrito por um modelo de linguagem e
> orientado por uma pessoa não é a mesma coisa que um livro escrito à mão, e
> esconder isso é desonesto com o leitor. Por isso o crédito traz o nome **e a
> versão** do modelo (`--ai-model`).

---

## As regras que o agente segue

O que separa material didático de texto gerado. Todas detalhadas no
[`CLAUDE.md`](CLAUDE.md).

| Regra | O que significa na prática |
|---|---|
| **12 camadas de profundidade** | Intuição → definição informal → por que existe → primeiro uso → formalismo → mecânica interna → implementação → casos reais → trade-offs → economia → pesquisa → fronteira. Pular camada exige justificativa escrita. |
| **Regra dos cinco porquês** | Segue até uma lei física/matemática, uma decisão histórica documentada, um trade-off econômico ou uma convenção arbitrária — e então diz que é arbitrária. "O padrão define" não é resposta. |
| **Define antes de usar** | Todo termo aparece definido, e vai para o `GLOSSARIO.md`. |
| **Exemplo concreto sempre** | Todo conceito abstrato ganha um exemplo logo depois. |
| **Código executável** | Nada de `...` no meio. Se está no material, roda. |
| **Web obrigatória** | Instalação, preços, cursos, bibliografia e estado da arte são pesquisados antes de escrever, com data e fontes no rodapé. |
| **Nada inventado** | Nunca um ISBN, preço, link ou número fabricado. Na dúvida, diz que é aproximado ou omite. |
| **Datas absolutas** | "Em 15/09/2026", nunca "recentemente". |
| **Separar fato de opinião** | Quando é recomendação profissional e não consenso, o texto diz isso. |

E o limite, dito na frente: **a fábrica não verifica fato.** Se o modelo inventou
um preço, o PDF sai com o erro em tipografia bonita. O preset manda buscar na
web e citar a fonte; a responsabilidade editorial é de quem orienta.

---

## Estrutura do repositório

```
course-factory/
├── CLAUDE.md                     O PRESET — as regras que o agente obedece
├── INDEX.md                      catálogo dos cursos produzidos
├── LICENSE                       MIT, com o escopo explicitado
├── THIRD-PARTY-NOTICES.md        o que é de terceiros, e sob que licença
├── docs/                         a documentação do framework
├── courses/                      os cursos gerados  (NÃO versionado)
└── tools/                        o motor
    ├── publish-course.py · publish-all.py · repair-publication.py
    ├── generate-lectures.py · sync-brand.py · common.py
    ├── md2book/                  o conversor Markdown → LaTeX → PDF (MIT)
    └── course-factory-brand/     O SLOT DE MARCA
        └── template/             o pré-molde neutro, versionado
```

**Autossuficiente:** numa máquina com Python 3 e LaTeX, um `git clone` publica.
Não há `pip install`, não há Pandoc, não há dependência de rede.

---

## Requisitos

Para **escrever** cursos, basta o agente. Para **publicar** em PDF:

```bash
sudo apt install texlive-xetex texlive-latex-extra texlive-lang-portuguese \
                 latexmk poppler-utils
```

macOS, Windows/WSL2, Fedora e a alternativa sem instalar nada:
[`docs/01-install.md`](docs/01-install.md).

---

## Onde ficam os cursos

`courses/` **não é versionado**. A ferramenta é pública; o material produzido
pertence a quem o gerou e circula onde cada um decidir — site, Drive, servidor
próprio ou um repositório à parte.

Os cursos produzidos pela Andrada's Dev com esta fábrica são distribuídos em
PDF (livro e aulas), com o catálogo em [`INDEX.md`](INDEX.md).

---

## Licença

**MIT** — ver [`LICENSE`](LICENSE), que traz o escopo explicitado. Em resumo:

- **A fábrica é livre.** Preset, programas, documentação e pré-molde de marca:
  use, modifique, redistribua, inclusive comercialmente.
- **Os cursos produzidos são de quem os produziu.** Este repositório não
  distribui curso nenhum.
- **Kits de marca de terceiros seguem a licença deles.** Instalar um kit no slot
  não o licencia.
- **A marca Andrada's Dev não está aqui e não é licenciada por este documento.**
  Usar a fábrica é permitido; assinar material com a marca Andrada's Dev, não.

Componentes de terceiros: [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).

---

## Créditos

| Papel | Quem |
|---|---|
| **Autor e orientador** | **Ronivaldo Domingues de Andrade** — concebeu a fábrica, definiu o preset, o escopo, a profundidade e o padrão de qualidade, e responde pelo resultado |
| **Escrita e materialização** | Agente de IA (Claude Code, Anthropic), nomeado e versionado em cada peça publicada |
| **Conversor** | [md2book](https://github.com/ronidomingues/md2book) — MIT, mesmo autor |

---

<div align="center">
<sub>Um preset, um conversor e um kit de marca.<br>
O resto é o assunto que você escolher.</sub>
</div>
