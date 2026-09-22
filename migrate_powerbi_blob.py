"""
migrate_powerbi_blob.py — Atualiza o blob trilhas/powerbi.json no Vercel
com a nova estrutura de 1 módulo único "Tudo sobre Power BI".

Execute com: python migrate_powerbi_blob.py
Requer BLOB_READ_WRITE_TOKEN no .env
"""
import json
import sys
from pathlib import Path

# Garante que o path do projeto está no sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv()

from app.blob_storage import blob_get, blob_put

SLUG = "powerbi"

def main():
    print(f"[INFO] Carregando trilha atual do Blob: trilhas/{SLUG}.json ...")
    current = blob_get(f"trilhas/{SLUG}.json")

    if current:
        print(f"[INFO] Trilha encontrada: {current.get('nome')}")
        print(f"[INFO] Módulos atuais: {[m['titulo'] for m in current.get('modulos', [])]}")
        # Preserva aulas existentes do antigo módulo-01 (se houver)
        aulas_existentes = []
        for m in current.get("modulos", []):
            aulas_existentes.extend(m.get("aulas", []))
        print(f"[INFO] Total de aulas encontradas (serão preservadas): {len(aulas_existentes)}")
    else:
        print("[AVISO] Trilha não encontrada no Blob — será criada do zero.")
        aulas_existentes = []

    nova_trilha = {
        "id": "powerbi",
        "slug": "powerbi",
        "nome": "Power BI",
        "descricao": (
            "Estudos e projetos práticos em Microsoft Power BI: importação e tratamento de dados "
            "com Power Query (ETL), modelagem dimensional e construção de relatórios e dashboards "
            "interativos de alta performance."
        ),
        "categoria": "Análise de Dados",
        "icone": "fa-chart-pie",
        "cor": "amarelo",
        "modulos": [
            {
                "id": "modulo-01",
                "numero": 1,
                "titulo": "Tudo sobre Power BI",
                "aulas": aulas_existentes,
            }
        ],
    }

    print(f"\n[INFO] Salvando nova estrutura no Blob...")
    url = blob_put(f"trilhas/{SLUG}.json", nova_trilha)
    print(f"[OK] Blob atualizado com sucesso!")
    print(f"[OK] URL: {url}")
    print(f"\n[RESUMO] Estrutura salva:")
    print(json.dumps(nova_trilha, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
