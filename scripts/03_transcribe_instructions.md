# 03 — Instruções de transcrição (dadas a cada agente de visão)

A transcrição não é OCR tradicional: cada lote (`batches/batch_NNN.json`) é entregue a um
**agente de visão** (um LLM multimodal — aqui foram subagentes do Claude Code, modelo Sonnet)
que abre cada imagem, lê o texto e grava `parts/part_NNN.md`. Estas são as instruções exatas
passadas a cada agente:

---

Você vai transcrever o texto que aparece DENTRO de imagens de posts do Instagram
da conta @neuroglobe (conteúdo de neurociência/psicologia). O texto geralmente
está em INGLÊS — transcreva no idioma ORIGINAL, não traduza.

Você recebeu um número de lote NNN (três dígitos, ex.: 007).

## Passo 1 — Ler o lote
Leia `batches/batch_NNN.json`. É um array JSON. Cada item é um post com:
- `"post"`: timestamp (ex.: `"2025-03-04_17-34-54_UTC"`)
- `"images"`: lista ORDENADA de caminhos absolutos `.jpg` (os slides do carrossel)

## Passo 2 — Transcrever
Para CADA post, leia TODAS as imagens dele em ordem e transcreva FIELMENTE todo o
texto visível dentro da imagem (títulos, corpo, chamadas, números, listas). Regras:
- Preserve a estrutura e o idioma original. NÃO invente nada.
- IGNORE a marca d'água "@neuroglobe" — não a inclua na transcrição.
- Se uma imagem não tiver texto (foto/ilustração pura), escreva: `[imagem sem texto]`

## Passo 3 — Gravar o resultado
Grave (UTF-8) em `parts/part_NNN.md` neste formato (uma seção por post, na ordem do JSON):

```
## AAAA-MM-DD HH:MM UTC

**Slide 1:**
<texto do slide 1>

**Slide 2:**
<texto do slide 2>
```

- Converta o timestamp `2025-03-04_17-34-54_UTC` para o cabeçalho `## 2025-03-04 17:34 UTC`.
- Um `**Slide K:**` para cada imagem, na ordem.
- Uma linha em branco entre posts.

## Por que dividir em lotes e rodar em paralelo?
São ~600 posts / ~3.000 imagens. Rodar tudo num só contexto estoura o limite de tokens.
Dividindo em lotes de 12 posts e disparando vários agentes em paralelo, cada um escreve sua
própria parte e o custo/tempo fica administrável. **Lição prática:** ~12 agentes simultâneos é
o teto saudável; ~25 de uma vez começa a bater rate-limit do servidor.
