# -*- coding: utf-8 -*-
"""
02_make_batches.py — Agrupa as imagens baixadas em "lotes" de posts para a transcrição.

Cada post do Instagram pode ser um carrossel com vários slides. Os arquivos vêm
nomeados como AAAA-MM-DD_HH-MM-SS_UTC_N.jpg (N = índice do slide). Este script:
  - agrupa as imagens por post (prefixo antes de _UTC),
  - ordena os posts cronologicamente e os slides por índice,
  - divide em lotes de BATCH_SIZE posts,
  - grava um JSON por lote em ./batches/batch_NNN.json

Cada lote é depois entregue a um agente de visão que lê as imagens e transcreve o texto.

Uso:
  python 02_make_batches.py [pasta_posts] [pasta_batches] [tamanho_lote]
"""
import os
import re
import sys
import json
import glob

POSTS_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "posts")
BATCH_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "batches")
BATCH_SIZE = int(sys.argv[3]) if len(sys.argv) > 3 else 12
os.makedirs(BATCH_DIR, exist_ok=True)

files = glob.glob(os.path.join(POSTS_DIR, "*.jpg"))

# agrupa por post
posts = {}
for f in files:
    base = os.path.splitext(os.path.basename(f))[0]
    m = re.match(r"^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_UTC)(?:_(\d+))?$", base)
    if not m:
        continue
    key = m.group(1)
    idx = int(m.group(2)) if m.group(2) else 0
    posts.setdefault(key, []).append((idx, f))

ordered_posts = sorted(posts.keys())            # cronológico
for k in posts:
    posts[k].sort(key=lambda t: t[0])           # slides em ordem

batches = []
for i in range(0, len(ordered_posts), BATCH_SIZE):
    chunk = ordered_posts[i:i + BATCH_SIZE]
    batches.append([{"post": p, "images": [f for _, f in posts[p]]} for p in chunk])

for bi, batch in enumerate(batches):
    with open(os.path.join(BATCH_DIR, f"batch_{bi:03d}.json"), "w", encoding="utf-8") as out:
        json.dump(batch, out, ensure_ascii=False, indent=1)

print(f"Posts com imagens: {len(ordered_posts)}")
print(f"Lotes gerados: {len(batches)} (de {BATCH_SIZE} posts cada)")
if ordered_posts:
    print(f"Período: {ordered_posts[0]}  ->  {ordered_posts[-1]}")
