# Catálogo — cursos produzidos com esta fábrica

Este é o registro do que a **Course Factory** já produziu. Cada linha é um curso
completo: do zero absoluto ao nível de pesquisa, com projetos executáveis, livro
em PDF e uma apresentação por aula.

**Situação em 16/09/2026:** 47 cursos publicados — **11.886 páginas de livro** e
**1.712 aulas em slides (53.648 telas)**, com o LaTeX de tudo ao lado dos PDFs.

> **Republicado em 16/09/2026:** o assunto **gerenciamento-de-projetos** ganhou
> uma edição nova — 55 documentos, livro de **336 páginas** e **25 aulas escritas
> à mão** (351 slides). A edição anterior, de 08/09/2026, foi substituída nesta
> linha do catálogo; os totais acima ainda são os da consolidação anterior e serão
> recalculados na próxima rodada de `publish-all.py`.

---

## Onde o material está

> **Os cursos não são versionados neste repositório.** `courses/` está no
> `.gitignore`: a ferramenta é pública, o material produzido pertence a quem o
> gerou e circula onde cada um decidir.

Os cursos desta tabela foram produzidos pela **Andrada's Dev** e são
distribuídos em PDF — livro e aulas. O endereço de distribuição entra aqui
assim que a publicação estiver no ar.

| Peça | Onde | Situação |
|---|---|---|
| Livros em PDF | Andrada's Dev — link no site da empresa | a publicar |
| Aulas em PDF | Andrada's Dev — link no site da empresa | a publicar |
| Markdown de origem | repositório próprio, ainda não definido como público ou privado | em decisão |

Quem clonar esta fábrica **não recebe curso nenhum** — recebe a máquina de
produzi-los. Ver [`README.md`](README.md) e [`docs/`](docs/README.md).

---

## Como ler a tabela

- **Assunto** — o nome da pasta, em kebab-case.
- **Gerado em** — a data de geração, que faz parte do nome da pasta. Material
  técnico envelhece: a data diz contra qual realidade o curso foi escrito.
- **Docs** — arquivos Markdown de material, sem contar a publicação.
- Todos os cursos listados têm os blocos **A a F completos**: porta de entrada,
  núcleo, prática, economia, fontes e publicação. A estrutura está no
  [`CLAUDE.md`](CLAUDE.md).

---

## Os 47 assuntos

| Assunto | Gerado em | Docs | O que cobre |
|---|---|---|---|
| **apis** | 11/08/2026 | 26 | O que é uma API, o que é REST de verdade (as 6 restrições de Fielding, HATEOAS, o modelo de Richardson), quais estilos existem — REST, RPC, gRPC, GraphQL, SOAP… |
| **docker** | 11/08/2026 | — | O que é um container e o que é o Docker, como usar (imagens, volumes, redes, Compose), como funciona por dentro (namespaces, cgroups, OverlayFS, runtime)… |
| **postgresql** | 11/08/2026 | — | O banco de dados relacional: o que é e o que é "relacional", SQL do básico ao avançado (JOINs, janelas, CTEs), modelagem e normalização, tipos ricos (JSONB, arrays… |
| **salesforce** | 11/08/2026 | 27 | O CRM e a plataforma: o que é, como se começa do zero, como funciona por dentro (modelo de dados, segurança em cinco camadas, Apex, LWC, integração… |
| **bert** | 12/08/2026 | 33 | O modelo que lê (e não escreve): o que é BERT, por que não é um LLM pequeno, como instalar, afinar, avaliar e servir em produção com latência de milissegundos. |
| **ethical-hacking** | 12/08/2026 | 33 | O que é hacking ético, como se entra na carreira e o passo a passo real. |
| **agentes-de-ia** | 13/08/2026 | 24 | O que são agentes de IA e como usar o Claude Code — do "imagine que você contrata um cozinheiro" à indecidibilidade de Rice. |
| **commits-assinados** | 13/08/2026 | 26 | Como configurar commits assinados por GPG ou SSH no GitHub, passo a passo — e o que o selo Verified realmente prova. |
| **sql** | 13/08/2026 | 32 | A linguagem: o que é SQL, para que serve e como usar — do primeiro SELECT à cota AGM e aos limites de expressividade. |
| **testes-automatizados** | 13/08/2026 | 25 | O que são testes automatizados e o que são testes unitários — em Python e em JavaScript, lado a lado. |
| **jwt** | 14/08/2026 | 29 | O que é um JSON Web Token, como se usa, como funciona por dentro — e quando não usar. Da analogia da pulseira de parque ao ML-DSA pós-quântico. |
| **optimistic-locking** | 14/08/2026 | 27 | Controle de concorrência otimista: como dois usuários editam o mesmo dado sem que um apague o trabalho do outro, sem travar nada e sem ninguém esperar. |
| **portas-de-rede** | 14/08/2026 | 27 | Como se verificam as portas de uma máquina, quais são elas, para que servem, quais os protocolos, e como testá-las e descobri-las. |
| **portas-logicas** | 14/08/2026 | 22 | As peças com que todo computador é feito: o que é uma porta lógica, quantas existem e para que servem, como um transistor vira porta, como portas viram somador… |
| **power-bi** | 14/08/2026 | 34 | A plataforma de BI da Microsoft: o que é, como funciona por dentro, como se trabalha com ela e o que ela pode (e não pode) fazer. |
| **tabela-arp** | 14/08/2026 | 27 | O que é a tabela ARP: a lista IP→MAC que cada máquina mantém para entregar pacotes no próprio segmento, e o protocolo de 1982 que a preenche. |
| **hospedagem-de-aplicacoes-web** | 18/08/2026 | 27 | Onde e como hospedar um sistema web de quatro peças — frontend, backend, PostgreSQL e Redis. |
| **criptografia** | 19/08/2026 | — | O que é criptografia, como funciona por dentro e como se começa do zero. Do bilhete na sala de aula ao acordo híbrido pós-quântico X25519+ML-KEM-768. |
| **engenharia-de-prompt** | 19/08/2026 | 28 | O que é um Engenheiro de Prompt, o que o cargo realmente exige em 2026, e como se tornar um do zero. |
| **processamento-de-sinais** | 19/08/2026 | 36 | Do sinal analógico ao espectro na tela: amostragem e Nyquist, Fourier, DFT/FFT, transformada Z, filtros FIR e IIR, análise espectral e janelas. |
| **engenharia-de-software-com-ia** | 20/08/2026 | 35 | "O que é um dev que sabe usar IA?" — a resposta desenvolvida, justificada e transformada em prática. |
| **estatistica-descritiva** | 20/08/2026 | — | O que são média, mediana, desvio padrão e erro — e o que cada uma significa na realidade. |
| **investimentos-brasil** | 20/08/2026 | — | Onde colocar dinheiro no Brasil de hoje, do zero absoluto à teoria de apreçamento. |
| **ingles-do-basico-ao-fluente** | 31/08/2026 | 29 | Curso completo de inglês, do "não sei dizer meu nome" ao nível de pesquisa em aquisição de segunda língua. |
| **tls** | 31/08/2026 | 28 | O protocolo que põe o S no HTTPS. Da analogia do envelope lacrado até a análise formal do handshake: certificados X.509 campo a campo, a PKI e por que ela é o elo… |
| **uv-python** | 31/08/2026 | 28 | O uv, o gerenciador de pacotes e projetos Python escrito em Rust pela Astral — do primeiro comando à prova de que resolver dependências é NP-completo. |
| **pentest** | 01/09/2026 | 38 | Pentest — teste de intrusão, de invasão, *penetration test*: o serviço profissional de atacar um sistema com autorização por escrito para descobrir, provar e… |
| **streamlit** | 02/09/2026 | 35 | Como transformar um script Python numa aplicação web — e como fazer isso bem. |
| **claude-code** | 03/09/2026 | 30 | O agente de programação de linha de comando da Anthropic: o que é um agente (laço agêntico, contexto, ferramentas), todos os comandos (CLI, barra, atalhos… |
| **curso-docker** | 03/09/2026 | 21 | Curso prático aplicado, complementar ao assunto docker. Enquanto docker/ cobre a teoria completa (namespaces, cgroups, OverlayFS, runtime, registries), este aqui… |
| **engenharia-reversa** | 03/09/2026 | 33 | Como um programa executável guarda segredos, e como um humano recupera a lógica que o compilador escondeu. |
| **mcp** | 03/09/2026 | 30 | Model Context Protocol — o padrão aberto que conecta aplicações de IA a ferramentas, dados e sistemas. |
| **n8n** | 03/09/2026 | 31 | Automação de fluxos e orquestração de agentes de IA com n8n — da analogia da esteira de montagem ao limite teórico de por que *exactly-once* não existe. |
| **spa-single-page-application** | 03/09/2026 | — | O que é uma SPA, como funciona por dentro (roteamento, estado, renderização, dados), quando usar e quando não usar, e as arquiteturas híbridas (SSR, ilhas, RSC) que… |
| **variaveis-de-ambiente-e-segredos** | 03/09/2026 | 30 | O que fazer com o .env quando o sistema sai do desenvolvimento e vai para o cliente. |
| **desenvolvimento-de-sistemas** | 08/09/2026 | 42 | Qual é o fluxo real do desenvolvimento de um sistema — as 33 etapas na ordem correta, da dor do cliente ao descomissionamento. |
| **diagramas-uml-e-modelagem-de-dados** | 08/09/2026 | 33 | Como desenhar sistemas antes de construí-los — e ler o desenho dos outros. |
| **fisica-eletrica** | 08/09/2026 | 30 | Amperagem, tensão, potência, carga — o que cada uma significa na realidade física, quem manda em quem num circuito, e por que tensão errada queima e corrente… |
| **redes-de-computadores** | 08/09/2026 | 35 | Como funciona a rede mundial de computadores, quais são os protocolos, o que significam e quais são as regras de conexão. |
| **sistema-operacional-linux** | 08/09/2026 | 34 | Do primeiro comando à administração de servidores de produção — e do prompt até o kernel. |
| **triggers-buffers-e-primitivas-de-sistemas** | 08/09/2026 | 34 | O vocabulário que ninguém explica: gatilho é como um sistema decide *quando* agir; buffer é como ele lida com o fato de que as coisas não acontecem na mesma… |
| **apis-de-llm-gratuitas** | 09/09/2026 | 26 | Como usar inteligência artificial conversacional por API sem pagar nada — e onde o gratuito acaba. |
| **discord-py-e-bots-inteligentes** | 09/09/2026 | 32 | Criar bots para o Discord com discord.py 2.7.1 — e ligar neles uma IA generativa gratuita (Groq, Google Gemini ou Ollama rodando na própria máquina). Do "porteiro… |
| **freelancer-desenvolvimento-web** | 09/09/2026 | 28 | Como conseguir trabalhos freelancer de desenvolvimento web, do júnior ao sênior, com investimento de R$ 0: canais, plataformas (com taxas datadas), prospecção… |
| **bolha-da-ia** | 13/09/2026 | 26 | Estamos numa bolha de inteligência artificial? O curso troca a pergunta binária por um procedimento: quatro riscos separados (valuation, crédito, energia… |
| **regex** | 16/09/2026 | 30 | Expressões regulares do zero absoluto ao nível de pesquisa. Do "Ctrl+F que entende formato" até a prova de que parênteses balanceados não formam linguagem regular. |
| **gerenciamento-de-projetos** | 16/09/2026 | 55 | Como iniciar um projeto, o passo a passo, os documentos iniciais e de onde se parte — e depois tudo o que vem a seguir: escopo, cronograma, custo, risco, pessoas, contrato, ágil… |

---

## Nota sobre as aulas

Os decks da primeira rodada (46 cursos) foram **gerados a partir do material** e
estão marcados como rascunho no cabeçalho: cobrem 100% dos arquivos e servem de
base, mas apresentar em sala pede revisão.

Cursos novos nascem com as aulas **escritas à mão**: o primeiro assim foi o
**regex** (20 aulas) e o segundo é o **gerenciamento-de-projetos** (25 aulas,
351 slides), ambos de 16/09/2026. A diferença entre as duas coisas está em
[`docs/06-lectures.md`](docs/06-lectures.md).

---

## Acrescentar um curso a este catálogo

Uma linha por curso, na ordem da data de geração. O agente que produz o curso
atualiza esta tabela na mesma sessão — um curso que ninguém encontra é um curso
que não existe.

| Campo | De onde sai |
|---|---|
| Assunto | o nome da pasta, sem a data |
| Gerado em | a data no nome da pasta |
| Docs | `find courses/<pasta> -name '*.md' -not -path '*97-publicacao*' \| wc -l` |
| O que cobre | a primeira frase do `00-MAPA.md` |

Números de páginas e de aulas saem do relatório de publicação:

```bash
python3 tools/publish-all.py courses --jobs 6
cat courses/.publication.json
```
