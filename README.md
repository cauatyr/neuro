# neuro — scraping + transcrição do perfil @neuroglobe

Projeto que **baixa todas as fotos** do perfil do Instagram
[@neuroglobe](https://www.instagram.com/neuroglobe/) (conteúdo de neurociência/psicologia)
e **transcreve o texto que aparece dentro das imagens** para um arquivo Markdown único, em
ordem cronológica.

O resultado da transcrição está em [`neuroglobe.md`](./neuroglobe.md).

---

## Estado atual

| Item | Status |
|---|---|
| Fotos baixadas | ✅ **3.124 imagens** de **604 posts** (852 posts no total; os outros eram vídeos, ignorados) |
| Transcrição | 🟨 **1ª metade — 312 de 604 posts** (os mais antigos, out/2024 → ~fev/2026) |
| Publicado aqui | `neuroglobe.md` com a 1ª metade |
| Falta | 2ª metade da transcrição (posts mais recentes) |

> A transcrição foi pausada na metade a pedido, e por conta do limite de sessão do
> ambiente de IA usado. É retomável (ver "Como retomar" no fim).

---

## Como funciona o scraping (visão geral)

O pipeline tem 4 etapas, cada uma com um script em [`scripts/`](./scripts):

```
[1] 01_download.py        Instagram  ->  posts/*.jpg      (instaloader + cookies)
[2] 02_make_batches.py    posts/     ->  batches/*.json   (agrupa por post, em lotes)
[3] agentes de visão      batches/   ->  parts/*.md       (lê imagens, transcreve texto)
[4] 04_assemble.py        parts/     ->  neuroglobe.md    (junta tudo, cronológico)
```

### 1. Download — `01_download.py`
Usa a biblioteca **[instaloader](https://instaloader.github.io/)**.

**O desafio:** o Instagram hoje **bloqueia o acesso anônimo** (responde `403 Forbidden`) e,
quando se tenta login por usuário/senha de fora do navegador, cai num **checkpoint de
segurança em loop**. Tentar ler os cookies automaticamente do Edge/Chrome também falha, porque
os navegadores Chromium modernos usam **app-bound encryption** (`Unable to get key for cookie
decryption`).

**A solução que funcionou:** reaproveitar a **sessão já logada no navegador**, copiando 3
cookies manualmente (via DevTools) e injetando-os no instaloader:
- `sessionid`, `csrftoken`, `ds_user_id`

Isso pula todo o fluxo de checkpoint, porque a sessão do navegador já foi verificada. O script
também é **resiliente e retomável**: um `403`/`503` passageiro em uma imagem não derruba o
processo (tenta de novo, depois pula), e como o instaloader ignora arquivos já baixados, basta
rodar de novo que ele continua de onde parou.

### 2. Lotes — `02_make_batches.py`
Cada post pode ser um carrossel com vários slides (`..._UTC_1.jpg`, `..._UTC_2.jpg`, ...).
O script agrupa as imagens por post, ordena cronologicamente e divide em **lotes de 12 posts**,
gravando um `batches/batch_NNN.json` por lote.

### 3. Transcrição — agentes de visão
Não é OCR tradicional. Cada lote é entregue a um **agente de visão** (um LLM multimodal — no
caso, subagentes do Claude Code no modelo Sonnet) que **abre cada imagem, lê o texto e escreve**
`parts/part_NNN.md`. As instruções exatas dadas a cada agente estão em
[`scripts/03_transcribe_instructions.md`](./scripts/03_transcribe_instructions.md).

Rodar vários agentes **em paralelo** (cada um com seu lote) é o que torna ~3.000 imagens viável.
**Lição prática:** ~12 agentes simultâneos é o teto saudável; ~25 de uma vez começa a bater
rate-limit do servidor.

### 4. Montagem — `04_assemble.py`
Concatena todos os `parts/part_NNN.md` em ordem no `neuroglobe.md` final.

---

## Formato da saída

Uma seção por post; um bloco por slide do carrossel:

```markdown
## 2024-10-19 17:35 UTC

**Slide 1:**
Best Herbs For Brain Health

Bacopa Monnieri
Boosts memory and cognitive function
...
```

---

## Como rodar

### Requisitos
```bash
pip install -r requirements.txt
```

### 1) Capturar os cookies (uma vez)
1. Faça login em `instagram.com` no navegador.
2. `F12` → aba **Application/Aplicativo** → **Cookies** → `https://www.instagram.com`
3. Copie os valores de `sessionid`, `csrftoken`, `ds_user_id`.
4. Exponha como variáveis de ambiente (⚠️ nunca coloque no código):

```powershell
# Windows PowerShell
$env:IG_SESSIONID  = "..."
$env:IG_CSRFTOKEN  = "..."
$env:IG_DS_USER_ID = "..."
```
```bash
# Linux / macOS
export IG_SESSIONID=...  IG_CSRFTOKEN=...  IG_DS_USER_ID=...
```

### 2) Rodar o pipeline
```bash
python scripts/01_download.py neuroglobe ./posts
python scripts/02_make_batches.py ./posts ./batches 12
# etapa 3: rodar os agentes de visão sobre cada batches/*.json -> parts/part_NNN.md
python scripts/04_assemble.py ./parts ./neuroglobe.md
```

> A **etapa 3** depende de um agente multimodal (Claude Code / API de visão). O `.md` publicado
> aqui foi gerado com subagentes do Claude Code. Você pode adaptar para a API de sua preferência
> usando as instruções em `scripts/03_transcribe_instructions.md`.

---

## Estrutura

```
neuro/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ neuroglobe.md            # <- resultado da transcrição (1ª metade)
└─ scripts/
   ├─ 01_download.py                 # download via instaloader + cookies
   ├─ 02_make_batches.py             # agrupa posts em lotes
   ├─ 03_transcribe_instructions.md  # instruções dadas aos agentes de visão
   └─ 04_assemble.py                 # junta as partes no .md final
```

As pastas `posts/`, `batches/` e `parts/` são geradas localmente e **não** vão para o Git
(ver `.gitignore`) — contêm dados pesados e conteúdo de terceiros.

---

## Como retomar a 2ª metade
Já existem as partes dos lotes 000–029, 032, 034, 035. Faltam os lotes **030, 031, 033,
036–050**. Basta rodar a etapa 3 (agentes de visão) só nesses lotes, depois `04_assemble.py`
para regerar o `neuroglobe.md` completo (604 posts) e commitar.

---

## Aviso

Uso pessoal / de pesquisa. As imagens originais e o texto são de autoria do perfil
**@neuroglobe**; este repositório guarda apenas os scripts e a transcrição textual, não as
imagens. Respeite os Termos de Uso do Instagram e os direitos do autor do conteúdo.

O `sessionid` do Instagram é **sensível** (equivale a estar logado na conta). Nunca o coloque no
código nem o commite; faça logout para invalidá-lo quando terminar.
