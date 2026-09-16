---
aula: Aula 00
curso: Curso de exemplo
subtitulo: O formato de um deck de aula
duracao: 20 min
---

# Como se escreve uma aula

## O formato

Cinco marcas de Markdown resolvem uma aula inteira.

### A gramática do deck

- `---` no topo: metadados da aula (`aula`, `curso`, `subtitulo`, `duracao`).
- `#` — o **título da aula**. Vira a capa.
- `##` — uma **parte da aula**. Vira tela de transição.
- `###` — **um slide**. É aqui que o conteúdo mora.
- `####` ou mais fundo — vira destaque em negrito dentro do slide.

```notas
Roteiro do professor: o bloco de notas não aparece na projeção.
Ele existe para quem vai falar, não para quem vai ver.
```

### O que cabe em um slide

Tudo o que o Markdown do curso já usa:

| Elemento | Funciona? | Observação |
|---|---|---|
| Lista | sim | é a forma padrão de um slide |
| Tabela | sim | vira `tabular`, sem quebra de página |
| Código | sim | todo slide é `fragile` |
| Citação | sim | filete na cor de destaque, à esquerda |
| Imagem | sim | caminho relativo ao próprio deck |

### Código na tela

```python
# O tamanho da fonte do bloco vem do slides.json.
def slide_bom(linhas: int) -> bool:
    """Um slide didático cabe na tela e cabe na memória."""
    return linhas <= 10
```

```notas
Mostre o código rodando antes de explicar linha a linha.
Quem viu funcionar aceita a explicação; o contrário raramente ocorre.
```

### Um slide que continua

Quando o assunto não cabe, a régua `---` continua o mesmo slide na tela
seguinte, com o mesmo título e a marca `(cont.)`.

---

- A continuação não é desculpa para empilhar texto.
- Se você precisa de três telas, provavelmente são três ideias.
- Três ideias merecem três títulos.

## A régua de qualidade

O que separa um slide didático de um documento projetado.

### As cinco regras

1. **Uma ideia por slide.** Se o título tem "e", são dois slides.
2. **No máximo dez linhas.** O gerador avisa quando você passa disso.
3. **O slide não é o texto da fala.** É a âncora visual dela.
4. **Todo número tem unidade e data.** `15 ms`, `US$ 20/mês em 15/09/2026`.
5. **Todo termo novo é definido na tela em que aparece.**

### O que o gerador confere

- Conta as linhas de cada slide e avisa quando passa do limite.
- Numera as telas e mostra o total no rodapé.
- Junta todas as aulas em um PDF único ao final.

> O aviso é aviso, não erro: quem decide o que cabe na aula é quem ensina.

### Encerramento

Cada deck termina sozinho: o tema acrescenta a tela de créditos, com o
autor, o orientador e o agente que escreveu o material. Você não precisa
escrever essa tela — mas precisa saber que ela existe.

```notas
Encerre convidando para o próximo passo concreto do curso:
o laboratório, o projeto-modelo, ou o próximo arquivo do material.
```
