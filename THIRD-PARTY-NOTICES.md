# Componentes de terceiros

O que este repositório distribui e não é de autoria própria, com a licença de
cada item. Conferido em **16/09/2026**.

---

## Software

| Componente | Onde | Licença | Titular |
|---|---|---|---|
| **md2book** | `tools/md2book/` | MIT | Ronivaldo D. Andrade — repositório próprio: <https://github.com/ronidomingues/md2book> |

`md2book` é cópia embarcada (*vendored*) do repositório acima: a fábrica
funciona sem instalar nada além do LaTeX. A cópia traz o `LICENSE` original em
`tools/md2book/LICENSE` e é atualizada com
`python3 tools/sync-brand.py --md2book <caminho-do-checkout>`.

A cópia é **fiel ao upstream, sem patch local** — inclusive nos valores padrão,
que ainda citam a marca do autor (por exemplo, `"tema": "andradasdev"` como
default de slides em `src/md2book/slides.py`). Esses padrões nunca entram em
jogo aqui: os `*.base.json` do kit de marca definem o tema em toda publicação.
Manter a cópia sem alterações é o que permite atualizá-la do upstream sem
conflito.

---

## Tipografia

**Este repositório não distribui arquivo de fonte.**

O pré-molde de marca (`tools/course-factory-brand/template/`) usa a família
**Latin Modern**, que acompanha qualquer instalação de TeX Live (licença GUST
Font License, uma licença livre aprovada, equivalente à OFL), e **DejaVu Sans**
para símbolos, presente na maioria dos sistemas. Nenhuma das duas é copiada
para cá — elas já estão na máquina de quem compila.

Um kit de marca instalado no slot **pode** distribuir tipografia própria. Se o
fizer, a licença é responsabilidade de quem monta o kit. Regra prática:

| Licença da fonte | Pode redistribuir no kit? |
|---|---|
| SIL Open Font License 1.1 (Inter, JetBrains Mono, a maioria das do Google Fonts) | **Sim** — mantendo o arquivo de licença junto |
| Apache 2.0 | **Sim** — mantendo o aviso |
| GUST Font License (Latin Modern, TeX Gyre) | **Sim** |
| Comercial / EULA de foundry | **Quase sempre não** — leia o contrato |

Ver [`docs/03-brand-kit.md`](docs/03-brand-kit.md), seção "Tipografia".

---

## LaTeX

A compilação depende de pacotes distribuídos com o TeX Live — `graphicx`,
`xcolor`, `fontspec`, `beamer`, `fancyhdr`, `eso-pic`, `etoolbox`, `needspace`,
`hyperref`, entre outros. Não são redistribuídos aqui; vêm da instalação do
TeX Live, cada um sob a sua própria licença (LPPL, na maioria).

---

## Agente de IA

O material didático produzido com esta fábrica é redigido por um agente de
inteligência artificial — por padrão **Claude Code (Anthropic)**. O agente não
é um componente deste repositório: é uma ferramenta externa, usada por quem
executa a fábrica, sob os termos do respectivo fornecedor.

O crédito ao agente é impresso em toda peça publicada, por decisão editorial.
Ver [`docs/04-architecture.md`](docs/04-architecture.md).
