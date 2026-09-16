# 06 · Escrever as aulas

Nível: iniciante · Verificado em **16/09/2026**

Um livro se lê, um slide se projeta. São dois produtos, e o erro mais comum —
também o mais fácil de detectar — é copiar o capítulo para dentro do slide.

> **Se o slide tem parágrafo, está errado.**

---

## 1. Onde as aulas moram

```
courses/<assunto>-AAAA-MM-DD/97-publicacao/slides/
├── md/                       ← AQUI. um arquivo por aula, escrito à mão
│   ├── LEIA-ME.md            #  a gramática, gerada ao lado de onde se escreve
│   ├── aula-01-<tema>.md
│   └── aula-02-<tema>.md
├── latex/                    ← gerado: cada aula em Beamer
└── pdf/                      ← gerado: um PDF por aula + o PDF único
```

O nome importa: `aula-NN-<tema>.md`. O `NN` define a ordem, e o conversor usa o
nome do arquivo para nomear o `.tex` e o `.pdf`.

---

## 2. A gramática inteira

Cinco marcas resolvem uma aula.

````markdown
---
aula: Aula 03
curso: Docker e Containers
subtitulo: Camadas, cache e o que realmente vai para a imagem
duracao: 45 min
---

# Como o Docker monta uma imagem

## Camadas
A ideia que explica quase todo comportamento estranho do build.

### Uma camada é um diff

- Cada instrução do Dockerfile cria **uma camada**.
- A camada guarda só o que mudou — o resto é reaproveitado.
- É por isso que a ordem das instruções muda o tempo de build.

```notas
Roteiro do professor: mostre `docker history` antes de explicar a teoria.
Quem viu a lista de camadas aceita a explicação; o contrário raramente ocorre.
```

### O cache quebra de cima para baixo
````

| Marca | Vira |
|---|---|
| bloco `---` no topo, `chave: valor` | metadados: `aula`, `curso`, `subtitulo`, `duracao` |
| `#` | o **título da aula** — a capa |
| `##` | uma **parte** da aula — tela de transição |
| `###` | **um slide** |
| `####` e mais fundo | destaque em negrito dentro do slide |
| bloco de código ` ```notas ` | roteiro do professor, **invisível** na projeção |
| `---` dentro de um slide | continua o mesmo slide na tela seguinte, com `(cont.)` |

Listas, tabelas, código, citações e imagens funcionam como em qualquer arquivo
do curso. Todo slide é compilado como `fragile`, então código nunca quebra.

Gabarito completo: [`tools/example/aula-00-modelo.md`](../tools/example/aula-00-modelo.md).

---

## 3. A régua

Referência, não camisa de força. O conversor avisa quando um slide passa do
limite; ele não impede.

| Medida | Valor |
|---|---|
| Aulas por curso | quantas o material exigir — 8 a 25 é o comum; **nunca "uma aula geral"** |
| Slides por aula | 12 a 25 |
| Duração alvo | 30 a 50 min de fala |
| Linhas por slide | **até 10** — o aviso sai a partir de 12 |
| Ideias por slide | **uma**; se o título tem "e", são dois slides |
| Código por slide | até 12 linhas; recorte o trecho e diga onde está o inteiro |

---

## 4. O que entra e o que não entra

**Entra:**

- Uma afirmação por linha.
- Número com **unidade e data**: `11.886 páginas (16/09/2026)`, não "muitas".
- O termo definido na tela em que aparece.
- Um exemplo concreto logo depois de todo conceito abstrato.
- Diagrama em ASCII ou tabela pequena — valem mais que três frases.

**Não entra:**

- Parágrafo. Nunca.
- Lista de dez itens (são dois slides).
- Tabela de quinze linhas (é uma página do livro, não uma tela).
- Captura de tela que ninguém lê no projetor.
- "Conforme vimos anteriormente."

---

## 5. Cobertura: o planejamento antes da primeira aula

Antes de escrever a Aula 01, monte a tabela que liga **cada arquivo do curso** a
pelo menos uma aula. Ela vive no `00-MAPA.md` do curso ou no
`97-publicacao/slides/md/LEIA-ME.md`:

| Arquivo do curso | Aula |
|---|---|
| `01-introducao-leigo.md` | Aula 01 |
| `10-fundamentos.md` | Aula 02, Aula 03 |
| `75-armadilhas.md` | Aula 12 |

Duas leituras dessa tabela:

- **Arquivo sem aula** é furo de cobertura — alguém vai perguntar em sala
  exatamente sobre o que ficou de fora.
- **Aula sem arquivo de origem** é conteúdo novo que deveria estar no material:
  mova para um `.md` do curso e referencie.

---

## 6. O gerador de rascunho

```bash
python3 tools/generate-lectures.py courses/<assunto>-AAAA-MM-DD
```

Converte cada arquivo do curso em um deck: `##` vira tela de transição, `###`
vira slide, a prosa vai para as notas, e o slide fica com listas, tabelas
pequenas e código recortado.

**Para que serve:** cobrir material já escrito, rápido, com 100% dos arquivos
contemplados. Cada deck sai com `gerado: rascunho` no cabeçalho.

**Para que não serve:** apresentar. O gerador não sabe qual é a ideia central de
uma aula, não sabe o que merece uma tela inteira e não inventa a analogia que
faz a turma entender.

Curso novo nasce com aula **escrita à mão**. Usou o gerador e reescreveu? Apague
a linha `gerado: rascunho` — ela é uma declaração de estado, não decoração.

---

## 7. Publicar

```bash
python3 tools/publish-course.py <assunto> --only slides
```

Sai um PDF por aula em `97-publicacao/slides/pdf/`, mais
`<assunto>-slides-completo.pdf` com todas.

Renomeou ou juntou decks? A fábrica apaga o `.tex` e o `.pdf` da aula que deixou
de existir — um PDF órfão com cara de material válido é pior que nenhum.

---

## 8. Conferir antes de dar por pronto

- [ ] Existe um PDF por aula **e** o PDF único com todas.
- [ ] Todo arquivo do curso aparece na tabela de cobertura.
- [ ] Os avisos de "slide grande demais" foram resolvidos ou justificados.
- [ ] Nenhum slide virou parágrafo.
- [ ] A capa de cada aula identifica curso, autor/orientador e o agente de IA.
- [ ] As notas do professor existem onde a explicação não cabe na tela.

---

## Autoteste

1. O que `###` vira, e o que `##` vira?
2. Onde vai o que o professor fala e a plateia não deve ler?
3. Qual é o sinal mais rápido de que um slide está errado?
4. Para que serve a tabela de cobertura — e o que significa uma aula sem arquivo de origem?
5. Quando o deck gerado é aceitável, e quando não é?
