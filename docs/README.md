# Documentação — Course Factory

A fábrica tem três peças e uma regra. As peças: um **preset** que diz ao agente
de IA o que escrever, um **conversor** que transforma Markdown em livro e em
slides, e um **kit de marca** que decide como isso se parece. A regra: o
Markdown do curso é a fonte da verdade, e a publicação nunca o altera.

Leia nesta ordem se está começando. Consulte fora de ordem depois.

| # | Documento | Para quê |
|---|---|---|
| 01 | [Instalação](01-install.md) | pôr a máquina em condição de publicar — LaTeX, Python, clone |
| 02 | [Primeiro curso](02-first-course.md) | do repositório vazio ao primeiro PDF na tela |
| 03 | [Kit de marca](03-brand-kit.md) | **instalar a sua identidade** — o contrato, o pré-molde, a troca |
| 04 | [Arquitetura](04-architecture.md) | como o framework funciona por dentro, e por que assim |
| 05 | [Referência da CLI](05-cli-reference.md) | todo comando, toda opção, o que cada uma faz |
| 06 | [Escrever as aulas](06-lectures.md) | a gramática do deck e a régua do slide |
| 07 | [Problemas](07-troubleshooting.md) | mensagens de erro literais, causa e correção |

---

## O caminho curto

Já tem LaTeX e Python na máquina? Então são quatro linhas:

```bash
git clone <este-repositório> course-factory && cd course-factory
python3 tools/publish-course.py --doctor          # o que falta nesta máquina
python3 tools/sync-brand.py --from-template       # começar pela marca-molde
# escreva um curso em courses/<assunto>-AAAA-MM-DD/, depois:
python3 tools/publish-course.py <assunto>
```

O `--doctor` responde a pergunta que importa antes de qualquer outra: **esta
máquina publica um curso sozinha?**

---

## Vocabulário

Termos que aparecem em todos os documentos, definidos uma vez.

| Termo | O que é |
|---|---|
| **Curso** | uma pasta `courses/<assunto>-AAAA-MM-DD/` com o material em Markdown |
| **Preset** | o `CLAUDE.md` da raiz: a persona, a estrutura e a régua que o agente segue |
| **Bloco** | uma faixa de numeração dentro do curso (A a F); ver o preset |
| **Publicação** | a pasta `97-publicacao/` de um curso: livro e slides, LaTeX e PDF |
| **Kit de marca** | a pasta que carrega a identidade aplicada na publicação |
| **Slot** | `tools/course-factory-brand/` — onde o kit de marca é instalado |
| **Pré-molde** | o kit neutro que vem no repositório, em `.../course-factory-brand/template/` |
| **Deck** | o arquivo Markdown de **uma** aula, em `97-publicacao/slides/md/` |
| **md2book** | o conversor Markdown → LaTeX → PDF, embarcado em `tools/md2book/` |

---

## O que a fábrica não faz

Honestidade antecipada poupa uma tarde:

- **Não revisa o que o agente escreveu.** A régua está no preset; a
  responsabilidade editorial é de quem orienta.
- **Não verifica fato.** Se o modelo inventou um preço ou um ISBN, o PDF sai
  com o erro em tipografia bonita. O preset manda buscar na web; confira.
- **Não escreve aula boa sozinha.** `generate-lectures.py` gera **rascunho**, e
  diz isso no cabeçalho de cada deck. Ver [06](06-lectures.md).
- **Não hospeda nada.** O PDF sai na sua máquina. Onde ele circula é decisão
  sua.
