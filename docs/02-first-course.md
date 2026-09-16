# 02 · Primeiro curso

Nível: iniciante · Verificado em **16/09/2026**

Do repositório recém-clonado a um livro em PDF e uma aula projetável. Assume a
máquina pronta — se `--doctor` ainda reclama, volte para
[01 · Instalação](01-install.md).

---

## 1. Instale uma marca

A fábrica não tem identidade própria. Antes do primeiro curso, escolha com o
que ele vai sair assinado:

```bash
# começar pelo molde neutro (dá para trocar depois)
python3 tools/sync-brand.py --from-template

# ou apontar para a sua, que mora no próprio repositório
git clone git@github.com:voce/sua-marca.git ~/sua-marca
echo ~/sua-marca > tools/course-factory-brand/BRAND_PATH
python3 tools/sync-brand.py --check
```

O detalhe inteiro está em [03 · Kit de marca](03-brand-kit.md). Para seguir
agora, o molde basta.

---

## 2. Duas formas de escrever o curso

### 2.1 Com o agente de IA — o caminho para que a fábrica existe

Abra um agente de programação nesta pasta (o preset é o `CLAUDE.md` da raiz, e
o Claude Code o lê sozinho ao abrir o diretório) e peça um assunto:

```
me ensina expressões regulares
```

O agente lê o preset, pesquisa, cria `courses/regex-2026-09-16/` e escreve o
curso inteiro: introdução para leigo, pré-requisitos, manual de instalação,
projetos executáveis, núcleo teórico, prática, custos, bibliografia, glossário
— e no fim publica o livro e as aulas.

O preset é longo de propósito: ele é a diferença entre "um agente escreveu um
texto" e "saiu um curso com régua". Leia-o antes de mudá-lo — mudar o
`CLAUDE.md` muda a fábrica inteira.

### 2.2 À mão — para entender a mecânica

Um curso é uma pasta com Markdown. O mínimo que publica:

```bash
mkdir -p courses/meu-assunto-2026-09-16
cd courses/meu-assunto-2026-09-16
```

`00-MAPA.md` — o índice, e de onde saem o título e o subtítulo da capa:

```markdown
# Meu Assunto — mapa do curso

Nível: iniciante
Data: 16/09/2026

Uma frase que explica do que se trata. Ela vira o subtítulo da capa do livro,
então escreva-a como se fosse aparecer impressa — porque vai.
```

`01-introducao.md` — o primeiro capítulo. E é só isso: qualquer `.md` fora de
`97-publicacao/` entra no livro, na ordem do nome do arquivo.

> **A regra da numeração.** Os arquivos são agrupados em blocos por faixa —
> `01–09` porta de entrada, `10–69` núcleo, `70–79` prática, `80–89` economia,
> `90–96` fontes. O nome do bloco vira a divisão de partes do livro. A faixa
> está descrita no `CLAUDE.md` e configurada em `md2book/book.base.json` do kit
> de marca.

---

## 3. Publique

```bash
cd /caminho/do/course-factory
python3 tools/publish-course.py meu-assunto
```

Note que bastou o assunto: a fábrica encontra `courses/meu-assunto-2026-09-16/`
sozinha, e escolhe a mais recente se houver mais de uma data.

Saída esperada, encurtada:

```
Course: .../courses/meu-assunto-2026-09-16
Title : Meu Assunto
Brand : course-factory-brand (installed)
Preparing the brand theme...
  fonts: as declared by the brand kit (no files shipped)

== Book ==
  livro.json written
...
== Result ==
Book   : .../97-publicacao/livro/pdf/meu-assunto-livro.pdf
Lectures: 0 PDF(s)
Theme  : .../97-publicacao/tema
```

Abra o PDF. Ele tem capa com a marca, página de créditos, sumário, o material
inteiro e colofão.

`Lectures: 0` é o esperado: você ainda não escreveu aula nenhuma.

---

## 4. O que apareceu dentro do curso

```
courses/meu-assunto-2026-09-16/
├── 00-MAPA.md                  ← seu
├── 01-introducao.md            ← seu
└── 97-publicacao/              ← gerado, e só isto é gerado
    ├── LEIA-ME.md              #  o que é cada pasta e como refazer
    ├── livro/
    │   ├── livro.json          #  a configuração DESTE livro
    │   ├── latex/              #  main.tex + um .tex por capítulo
    │   └── pdf/                #  meu-assunto-livro.pdf
    ├── slides/
    │   ├── md/LEIA-ME.md       #  a gramática do deck, ao lado de onde se escreve
    │   ├── latex/
    │   └── pdf/
    └── tema/                   #  a identidade aplicada: .sty, logos, brand-env.tex
```

**A regra que não se negocia:** a fábrica escreve **só** dentro de
`97-publicacao/`. Seu Markdown nunca é apagado, movido ou reescrito.

---

## 5. Agora as aulas

Escreva o primeiro deck em `97-publicacao/slides/md/aula-01-<tema>.md`:

````markdown
---
aula: Aula 01
curso: Meu Assunto
subtitulo: O que é e para que serve
duracao: 40 min
---

# O que é meu assunto

## A ideia

### Uma afirmação por linha

- O slide não é o capítulo.
- Se tem parágrafo, está errado.
- Uma ideia por tela.

```notas
Roteiro do professor: aqui vai o que se fala, e não aparece na projeção.
```
````

Publique só as aulas:

```bash
python3 tools/publish-course.py meu-assunto --only slides
```

Sai um PDF por aula em `97-publicacao/slides/pdf/`, mais o PDF único com todas.
A gramática completa e a régua do slide estão em
[06 · Escrever as aulas](06-lectures.md).

> Tem um curso já escrito e quer cobrir o material rápido? `python3
> tools/generate-lectures.py courses/meu-assunto-2026-09-16` gera decks de
> **rascunho** a partir dos capítulos. Serve para cobrir, não para apresentar.

---

## 6. O ciclo do dia a dia

```
edita o .md  →  publica  →  abre o PDF  →  corrige  →  publica de novo
```

Republicar é barato e idempotente. Só há duas coisas a saber:

- `livro.json` e `slides.json` são **preservados** entre publicações — é onde
  você ajusta o estilo de **um** curso específico. Para refazê-los a partir do
  kit de marca: `--reset-config`.
- Mudou o kit de marca? Republique os cursos afetados. **PDF desatualizado é
  pior que PDF ausente: ele mente com aparência de pronto.**

Para a fábrica inteira:

```bash
python3 tools/publish-all.py courses --jobs 6
python3 tools/repair-publication.py courses --check   # o que ficou faltando
```

---

## 7. Registre no catálogo

O `INDEX.md` da raiz é o catálogo do que a fábrica produziu. Acrescente uma
linha por curso novo: assunto, data, o que ele cobre, e onde o PDF publicado
vive. Um curso que ninguém encontra é um curso que não existe.

---

## Autoteste

1. De onde saem o título e o subtítulo da capa do livro?
2. Qual é a **única** pasta em que a fábrica escreve dentro de um curso?
3. O que acontece com `livro.json` quando você republica um curso?
4. Qual a diferença entre um deck escrito e um deck gerado?
5. Por que republicar depois de mudar o kit de marca não é opcional?
