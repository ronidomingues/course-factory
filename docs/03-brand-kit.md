# 03 · Kit de marca

Nível: intermediário · Verificado em **16/09/2026**

A fábrica **não tem identidade própria**. Ela publica com a identidade de
alguém, e essa identidade é uma **dependência**: uma pasta que satisfaz um
contrato, instalada em `tools/course-factory-brand/`.

Este documento diz o que essa pasta precisa ter, como instalar a sua, e por que
a arquitetura é assim.

---

## 1. Por que a marca é uma dependência

Três razões, e a terceira é a que decide.

1. **Marca é de quem é.** Logotipo, paleta, tipografia e manual pertencem a uma
   empresa ou a uma pessoa. Uma ferramenta pública que carregasse a identidade
   de alguém dentro de si estaria distribuindo o que não é dela.
2. **Identidade muda em outro ritmo que a ferramenta.** O manual da marca é
   revisado por motivos de marca; o conversor, por motivos de software. Juntos
   no mesmo repositório, um obriga o outro a versionar à toa.
3. **Ferramenta livre, marca fechada, sem contradição.** A fábrica é MIT. O kit
   que você instala pode ser proprietário, privado, e nunca sair da sua
   máquina. As duas coisas convivem porque estão em repositórios diferentes.

> **Opinião profissional, marcada como tal:** um framework de publicação que
> força a identidade do autor é um framework que ninguém adota. Separar a marca
> foi o que tornou este repositório publicável.

---

## 2. O slot e a ordem de busca

```
tools/course-factory-brand/          ← o SLOT
├── template/                        ← o pré-molde neutro, versionado aqui
├── BRAND_PATH                       ← ponteiro para o kit, quando ele mora fora
└── <ou o seu kit, aqui dentro>      ← ignorado pelo git
```

A fábrica resolve a marca na primeira que existir:

| Ordem | Origem | Como se ativa |
|---|---|---|
| 1 | caminho explícito | `--brand <caminho>` |
| 2 | variável de ambiente | `COURSE_FACTORY_BRAND=<caminho>` |
| 3 | **ponteiro** | `tools/course-factory-brand/BRAND_PATH`, um caminho por linha |
| 4 | **o slot** | um kit instalado em `tools/course-factory-brand/` |
| 5 | o pré-molde | `tools/course-factory-brand/template/`, sempre presente |

### 2.1 O ponteiro `BRAND_PATH`

Um kit que mora no próprio repositório, fora desta árvore, precisa continuar
ligado. Uma variável de ambiente resolveria, mas tem de ser exportada em **todo**
shell — inclusive naquele em que o agente de IA roda — e um kit que cai
silenciosamente no pré-molde publica material assinado por ninguém.

O ponteiro é um arquivo de uma linha, lembrado pela máquina e não pela pessoa:

```bash
echo /home/voce/sua-marca > tools/course-factory-brand/BRAND_PATH
python3 tools/sync-brand.py --check     # deve dizer: (pointer)
```

Aceita caminho absoluto ou relativo ao próprio slot — `../../../sua-marca`
sobrevive ao repositório mudar de lugar. Linhas em branco e as que começam com
`#` são comentário. Apontando para algo que não é um kit, a fábrica **avisa** e
segue a ordem — nunca publica errado em silêncio.

O arquivo é ignorado pelo git: ele descreve **esta** máquina.

Uma pasta **é** um kit de marca quando tem `latex/coursebook.sty`. Esse arquivo
é o marcador: é a peça sem a qual o livro não existe.

O `.gitignore` deste repositório ignora tudo dentro do slot **exceto**
`template/`. Um kit privado instalado ali não sobe junto com a fábrica.

> ⚠️ **`git clone <repo> tools/course-factory-brand` não funciona.** O `git
> clone` exige o destino vazio, e o slot já contém o `template/`. Clone para
> fora e use o ponteiro — é o que a seção 4.2 mostra.

Confira a qualquer momento:

```bash
python3 tools/sync-brand.py --check
```

---

## 3. O contrato

Um kit de marca é esta árvore. As linhas em **negrito** são obrigatórias.

```
<kit>/
├── brand.env                            ← OBRIGATÓRIO  dados que vão impressos
├── BRAND-MANUAL.md                      ← OBRIGATÓRIO  o manual da marca
├── EDITORIAL-STANDARD.md                ← OBRIGATÓRIO  o que livro e slide podem fazer
├── latex/
│   ├── coursebook.sty                   ← OBRIGATÓRIO  pacote `coursebook`, o livro
│   └── beamerthemecourseslides.sty      ← OBRIGATÓRIO  tema `courseslides`, as aulas
├── md2book/
│   ├── book.base.json                   ← OBRIGATÓRIO  estilo-base do livro
│   └── slides.base.json                 ← OBRIGATÓRIO  estilo-base das aulas
├── assets/*.pdf                            opcional    logos, para o LaTeX
├── logo/*.svg                              opcional    as fontes vetoriais dos logos
├── palette/                                GERADO      tokens de cor (--palette)
└── fonts/
    ├── fonts.json                          opcional    a tipografia declarada
    └── *.ttf | *.otf                       opcional    os arquivos, se puder distribuí-los
```

Falta alguma das obrigatórias? A fábrica **recusa publicar** e diz qual é.
Nunca sai um PDF meio-marcado.

### 3.1 `brand.env`

Pares `CHAVE=valor`, sem aspas. Referências `${OUTRA}` são resolvidas.

| Chave | Vai impresso em | Obrigatória |
|---|---|---|
| `BRAND_NAME` | capa, rodapé, créditos, colofão | sim |
| `BRAND_NAME_LOWER` | rodapé dos slides, assinatura | sim |
| `BRAND_TAGLINE` | capa, colofão, fecho de aula | recomendada |
| `BRAND_DESCRIPTOR` | página de créditos | recomendada |
| `BRAND_OWNER` | **autor e orientador** — capa e créditos | sim |
| `BRAND_AUTHOR` | propriedades do PDF | recomendada |
| `BRAND_EMAIL`, `BRAND_SITE`, `BRAND_SITE_URL` | créditos, colofão | opcionais |
| `BRAND_PROMPT` | telas de seção dos slides (**LaTeX cru**) | opcional |
| `BRAND_COURSE_LEVEL` | linha de nível na capa | opcional |
| `BRAND_COURSE_LICENSE` | linha de licença nos créditos | opcional |

> **Nunca ponha segredo aqui.** Este arquivo vira texto impresso na capa de um
> PDF que você vai distribuir. Senha, token e chave moram no cofre.

### 3.2 As macros que a fábrica escreve

A cada publicação, `publish-course.py` gera `97-publicacao/tema/brand-env.tex`
e o copia para onde o LaTeX compila. Os dois `.sty` o leem com
`\InputIfFileExists{brand-env.tex}{}{}`.

**Dados da marca** — definidos com `\def`, prontos para uso:

`\cfBrand` · `\cfBrandLower` · `\cfTagline` · `\cfDescriptor` · `\cfOwner` ·
`\cfAuthor` · `\cfEmail` · `\cfSite` · `\cfSiteURL` · `\cfPrompt`

**Dados do curso** — chamados como comandos de um argumento; o `.sty` os define
como *setters* que guardam o valor:

| Macro | Conteúdo |
|---|---|
| `\cftitle{}` | título do curso |
| `\cfsubtitle{}` | subtítulo, lido do `00-MAPA.md` |
| `\cfsubject{}` | o assunto em kebab-case |
| `\cfversion{}` | versão da publicação (`--doc-version`) |
| `\cfdate{}` | data da publicação, por extenso |
| `\cfproduced{}` | data de **geração do curso**, do nome da pasta |
| `\cfyear{}` | o ano |
| `\cflevel{}` | linha de nível da capa |
| `\cfpiece{}` | a peça: "Livro do curso" |
| `\cfadvisor{}` | autor e orientador |
| `\cfagent{}` | o agente de IA que escreveu |
| `\cfaimodel{}` | o modelo do agente |
| `\cflicense{}` | linha de licença |
| `\cfrepo{}` | repositório de origem |
| `\cfextent{}` | "29 documentos · 12.400 linhas" |
| `\cfnote{}` | linha extra |
| `\cfcourse{}` | o título, para os slides |
| `\cflecture{}` | a aula corrente, definida pelo md2book |

Um `.sty` que não conhece uma macro não quebra: a fábrica emite
`\providecommand` para todas antes de chamá-las, e o que sobra vira no-op.

### 3.3 Os comandos que o seu `.sty` precisa oferecer

O md2book chama estes por nome, configurados nos `*.base.json`:

| Comando | Quem chama | O que deve desenhar |
|---|---|---|
| `\cfbookopening` | `book.base.json` → `capa_comando` | capa + página de créditos |
| `\cfcolophon` | `book.base.json` → `encerramento` | o colofão, no fim do livro |
| `\cfslidecover` | `slides.base.json` → `capa_comando` | a capa da aula |
| `\cfsection[sub]{título}` | `slides.base.json` → `secao_comando` | tela de transição |
| `\cfslideclosing[nota]` | `slides.base.json` → `fechamento_comando` | tela de fecho da aula |
| `\cfassets{caminho}` | opcional | redefine onde estão os logos |

Quer outros nomes? Pode — desde que `capa_comando`, `secao_comando`,
`fechamento_comando` e `encerramento` nos seus `*.base.json` apontem para eles.
Os nomes acima são a convenção, não uma trava.

### 3.4 Os `*.base.json`

São o estilo-base de **todos** os cursos publicados com aquele kit. A fábrica
mescla cada um com os dados do curso e grava `livro.json` / `slides.json`
dentro do curso — que depois é preservado entre publicações.

Chaves que o livro exige apontar para o seu kit:

```json
"recursos": [
  "97-publicacao/tema/coursebook.sty",
  "97-publicacao/tema/brand-env.tex"
],
"pacotes_extra": ["coursebook"],
"capa_comando": "\\cfbookopening",
"encerramento": ["\\cfcolophon"]
```

E nos slides:

```json
"tema": "courseslides",
"recursos": ["../tema/beamerthemecourseslides.sty", "../tema/brand-env.tex"],
"capa_comando": "\\cfslidecover",
"secao_comando": "\\cfsection",
"fechamento_comando": "\\cfslideclosing"
```

> **Mudar o estilo de todos os cursos** é editar estes dois arquivos no kit —
> nunca o `livro.json` de um curso. Depois: `python3 tools/publish-all.py
> courses --reset-config --jobs 6`.

### 3.5 Cores — um arquivo, e só

Uma cor pode ser nomeada em três lugares, e só um vence. O `brand.env` é a
fonte: o `publish-course.py` emite cada `BRAND_COLOR_*` como `\definecolor` no
`brand-env.tex`, que os `.sty` leem **depois** dos próprios padrões.

```bash
BRAND_COLOR_cfBlue=3B82F6       # cor condutora — o que vem depois do hex é comentário
BRAND_COLOR_cfInk=101620        # fundo escuro de capa e de slide
```

O nome é o do `\color{...}` no seu `.sty`; o valor são seis dígitos hex, com ou
sem `#`. Um valor inválido é ignorado **com aviso** — nunca em silêncio.

O md2book pinta os blocos de código e o filete de destaque sozinho, a partir do
JSON, antes de qualquer `.sty` carregar. Essas cinco cores têm chaves próprias:

| Chave | Vai para |
|---|---|
| `BRAND_BOOK_ACCENT` | `book.base.json` → `cor_destaque` |
| `BRAND_BOOK_CODE_BG` · `BRAND_BOOK_CODE_BORDER` | fundo e borda do código, no livro |
| `BRAND_SLIDES_ACCENT` | `slides.base.json` → `cor_destaque` |
| `BRAND_SLIDES_CODE_BG` · `_BORDER` · `_FG` | o bloco de código, no slide |
| `BRAND_SLIDES_MUTED` | `cor_texto_apoio` |

Para ver quem está vencendo — e qual declaração virou letra morta:

```bash
python3 tools/sync-brand.py --colors
```

```
  NAME             brand.env  .sty       WINNER
  cfBlue           FF5C8A     3B82F6     brand.env (the .sty value is dead)
```

> ⚠️ **Cuidado com `\colorlet` no tema Beamer.** `\colorlet{cfBg}{cfInk}` copia
> o valor **no ato**. Se rodar antes do `\InputIfFileExists{brand-env.tex}`, o
> papel congela a cor padrão do `.sty` e a cor do `brand.env` nunca chega à
> tela. Nos `.sty` deste repositório a atribuição de papéis vem **depois** da
> leitura, de propósito. Fazendo o seu do zero, mantenha essa ordem.

#### `palette/` é gerado

`palette/tokens.json` e `palette/tokens.css` saem do `brand.env`:

```bash
python3 tools/sync-brand.py --palette
```

Não edite à mão — o cabeçalho de cada arquivo diz isso. Eles existem para quem
consome a identidade **fora** do LaTeX (site, slides em HTML, Figma). O
`--colors` avisa quando estão desatualizados.

### 3.6 Tipografia

Sem `fonts/fonts.json`, o kit não distribui fonte: vale o que os `*.base.json`
declararem, e essas famílias precisam existir na máquina de quem compila. É o
que o pré-molde faz, com a família Latin Modern do TeX Live.

Com `fonts/fonts.json`, a fábrica sabe copiar os arquivos junto com o material:

```json
{
  "check":     ["Inter", "JetBrains Mono"],
  "extension": ".ttf",
  "system":    { "texto": "Inter", "titulo": "JetBrains Mono",
                 "mono": "JetBrains Mono", "simbolos": "DejaVu Sans" },
  "embedded":  { "texto": "Inter", "titulo": "JetBrainsMono",
                 "mono": "JetBrainsMono", "simbolos": "DejaVu Sans" },
  "families": {
    "Inter": {
      "license": "SIL Open Font License 1.1",
      "files":   ["Inter-Regular.ttf", "Inter-Bold.ttf", "Inter-SemiBold.ttf"],
      "faces":   { "UprightFont": "*-Regular", "BoldFont": "*-Bold",
                   "FontFace": "{sb}{n}{*-SemiBold}" }
    }
  }
}
```

- `system` — os nomes **como o sistema os conhece**, usados quando as fontes
  estão instaladas.
- `embedded` — os **prefixos dos arquivos** em `fonts/`, usados quando elas
  viajam junto.
- `check` — o que testar com `fc-list` para decidir entre os dois.

> **Cuidado legal.** Distribuir arquivo de fonte só é permitido se a licença
> deixar. SIL OFL 1.1 e Apache 2.0 deixam (mantendo o texto da licença junto);
> a maioria das comerciais, não. Ponha o arquivo de licença ao lado, com nome
> `LICENSE-*.txt` ou `LICENCA-*.txt` — a fábrica o copia junto com as fontes,
> exatamente por isso. Detalhes em
> [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).

### 3.7 `assets/` e `logo/`

Tudo que for `.pdf` em `assets/` é copiado para `97-publicacao/tema/assets/`, e
o seu `.sty` referencia pelo nome, via `\cf@assets`. Os nomes são privados do
seu kit — a fábrica não exige nenhum.

`logo/` guarda os `.svg` de origem. Converta com:

```bash
inkscape --export-type=pdf --export-filename=assets/symbol.pdf logo/symbol.svg
```

> **Dica de projeto:** o pré-molde **não** desenha o nome da marca dentro do
> logo. Ele compõe símbolo + `\cfBrandLower` em tipo, em tempo de compilação.
> Trocar `BRAND_NAME` troca a assinatura inteira sem redesenhar nada. Se o seu
> logotipo tiver o nome embutido, você perde isso — vale a pena pesar.

---

## 4. Instalar a sua marca

### 4.1 Começando do zero, pelo molde

```bash
python3 tools/sync-brand.py --from-template
```

Copia o pré-molde para a raiz do slot. Agora é seu, e a ordem é esta:

1. **`brand.env`** — nome, tagline, autor/orientador **e as cores**. É o único
   arquivo que precisa mudar para a identidade ficar outra.
2. **`logo/*.svg`** → converta para `assets/*.pdf`.
3. **`BRAND-MANUAL.md`** e **`EDITORIAL-STANDARD.md`** — escreva os seus.
4. `python3 tools/sync-brand.py --palette` para regerar `palette/`.

Os dois `.sty` só precisam de edição se você quiser mudar **a estrutura** das
páginas — a capa, os créditos, o colofão. Para recolorir, não toque neles.

Publique um curso de teste e olhe o PDF antes de seguir.

### 4.2 Se você já tem um repositório de marca

Clone **fora** do slot e aponte para ele. O slot não está vazio — tem o
`template/` dentro —, e `git clone` para um diretório não vazio falha:

```bash
git clone git@github.com:voce/sua-marca.git ~/sua-marca
echo ~/sua-marca > tools/course-factory-brand/BRAND_PATH
python3 tools/sync-brand.py --check      # deve dizer: (pointer)
```

Cada repositório mantém o próprio histórico, e o `BRAND_PATH` é ignorado pelo
git da fábrica. Em outra máquina, clone os dois e recrie o ponteiro.

Prefere o kit dentro da árvore? Copie o conteúdo para o slot:

```bash
python3 tools/sync-brand.py --install ~/sua-marca --dry-run
python3 tools/sync-brand.py --install ~/sua-marca
```

E, para casos pontuais:

```bash
export COURSE_FACTORY_BRAND=~/sua-marca                  # só neste shell
python3 tools/publish-course.py x --brand ~/sua-marca    # só nesta chamada
```

### 4.3 Trocando a marca de um material já publicado

Republique. Sempre. O tema é **copiado** para dentro de cada curso em
`97-publicacao/tema/`, e é de lá que o PDF antigo foi compilado — ele não muda
sozinho porque você mudou o kit.

```bash
python3 tools/publish-all.py courses --reset-config --jobs 6
```

`--reset-config` é necessário quando a mudança está nos `*.base.json`; sem ele,
o `livro.json` de cada curso é preservado e a mudança não chega.

---

## 5. Checklist de um kit pronto

- [ ] `python3 tools/sync-brand.py --check` diz **Contract satisfied**.
- [ ] `python3 tools/sync-brand.py --colors` não acusa declaração morta
      nem `palette/` desatualizada.
- [ ] Um curso de teste publica livro **e** aulas, sem aviso de LaTeX.
- [ ] A capa traz marca, título, autor/orientador e o agente de IA.
- [ ] A página de créditos diz o que cada um fez.
- [ ] O rodapé de toda página tem marca e título do curso.
- [ ] O colofão fecha o livro.
- [ ] A capa e o fecho de cada aula identificam curso, autor e agente.
- [ ] Nenhuma cor de texto reprova em contraste (4.5:1 normal, 3:1 grande).
- [ ] Se há fonte em `fonts/`, a licença permite distribuí-la e o arquivo de
      licença está ao lado.
- [ ] O kit está no **seu** repositório, não no da fábrica.

---

## Autoteste

1. Qual arquivo prova que uma pasta é um kit de marca?
2. Em que ordem a fábrica procura a marca, e o que vence?
2b. Por que o `BRAND_PATH` é melhor que uma variável de ambiente?
3. O que acontece se faltar `BRAND-MANUAL.md`?
4. Qual a diferença entre `system` e `embedded` no `fonts.json`?
5. Por que trocar a cor da marca não muda os PDFs já gerados?
6. Onde se muda o estilo de **todos** os cursos — e onde não se muda?
7. Por que `\colorlet` antes do `brand-env.tex` quebra a troca de cor?
8. Quem gera o `palette/`, e por que ele não se edita à mão?
