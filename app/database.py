"""
database.py — Camada de acesso aos dados dos projetos CAD.

Persistência em JSON local (app/data/cad_projects.json).
Estrutura preparada para migração futura para SQLite ou PostgreSQL
sem alterar routers ou templates.
"""

from __future__ import annotations

import json
import re
import shutil
import unicodedata
import uuid
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF — extração de páginas do PDF como imagens

# ──────────────────────────────────────────────────────────────────────────────
# Caminhos base
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent
DATA_FILE  = BASE_DIR / "data" / "cad_projects.json"
STATIC_DIR = BASE_DIR / "static"


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


def extract_pdf_sheets(pdf_path: Path, dest_dir: Path, dpi: int = 150) -> list[str]:
    """
    Extrai as páginas de um PDF como imagens PNG de alta qualidade.
    Retorna a lista de URLs estáticas relativas ao /static.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    static_urls: list[str] = []
    try:
        doc = fitz.open(str(pdf_path))
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi)
            filename = f"sheet_{i + 1}.png"
            pix.save(str(dest_dir / filename))
            # Converte o caminho absoluto para URL estática /static/...
            rel = str(dest_dir / filename).replace(str(STATIC_DIR), "").replace("\\", "/")
            static_urls.append(f"/static{rel}")
    except Exception:
        pass
    return static_urls


# ──────────────────────────────────────────────────────────────────────────────
# I/O interno do JSON
# ──────────────────────────────────────────────────────────────────────────────

def _load() -> list[dict]:
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _persist(projects: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(projects, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ──────────────────────────────────────────────────────────────────────────────
# API pública — CRUD
# ──────────────────────────────────────────────────────────────────────────────

def get_all_projects() -> list[dict]:
    """Retorna todos os projetos, mais recentes primeiro."""
    return sorted(_load(), key=lambda p: p.get("date", ""), reverse=True)


def get_project_by_slug(slug: str) -> Optional[dict]:
    for p in _load():
        if p.get("slug") == slug:
            return p
    return None


def get_project_by_id(project_id: str) -> Optional[dict]:
    for p in _load():
        if p.get("id") == project_id:
            return p
    return None


def save_project(project: dict) -> dict:
    """Cria (sem ID) ou atualiza (com ID) um projeto no JSON."""
    projects = _load()
    if not project.get("id"):
        project["id"] = str(uuid.uuid4())
        projects.append(project)
    else:
        for i, p in enumerate(projects):
            if p["id"] == project["id"]:
                projects[i] = project
                break
        else:
            projects.append(project)
    _persist(projects)
    return project


def delete_project(project_id: str) -> bool:
    """Remove o projeto do JSON e limpa todos os seus arquivos estáticos."""
    projects = _load()
    target = next((p for p in projects if p["id"] == project_id), None)
    if not target:
        return False

    slug = target.get("slug", "")
    if slug:
        # Remove pasta de folhas (sheet images)
        sheets_dir = STATIC_DIR / "images" / "cad" / slug
        if sheets_dir.exists():
            shutil.rmtree(sheets_dir, ignore_errors=True)
        # Remove imagem de capa
        covers_dir = STATIC_DIR / "images" / "cad" / "covers"
        for ext in ("png", "jpg", "jpeg", "webp", "gif"):
            cover = covers_dir / f"{slug}.{ext}"
            if cover.exists():
                cover.unlink(missing_ok=True)
        # Remove PDF
        pdf_dir = STATIC_DIR / "documents" / "cad"
        pdf_file = pdf_dir / f"{slug}.pdf"
        if pdf_file.exists():
            pdf_file.unlink(missing_ok=True)

    _persist([p for p in projects if p["id"] != project_id])
    return True
