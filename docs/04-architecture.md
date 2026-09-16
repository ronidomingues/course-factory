# 04 · Arquitetura

Nível: intermediário · Verificado em **16/09/2026**

Como o framework funciona por dentro, peça por peça, e por que cada decisão foi
tomada assim. Se você só quer usar a fábrica, [02](02-first-course.md) basta.
Este documento é para quem vai mexer nela.

---

## 1. A ideia em uma frase

**Um preset diz ao agente de IA o que escrever; o agente escreve Markdown; um
conversor transforma esse Markdown em livro e em aulas; um kit de marca decide
como isso se parece.**

```
   você digita um assunto
             │
             ▼
  ┌──────────────────────────┐
  │  CLAUDE.md — o preset    │  persona, estrutura obrigatória, curva de
  │                          │  profundidade, régua de qualidade, quando
  └───────────┬──────────────┘  buscar na web
              ▼
  ┌──────────────────────────┐
  │  Agente de IA            │  pesquisa, escreve, monta os projetos,
  │  (Claude Code, ou outro) │  escreve as aulas
  └───────────┬──────────────┘
              ▼
  ┌──────────────────────────┐
  │  courses/<assunto>-DATA/ │  o curso em Markdown  ← A FONTE DA VERDADE
  └───────────┬──────────────┘
              ▼
  ┌──────────────────────────┐        ┌───────────────────────────┐
  │  tools/publish-course.py │◀───────│  kit de marca instalado   │
  │  + tools/md2book/        │        │  (.sty, cores, logos,     │
  └───────────┬──────────────┘        │   brand.env, base.json)   │
              ▼                       └───────────────────────────┘
      97-publicacao/
        livro/{latex,pdf}  ·  slides/{md,latex,pdf}  ·  tema/
```

---

## 2. As quatro peças

### 2.1 O preset — `CLAUDE.md`

Não é documentação: é **instrução executável por um agente**. Ele define a
persona (professor + veterano + pesquisador), a estrutura obrigatória de
arquivos em blocos numerados, a curva de doze camadas de profundidade, a regra
dos cinco porquês, quando a busca na web é obrigatória, e o padrão de
publicação.

É a peça que distingue "pedi um texto para uma IA" de "saiu um curso". Mudar o
`CLAUDE.md` muda tudo o que a fábrica produz daí em diante.

**Por que em Markdown e não em código?** Porque o consumidor dele é um modelo
de linguagem, não um interpretador. Prosa densa e tabelas são o formato que ele
segue melhor — e que uma pessoa consegue revisar.

### 2.2 O curso — `courses/<assunto>-AAAA-MM-DD/`

Markdown puro, numerado por blocos. A data no nome da pasta é a **data de
geração**, não a da última alteração: material técnico envelhece, e quem abrir
o curso em dois anos precisa saber contra qual realidade ele foi escrito antes
de ler a primeira linha.

`courses/` **não é versionado** neste repositório. A ferramenta é pública; o
material é de quem o gerou.

### 2.3 O conversor — `tools/md2book/`

Cópia embarcada do [md2book](https://github.com/ronidomingues/md2book) (MIT).
Faz Markdown → LaTeX → PDF, em dois modos:

- **livro** — junta a pasta inteira em um `main.tex` com partes, capítulos,
  sumário e um apêndice com o código-fonte dos projetos;
- **slides** — converte cada deck em um `.tex` Beamer e compila um PDF por aula.

Está embarcado, e não declarado como dependência, por um motivo prático: uma
máquina nova precisa publicar com `git clone` + LaTeX, sem `pip install`. O
custo é manter a cópia em dia, e é o que `sync-brand.py --md2book` resolve.

### 2.4 O kit de marca — `tools/course-factory-brand/`

Um slot de dependência. Ver [03 · Kit de marca](03-brand-kit.md) para o
contrato inteiro.

---

## 3. O motor, passo a passo

O que `publish-course.py` faz, na ordem, e o porquê de cada passo.

| # | Passo | Por quê |
|---|---|---|
| 1 | resolve o kit de marca | sem identidade não há publicação; falta algo, ele recusa |
| 2 | lê `brand.env` | os dados que vão impressos na capa |
| 3 | lê `00-MAPA.md` | título e subtítulo da capa saem do material, não da linha de comando |
| 4 | conta documentos e linhas | a extensão real vai na capa — "29 documentos · 12.400 linhas" |
| 5 | copia os `.sty` e os logos para `97-publicacao/tema/` | o curso precisa ser recompilável em outra máquina, sem o kit |
| 6 | escreve `tema/brand-env.tex` | traduz `.env` + metadados em macros LaTeX |
| 7 | resolve a tipografia | instalada, ou copiada uma vez para o repositório |
| 8 | grava `livro.json` / `slides.json` (só na primeira vez) | o ajuste fino de um curso sobrevive à republicação |
| 9 | chama o md2book | gera o `.tex` e compila |
| 10 | separa `.tex` em `latex/` e `.pdf` em `pdf/` | e apaga os intermediários — `.aux`, `.log`, `.xdv` |
| 11 | escreve `97-publicacao/LEIA-ME.md` | o estado da publicação, dentro do próprio curso |

### 3.1 Por que o tema é copiado, e não referenciado

A alternativa seria apontar o LaTeX para `tools/course-factory-brand/latex/` por
caminho absoluto. Seria mais enxuto e estaria errado: o `.tex` de um curso
publicado precisa continuar compilando daqui a um ano, em outra máquina, na mão
de alguém que recebeu só a pasta do curso. Copiar custa ~40 KB por curso e
compra reprodutibilidade.

### 3.2 Por que a tipografia tem quatro políticas

`--fonts auto | system | repo | course` existe porque a conta muda com o
contexto:

| Política | Onde ficam as fontes | Custo | Quando usar |
|---|---|---|---|
| `auto` | instaladas, se houver; senão uma cópia no repositório | nenhum ou ~3 MB | o padrão |
| `system` | só as instaladas | zero | CI com as fontes instaladas |
| `repo` | uma cópia para todos os cursos | ~3 MB, uma vez | muitos cursos no mesmo repositório |
| `course` | dentro do próprio curso | ~3 MB **por curso** | mandar **uma** pasta para alguém |

Fonte instalada não ocupa espaço mas some quando o material viaja. Fonte copiada
viaja junto mas pesa. `auto` resolve o caso comum sozinho.

### 3.3 A regra que não se negocia

`publish-course.py` escreve **exclusivamente** dentro de `97-publicacao/`.
Material do curso não é apagado, movido nem reescrito — em nenhuma circunstância.
As únicas remoções que ele faz são dentro da própria pasta gerada: os
intermediários do LaTeX, e o `.pdf`/`.tex` de uma aula cujo deck deixou de
existir (senão sobraria um PDF órfão com cara de material válido).

---

## 4. Os programas

| Programa | Faz |
|---|---|
| `tools/publish-course.py` | publica **um** curso: livro, aulas, ou os dois |
| `tools/publish-all.py` | publica a pasta inteira, em paralelo, com relatório JSON |
| `tools/repair-publication.py` | refaz só o que faltou numa rodada em lote |
| `tools/generate-lectures.py` | gera decks de **rascunho** a partir do material |
| `tools/sync-brand.py` | instala, confere e atualiza o slot de marca |
| `tools/common.py` | resolve caminhos: marca, md2book, fontes |

Referência completa das opções: [05 · CLI](05-cli-reference.md).

### 4.1 Paralelismo em `publish-all.py`

Um curso por thread, chamando `publish-course.py` em subprocesso. As fontes
compartilhadas são **semeadas antes** de abrir o pool, em série: dois processos
copiando o mesmo `.ttf` ao mesmo tempo deixariam um arquivo pela metade para um
terceiro ler.

O relatório sai em `.publication.json` na pasta dos cursos: páginas por livro,
aulas, slides, avisos e falhas. É dele que sai a atualização do catálogo.

### 4.2 Por que existe um programa só para reparar

Numa rodada de dezenas de cursos alguma compilação sempre cai — um caractere de
controle dentro de um bloco de código, memória apertada, um contador do LaTeX
que estourou. Republicar tudo custa horas. `repair-publication.py` olha o que
**faltou** (livro sem PDF, deck sem PDF) e refaz só aquilo.

---

## 5. O que fica versionado, e o que não

| Caminho | No git? | Por quê |
|---|---|---|
| `CLAUDE.md`, `tools/`, `docs/`, `INDEX.md` | **sim** | é a fábrica |
| `tools/course-factory-brand/template/` | **sim** | o molde neutro, MIT |
| `tools/course-factory-brand/*` (o resto) | não | identidade de terceiro |
| `courses/` | não | o material é de quem o gerou |
| `.publication.json`, `.course-factory-fonts/` | não | subprodutos |

---

## 6. Limites conhecidos

Ditos aqui para não serem descobertos na pior hora:

- **A estrutura do curso é em português.** Nomes como `00-MAPA.md`,
  `97-publicacao/` e as faixas de bloco vêm do preset, que é pt-BR. A CLI e a
  documentação da ferramenta são em inglês; o material, não. Traduzir a
  estrutura é possível — é editar o `CLAUDE.md` e os `*.base.json` — mas
  quebraria os cursos já publicados, então ficou como está.
- **`97-publicacao/` é um nome fixo**, constante no código. Ainda não é
  configurável.
- **Não há teste automatizado.** A verificação é publicar um curso e olhar o
  PDF. Para um gerador de documento, é honestamente o teste que importa; ainda
  assim, é uma lacuna.
- **O agente não é verificado.** A fábrica não checa se o que foi escrito é
  verdade. Essa responsabilidade é de quem orienta, e o preset a coloca por
  escrito.

---

## Autoteste

1. Por que o tema é copiado para dentro de cada curso em vez de referenciado?
2. Qual é a única pasta em que `publish-course.py` escreve?
3. Por que as fontes compartilhadas são semeadas antes do paralelismo?
4. Quando `--fonts course` vale a pena, apesar de pesar mais?
5. O que `repair-publication.py` faz que `publish-all.py` faria mais devagar?
6. Por que `courses/` não é versionado?
