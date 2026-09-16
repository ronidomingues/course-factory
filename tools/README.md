# `tools/` — o motor da fábrica

Tudo o que transforma uma pasta de Markdown em livro e em aulas. Nada aqui
precisa ser instalado: `python3 tools/<programa>.py` funciona a partir de um
clone limpo, desde que a máquina tenha Python 3 e LaTeX.

```
tools/
├── publish-course.py         publica UM curso: livro, aulas, ou os dois
├── publish-all.py            publica a pasta inteira, em paralelo
├── repair-publication.py     refaz só o que faltou numa rodada em lote
├── generate-lectures.py      rascunho dos decks, a partir do material
├── sync-brand.py             instala, confere e atualiza o kit de marca
├── common.py                 resolve caminhos: marca, md2book, fontes
├── example/                  o gabarito de um deck de aula
├── md2book/                  o conversor Markdown → LaTeX → PDF (MIT, embarcado)
└── course-factory-brand/     ← O SLOT DE MARCA
    └── template/                o pré-molde neutro, versionado
```

---

## O slot de marca

`course-factory-brand/` é uma **dependência**, não uma pasta de código. É onde
quem publica instala a própria identidade — normalmente clonando ali um
repositório separado, privado se a marca for.

O `.gitignore` deste repositório ignora tudo dentro do slot **exceto**
`template/`. Você pode clonar um kit privado ali sem risco de ele subir junto.

```bash
python3 tools/sync-brand.py --check           # o kit instalado serve?
python3 tools/sync-brand.py --from-template   # começar pelo molde
```

O kit pode ficar **fora** desta árvore — é o normal quando a marca tem
repositório próprio. Nesse caso, um ponteiro de uma linha o mantém ligado:

```bash
echo ~/sua-marca > tools/course-factory-brand/BRAND_PATH
```

O contrato inteiro — arquivos obrigatórios, macros LaTeX, tipografia — está em
[`docs/03-brand-kit.md`](../docs/03-brand-kit.md).

---

## Começo rápido

```bash
python3 tools/publish-course.py --doctor        # esta máquina publica?
python3 tools/publish-course.py <assunto>       # publica um curso
python3 tools/publish-all.py courses --jobs 6   # publica todos
```

Referência de toda opção: [`docs/05-cli-reference.md`](../docs/05-cli-reference.md).

---

## As duas regras do motor

1. **Escreve só em `97-publicacao/`.** Material de curso não é apagado, movido
   nem reescrito — em nenhuma circunstância.
2. **Sem marca válida, não publica.** Falta um arquivo do contrato? Ele recusa e
   diz qual. Nunca sai um PDF meio-marcado.

---

## `md2book/` é cópia

Vem do repositório <https://github.com/ronidomingues/md2book> (MIT) e está
embarcado para que uma máquina nova publique com `git clone` + LaTeX, sem
`pip install`. Atualize a cópia a partir de um checkout:

```bash
python3 tools/sync-brand.py --md2book ~/md2book --dry-run
python3 tools/sync-brand.py --md2book ~/md2book
```

---

## Nota sobre idioma

A interface é em inglês — nomes de pasta, de arquivo, de opção e as mensagens
de execução. O material produzido é em **português do Brasil**, e por isso a
estrutura interna de um curso (`00-MAPA.md`, `97-publicacao/`, os nomes de
bloco) e os textos gerados **dentro** de um curso continuam em pt-BR. São duas
camadas diferentes: a ferramenta e o produto.
