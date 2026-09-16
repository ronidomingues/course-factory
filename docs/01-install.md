# 01 · Instalação

Nível: iniciante · Verificado em **16/09/2026**

A fábrica tem **duas** dependências de sistema: Python 3 e uma distribuição
LaTeX. O resto vem embarcado no repositório. Se a sua máquina já tem as duas,
pule para [02 · Primeiro curso](02-first-course.md).

---

## 1. O que precisa estar na máquina

| Peça | Versão mínima | Para quê | Obrigatório? |
|---|---|---|---|
| Python | 3.8 | os programas em `tools/` | **sim** |
| XeLaTeX (TeX Live / MacTeX / MiKTeX) | TeX Live 2021 | compilar o PDF | **sim** |
| `latexmk` | qualquer | resolver as passagens de compilação | recomendado |
| `pdfunite` (poppler) ou `gs` | qualquer | juntar as aulas num PDF único | recomendado |
| `pdfinfo` (poppler) | qualquer | contar páginas no relatório em lote | opcional |
| `fontconfig` (`fc-list`) | qualquer | detectar fonte instalada | opcional |
| `inkscape` | 1.x | converter logo SVG → PDF ao montar um kit de marca | opcional |
| Git | 2.x | clonar este repositório e o kit de marca | recomendado |

Sem LaTeX a fábrica ainda roda: ela gera o `.tex` e avisa que o PDF ficou
pendente. Não finge que saiu.

---

## 2. Instalar, por sistema operacional

### 2.1 Linux — Debian, Ubuntu, Mint, Pop!_OS

```bash
sudo apt update
sudo apt install -y python3 git texlive-xetex texlive-latex-extra \
                    texlive-lang-portuguese latexmk poppler-utils fontconfig
```

O que cada pacote faz, em uma linha:

- `texlive-xetex` — o motor que compila o PDF com fontes do sistema.
- `texlive-latex-extra` — `fancyhdr`, `eso-pic`, `needspace` e companhia.
- `texlive-lang-portuguese` — hifenização correta em português.
- `latexmk` — roda o motor quantas vezes o sumário exigir.
- `poppler-utils` — `pdfunite` e `pdfinfo`.

Verificação imediata:

```bash
python3 --version
# esperado: Python 3.8.x ou superior

xelatex --version | head -1
# esperado: XeTeX 3.141592653-2.6-0.999993 (TeX Live 2021) ou superior
```

Saiu diferente? Se `xelatex` diz `command not found`, o `texlive-xetex` não
entrou — repita a instalação e leia a saída do `apt`.

### 2.2 Linux — Fedora, RHEL, Rocky, Alma

```bash
sudo dnf install -y python3 git texlive-xetex texlive-collection-latexextra \
                    texlive-collection-langportuguese latexmk poppler-utils \
                    fontconfig
```

No Fedora, o `texlive-scheme-medium` resolve de uma vez, ao custo de ~1,5 GB:

```bash
sudo dnf install -y texlive-scheme-medium
```

### 2.3 macOS (Intel e Apple Silicon)

O caminho curto é o **BasicTeX** (~100 MB) mais os pacotes que faltam:

```bash
brew install --cask basictex
brew install poppler inkscape
eval "$(/usr/libexec/path_helper)"          # põe o TeX no PATH desta sessão
sudo tlmgr update --self
sudo tlmgr install latexmk fancyhdr eso-pic needspace collection-langportuguese
```

O caminho confortável é o **MacTeX** completo (~4 GB), que já traz tudo:

```bash
brew install --cask mactex
```

Apple Silicon e Intel usam o mesmo pacote; a diferença é só o tempo de
instalação. Verificação:

```bash
xelatex --version | head -1
which pdfunite
```

Se `xelatex` não aparece depois de instalar, **abra um terminal novo**: o
instalador escreve o PATH em `/etc/paths.d/TeX`, e isso só vale para sessões
abertas depois.

### 2.4 Windows

Há dois caminhos, e a recomendação é explícita: **use o WSL2**.

**Recomendado — WSL2 com Ubuntu.** Ganha-se o mesmo ambiente do Linux, os
mesmos comandos e os mesmos resultados. No PowerShell, como administrador:

```powershell
wsl --install -d Ubuntu
```

Reinicie, abra o Ubuntu e siga a seção [2.1](#21-linux--debian-ubuntu-mint-poposos).

**Nativo — MiKTeX.** Funciona, mas espere diferenças de PATH e de nome de
fonte. Instale o Python em <https://python.org/downloads> marcando *"Add
python.exe to PATH"*, e o MiKTeX em <https://miktex.org/download>. Depois, no
PowerShell:

```powershell
python --version
xelatex --version
```

O MiKTeX baixa pacote sob demanda na primeira compilação — a primeira publicação
demora e pede confirmação. Configure `MiKTeX Console → Settings → Always
install missing packages on-the-fly` para não travar no meio.

---

## 3. Clonar a fábrica

```bash
git clone <url-deste-repositorio> course-factory
cd course-factory
```

Nada a compilar, nada a instalar: `tools/md2book/` já vem dentro.

---

## 4. O teste que responde tudo

```bash
python3 tools/publish-course.py --doctor
```

Saída esperada em uma máquina pronta:

```
Brand kit: .../tools/course-factory-brand/template (template)
  latex      ok       .../template/latex
  ...
  md2book        ok       /usr/bin/python3 .../tools/md2book/md2book.py
  brand kit      ok       .../template (template)
  brand fonts    MISSING  kit ships none — it uses typefaces installed on the machine
  xelatex        ok       /usr/bin/xelatex
  latexmk        ok       /usr/bin/latexmk
  pdfunite/gs    ok       /usr/bin/pdfunite

This machine can publish a course on its own.
```

`brand fonts MISSING` no pré-molde **não é erro**: o molde usa a família Latin
Modern, que vem com o TeX Live, e por isso não distribui arquivo de fonte.

Se a última linha disser `Something essential is missing`, volte à seção do seu
sistema operacional. Erros literais e correções estão em
[07 · Problemas](07-troubleshooting.md).

---

## 5. Sem instalar nada

Para experimentar antes de decidir:

- **GitHub Codespaces / VS Code Dev Container** — abra o repositório e rode, no
  terminal do container, a instalação da seção 2.1. O container é Debian.
- **Docker**, se preferir não tocar na máquina:

  ```bash
  docker run --rm -it -v "$PWD":/work -w /work debian:12 bash -lc \
    'apt update && apt install -y python3 texlive-xetex texlive-latex-extra \
     texlive-lang-portuguese latexmk poppler-utils && \
     python3 tools/publish-course.py --doctor'
  ```

Os dois servem para ver a fábrica funcionando hoje e instalar depois.

---

## 6. Desinstalar

A fábrica não instala nada fora da própria pasta: apagar o clone a remove por
completo. O que sobra na máquina é o LaTeX, e ele se remove pelo gerenciador
de pacotes (`apt remove texlive-*`, `brew uninstall --cask mactex`, o
desinstalador do MiKTeX).

Uma exceção: com `--fonts repo`, a fábrica guarda uma cópia de fontes em
`.course-factory-fonts/` na raiz do repositório de cursos. É uma pasta comum;
apague-a quando não precisar mais.

---

## Autoteste

1. Quais são as **duas** dependências de sistema obrigatórias?
2. O que a fábrica faz quando não encontra o `xelatex`?
3. Por que `brand fonts MISSING` não é um problema no pré-molde?
4. Qual é o caminho recomendado no Windows, e por quê?
5. Onde ficam as fontes quando se usa `--fonts repo`?
