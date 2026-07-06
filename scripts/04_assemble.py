# -*- coding: utf-8 -*-
"""
04_assemble.py — Concatena as partes transcritas (parts/part_NNN.md) num .md único.

A transcrição de cada lote é gravada em parts/part_NNN.md por um agente de visão
(ver 03_transcribe_instructions.md). Este script junta tudo em ordem cronológica.

Uso:
  python 04_assemble.py [pasta_parts] [arquivo_saida]
"""
import os
import re
import sys
import glob

PARTS_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "parts")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "neuroglobe.md")

parts = sorted(glob.glob(os.path.join(PARTS_DIR, "part_*.md")))
if not parts:
    sys.exit("Nenhum part_*.md encontrado.")

header = (
    "# Neuroglobe — Transcrição das imagens\n\n"
    "Transcrição fiel do texto contido nas imagens dos posts do perfil "
    "[@neuroglobe](https://www.instagram.com/neuroglobe/), em ordem cronológica.\n\n---\n\n"
)

body = []
for p in parts:
    with open(p, encoding="utf-8") as fh:
        body.append(fh.read().strip())

with open(OUT, "w", encoding="utf-8") as out:
    out.write(header)
    out.write("\n\n".join(body))
    out.write("\n")

with open(OUT, encoding="utf-8") as fh:
    txt = fh.read()
posts = len(re.findall(r"^## ", txt, flags=re.M))
print(f"Montado: {OUT}")
print(f"Partes juntadas: {len(parts)} | Posts (##): {posts}")
