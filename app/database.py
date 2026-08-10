"""
database.py — Camada de acesso aos dados dos projetos (CAD, Excel e Trilhas).

Persistência em JSON local:
  - app/data/cad_projects.json
  - app/data/excel_projects.json
  - app/data/trilhas/{slug}.json  (excel, autocad, solidworks)

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
BASE_DIR        = Path(__file__).resolve().parent
CAD_DATA_FILE   = BASE_DIR / "data" / "cad_projects.json"
EXCEL_DATA_FILE = BASE_DIR / "data" / "excel_projects.json"
TRILHAS_DIR     = BASE_DIR / "data" / "trilhas"
STATIC_DIR      = BASE_DIR / "static"

# Alias de compatibilidade para código legado
DATA_FILE = CAD_DATA_FILE


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
# I/O interno do JSON — genérico
# ──────────────────────────────────────────────────────────────────────────────

def _load_file(filepath: Path) -> list[dict]:
    if not filepath.exists():
        filepath.parent.mkdir(parents=True, exist_ok=True)
        return []
    try:
        return json.loads(filepath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _persist_file(filepath: Path, projects: list[dict]) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(
        json.dumps(projects, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ──────────────────────────────────────────────────────────────────────────────
# Aliases internos (manter compatibilidade com admin.py existente)
# ──────────────────────────────────────────────────────────────────────────────

def _load() -> list[dict]:
    return _load_file(CAD_DATA_FILE)


def _persist(projects: list[dict]) -> None:
    _persist_file(CAD_DATA_FILE, projects)


# ──────────────────────────────────────────────────────────────────────────────
# API pública — CRUD Projetos CAD
# ──────────────────────────────────────────────────────────────────────────────

def get_all_projects() -> list[dict]:
    """Retorna todos os projetos CAD, mais recentes primeiro."""
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
    """Cria (sem ID) ou atualiza (com ID) um projeto CAD no JSON."""
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
    """Remove o projeto CAD do JSON e limpa todos os seus arquivos estáticos."""
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


# ──────────────────────────────────────────────────────────────────────────────
# API pública — CRUD Projetos Excel
# ──────────────────────────────────────────────────────────────────────────────

def get_all_excel_projects() -> list[dict]:
    """Retorna todos os projetos Excel, mais recentes primeiro."""
    return sorted(
        _load_file(EXCEL_DATA_FILE),
        key=lambda p: p.get("date", ""),
        reverse=True,
    )


def get_excel_project_by_slug(slug: str) -> Optional[dict]:
    for p in _load_file(EXCEL_DATA_FILE):
        if p.get("slug") == slug:
            return p
    return None


def get_excel_project_by_id(project_id: str) -> Optional[dict]:
    for p in _load_file(EXCEL_DATA_FILE):
        if p.get("id") == project_id:
            return p
    return None


def save_excel_project(project: dict) -> dict:
    """Cria (sem ID) ou atualiza (com ID) um projeto Excel no JSON."""
    projects = _load_file(EXCEL_DATA_FILE)
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
    _persist_file(EXCEL_DATA_FILE, projects)
    return project


def delete_excel_project(project_id: str) -> bool:
    """Remove o projeto Excel do JSON e limpa seus arquivos estáticos."""
    projects = _load_file(EXCEL_DATA_FILE)
    target = next((p for p in projects if p["id"] == project_id), None)
    if not target:
        return False

    slug = target.get("slug", "")
    if slug:
        # Remove imagem de capa
        covers_dir = STATIC_DIR / "images" / "excel" / "covers"
        for ext in ("png", "jpg", "jpeg", "webp", "gif"):
            cover = covers_dir / f"{slug}.{ext}"
            if cover.exists():
                cover.unlink(missing_ok=True)
        # Remove arquivo Excel
        excel_dir = STATIC_DIR / "documents" / "excel"
        for ext in ("xlsx", "xlsm", "xls"):
            f = excel_dir / f"{slug}.{ext}"
            if f.exists():
                f.unlink(missing_ok=True)

    _persist_file(EXCEL_DATA_FILE, [p for p in projects if p["id"] != project_id])
    return True


# ──────────────────────────────────────────────────────────────────────────────
# API pública — Trilhas de Aprendizado (excel / autocad / solidworks)
# ──────────────────────────────────────────────────────────────────────────────

def get_trail_data(slug: str) -> Optional[dict]:
    """
    Carrega os dados de uma trilha a partir de app/data/trilhas/{slug}.json.
    Retorna None se o arquivo não existir ou o JSON for inválido.
    Slugs válidos: 'excel', 'autocad', 'solidworks'.
    """
    trail_file = TRILHAS_DIR / f"{slug}.json"
    if not trail_file.exists():
        return None
    try:
        return json.loads(trail_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


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
