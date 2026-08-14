#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrate_to_blob.py - Script de migracao one-shot.

Le os 3 arquivos JSON de trilhas do disco local e faz upload de cada um
para o Vercel Blob, preservando todo o conteudo ja cadastrado.

Pre-requisito:
  - Arquivo .env na raiz do projeto com BLOB_READ_WRITE_TOKEN preenchido.
  - Blob Store ja criado no dashboard da Vercel (aba Storage do projeto).

Uso:
  python migrate_to_blob.py

Execute apenas uma vez. Reexecutar e seguro: o upload sobrescreve o blob
existente com o mesmo conteudo (idempotente).
"""

import json
import sys
from pathlib import Path

# Garante que o pacote `app` esta no Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

load_dotenv()  # carrega .env antes de importar blob_storage

from app.blob_storage import blob_put  # noqa: E402

# ------------------------------------------------------------------------------
TRILHAS_DIR = Path(__file__).resolve().parent / "app" / "data" / "trilhas"
SLUGS = ("autocad", "solidworks", "excel")
# ------------------------------------------------------------------------------


def main() -> None:
    print("=" * 60)
    print("  Migracao de trilhas: JSON local -> Vercel Blob")
    print("=" * 60)
    print()

    success = 0
    errors = 0

    for slug in SLUGS:
        local_file = TRILHAS_DIR / f"{slug}.json"

        if not local_file.exists():
            print(f"[AVISO] {slug}.json nao encontrado em {TRILHAS_DIR} - pulando.")
            errors += 1
            continue

        # Le o arquivo local
        try:
            data = json.loads(local_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[ERRO] Falha ao ler {slug}.json: {exc}")
            errors += 1
            continue

        # Faz upload para o Vercel Blob
        try:
            url = blob_put(f"trilhas/{slug}.json", data)
            total_aulas = sum(
                len(m.get("aulas", [])) for m in data.get("modulos", [])
            )
            total_modulos = len(data.get("modulos", []))
            print(f"[OK] {slug}.json -> Blob atualizado")
            print(f"     Modulos: {total_modulos}  |  Aulas: {total_aulas}")
            print(f"     URL: {url}")
        except Exception as exc:
            print(f"[ERRO] Falha ao fazer upload de {slug}.json: {exc}")
            errors += 1
            continue

        success += 1
        print()

    print("-" * 60)
    print(f"  Resultado: {success} migrado(s) com sucesso, {errors} erro(s).")
    print("-" * 60)

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
