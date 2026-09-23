"""
database.py — Camada de acesso aos dados do portfólio (Trilhas de Aprendizado).

Persistência:
  - Trilhas: Vercel Blob — trilhas/{slug}.json (autocad, solidworks, excel, powerbi, overleaf)
             → leitura/escrita via blob_storage.blob_get / blob_put
             → fallback local para desenvolvimento: app/data/trilhas/{slug}.json
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Optional

from app.blob_storage import blob_get, blob_put

# ──────────────────────────────────────────────────────────────────────────────
# Caminhos base
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
TRILHAS_DIR = BASE_DIR / "data" / "trilhas"
STATIC_DIR  = BASE_DIR / "static"


# ──────────────────────────────────────────────────────────────────────────────
# Utilitários públicos (importados pelos routers)
# ──────────────────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Gera um slug URL-friendly a partir de texto em português."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def youtube_to_embed(url: str) -> str:
    """Converte qualquer URL do YouTube para o formato nocookie embed."""
    if not url or not url.strip():
        return ""
    url = url.strip()
    # youtu.be/ID
    m = re.search(r"youtu\.be/([a-zA-Z0-9_-]+)", url)
    if m:
        return f"https://www.youtube-nocookie.com/embed/{m.group(1)}"
    # youtube.com/watch?v=ID
    m = re.search(r"[?&]v=([a-zA-Z0-9_-]+)", url)
    if m:
        return f"https://www.youtube-nocookie.com/embed/{m.group(1)}"
    # Já é embed — normaliza para nocookie
    m = re.search(r"embed/([a-zA-Z0-9_-]+)", url)
    if m:
        return f"https://www.youtube-nocookie.com/embed/{m.group(1)}"
    return url


# ──────────────────────────────────────────────────────────────────────────────
# API pública — Trilhas de Aprendizado (excel / powerbi / autocad / solidworks / overleaf)
# ──────────────────────────────────────────────────────────────────────────────

def get_trail_data(slug: str) -> Optional[dict]:
    """
    Carrega os dados de uma trilha a partir do Vercel Blob (trilhas/{slug}.json).
    Retorna None se o blob não existir ou o conteúdo for inválido.
    Slugs válidos: 'excel', 'autocad', 'solidworks'.
    """
    return _load_trail(slug)


def calculate_trail_progress(trail: dict) -> dict:
    """
    Calcula estatísticas de progresso de uma trilha.
    Retorna dict com: total_aulas, concluidas, percentual (0-100).
    Nota: 'concluida' no JSON é o estado padrão; o progresso real é
    gerenciado no cliente via localStorage e injetado no template via JS.
    """
    total = 0
    concluidas = 0
    for modulo in trail.get("modulos", []):
        for aula in modulo.get("aulas", []):
            total += 1
            if aula.get("concluida", False):
                concluidas += 1
    percentual = round((concluidas / total) * 100) if total > 0 else 0
    return {
        "total_aulas": total,
        "concluidas": concluidas,
        "percentual": percentual,
    }


# ──────────────────────────────────────────────────────────────────────────────
# API pública — CRUD de Aulas nas Trilhas de Aprendizado
# ──────────────────────────────────────────────────────────────────────────────

VALID_TRAILS = ("excel", "powerbi", "autocad", "solidworks", "overleaf")


def _load_trail(slug: str) -> Optional[dict]:
    """
    Carrega o JSON de uma trilha.
    Prioriza o Vercel Blob (produção). Em caso de falha ou desenvolvimento offline,
    utiliza o arquivo JSON local em app/data/trilhas/{slug}.json.
    """
    if slug not in VALID_TRAILS:
        return None

    try:
        data = blob_get(f"trilhas/{slug}.json")
        if data:
            return data
    except Exception as exc:
        print(f"[AVISO] Não foi possível carregar trilha {slug} do Blob: {exc}")

    # Fallback para arquivo JSON local
    local_file = TRILHAS_DIR / f"{slug}.json"
    if local_file.exists():
        try:
            return json.loads(local_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def _persist_trail(slug: str, trail: dict) -> None:
    """
    Persiste o objeto de trilha no Vercel Blob (trilhas/{slug}.json)
    e sincroniza com o arquivo JSON local (backup e desenvolvimento local).
    """
    # 1. Salva localmente (garante backup imediato)
    try:
        TRILHAS_DIR.mkdir(parents=True, exist_ok=True)
        local_file = TRILHAS_DIR / f"{slug}.json"
        local_file.write_text(
            json.dumps(trail, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        print(f"[AVISO] Falha ao salvar trilha localmente em {slug}.json: {exc}")

    # 2. Salva no Vercel Blob
    try:
        blob_put(f"trilhas/{slug}.json", trail)
    except Exception as exc:
        print(f"[AVISO] Falha ao sincronizar trilha {slug} no Blob: {exc}")



def get_all_trails_summary() -> list[dict]:
    """
    Retorna lista com resumo de todas as trilhas (para dashboard admin).
    Cada item: { slug, nome, icone, cor, total_modulos, total_aulas }.
    """
    summaries = []
    for slug in VALID_TRAILS:
        trail = _load_trail(slug)
        if not trail:
            continue
        total_aulas = sum(len(m.get("aulas", [])) for m in trail.get("modulos", []))
        summaries.append({
            "slug":          trail.get("slug", slug),
            "nome":          trail.get("nome", slug.capitalize()),
            "icone":         trail.get("icone", "fa-book"),
            "cor":           trail.get("cor", "cinza"),
            "total_modulos": len(trail.get("modulos", [])),
            "total_aulas":   total_aulas,
        })
    return summaries


def save_aula_to_trail(trail_slug: str, modulo_id: str, aula: dict) -> Optional[dict]:
    """
    Cria (sem 'id') ou atualiza (com 'id') uma aula dentro de um módulo da trilha.
    Retorna a aula salva, ou None se trilha/módulo não encontrado.
    """
    trail = _load_trail(trail_slug)
    if not trail:
        return None

    modulos = trail.get("modulos", [])
    target_modulo = next((m for m in modulos if m["id"] == modulo_id), None)
    if not target_modulo:
        return None

    if not aula.get("id"):
        # Nova aula
        aula["id"] = str(uuid.uuid4())
        target_modulo.setdefault("aulas", []).append(aula)
    else:
        # Se estiver em outro módulo, remove do módulo anterior
        for m in modulos:
            if m["id"] != modulo_id and "aulas" in m:
                m["aulas"] = [a for a in m["aulas"] if a.get("id") != aula["id"]]

        aulas = target_modulo.setdefault("aulas", [])
        # Atualizar no módulo alvo
        for i, a in enumerate(aulas):
            if a.get("id") == aula["id"]:
                aulas[i] = aula
                break
        else:
            aulas.append(aula)

    _persist_trail(trail_slug, trail)
    return aula


def delete_aula_from_trail(trail_slug: str, modulo_id: str, aula_id: str) -> bool:
    """
    Remove uma aula de um módulo da trilha e apaga seus arquivos de download.
    Retorna True se removida com sucesso.
    """
    trail = _load_trail(trail_slug)
    if not trail:
        return False

    modulos = trail.get("modulos", [])
    target_modulo = next((m for m in modulos if m["id"] == modulo_id), None)
    if not target_modulo:
        return False

    aulas = target_modulo.get("aulas", [])
    original_len = len(aulas)
    target_aula = next((a for a in aulas if a["id"] == aula_id), None)

    if not target_aula:
        return False

    # Remove arquivos de download do servidor se existirem localmente
    try:
        aula_files_dir = STATIC_DIR / "documents" / "trilhas" / trail_slug / aula_id
        if aula_files_dir.exists():
            shutil.rmtree(aula_files_dir, ignore_errors=True)
    except Exception:
        pass

    target_modulo["aulas"] = [a for a in aulas if a["id"] != aula_id]

    if len(target_modulo["aulas"]) < original_len:
        _persist_trail(trail_slug, trail)
        return True
    return False


def reorder_aulas_in_modulo(trail_slug: str, modulo_id: str, ordered_ids: list[str]) -> bool:
    """
    Reordena as aulas de um módulo de acordo com a lista de IDs fornecida.
    Retorna True se bem-sucedido.
    """
    trail = _load_trail(trail_slug)
    if not trail:
        return False

    modulos = trail.get("modulos", [])
    target_modulo = next((m for m in modulos if m["id"] == modulo_id), None)
    if not target_modulo:
        return False

    aulas = target_modulo.get("aulas", [])
    aulas_by_id = {a["id"]: a for a in aulas}

    reordered = [aulas_by_id[aid] for aid in ordered_ids if aid in aulas_by_id]
    # Inclui aulas que não estavam na lista (segurança)
    remaining = [a for a in aulas if a["id"] not in set(ordered_ids)]
    target_modulo["aulas"] = reordered + remaining

    _persist_trail(trail_slug, trail)
    return True


def add_modulo_to_trail(trail_slug: str, titulo: str) -> Optional[dict]:
    """
    Adiciona um novo módulo/seção a uma trilha.
    Retorna o módulo criado, ou None se trilha inválida.
    """
    trail = _load_trail(trail_slug)
    if not trail:
        return None

    modulos = trail.setdefault("modulos", [])
    novo_numero = len(modulos) + 1
    novo_modulo = {
        "id":     f"modulo-{novo_numero:02d}",
        "numero": novo_numero,
        "titulo": titulo.strip(),
        "aulas":  [],
    }
    modulos.append(novo_modulo)
    _persist_trail(trail_slug, trail)
    return novo_modulo


def get_lesson_context(trail_slug: str, aula_id: str) -> Optional[dict]:
    """
    Retorna todo o contexto necessário para renderizar a página de reprodução da aula:
    - trail: dados completos da trilha
    - modulo: módulo ao qual a aula pertence
    - aula: dados da aula (com embedUrl e campos enriquecidos)
    - prev_aula: aula anterior na trilha sequencial (ou None)
    - next_aula: próxima aula na trilha sequencial (ou None)
    - progress: progresso da trilha
    """
    trail = _load_trail(trail_slug)
    if not trail:
        return None

    all_lessons = []
    target_modulo = None
    target_aula = None

    for mod in trail.get("modulos", []):
        for a in mod.get("aulas", []):
            item = {"modulo": mod, "aula": a}
            all_lessons.append(item)
            if a.get("id") == aula_id:
                target_modulo = mod
                target_aula = a

    if not target_aula:
        return None

    # Prepara URL de embed do YouTube (formato nocookie)
    target_aula["embedUrl"] = youtube_to_embed(target_aula.get("urlYoutube", ""))

    # Localiza aula anterior e próxima
    idx = next(i for i, item in enumerate(all_lessons) if item["aula"]["id"] == aula_id)
    prev_item = all_lessons[idx - 1] if idx > 0 else None
    next_item = all_lessons[idx + 1] if idx < len(all_lessons) - 1 else None

    return {
        "trail": trail,
        "modulo": target_modulo,
        "aula": target_aula,
        "prev_aula": prev_item["aula"] if prev_item else None,
        "prev_modulo": prev_item["modulo"] if prev_item else None,
        "next_aula": next_item["aula"] if next_item else None,
        "next_modulo": next_item["modulo"] if next_item else None,
        "progress": calculate_trail_progress(trail),
    }


