"""admin.py — Painel administrativo exclusivo do Laboratório CAD.

Rotas:
  GET  /admin-panel                  → Dashboard (lista de projetos)
  GET  /admin-panel/novo             → Formulário de novo projeto
  POST /admin-panel/novo             → Criar projeto
  GET  /admin-panel/editar/{id}      → Formulário de edição
  POST /admin-panel/editar/{id}      → Atualizar projeto
  GET  /admin-panel/excluir/{id}     → Confirmação de exclusão
  POST /admin-panel/excluir/{id}     → Executar exclusão

Nota: autenticação não implementada neste sprint por decisão do desenvolvedor.
A estrutura está preparada para adicionar um middleware de autenticação
futuramente sem alterar os handlers abaixo.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import get_base_context
from app.database import (
    delete_project,
    extract_pdf_sheets,
    get_all_projects,
    get_project_by_id,
    save_project,
    slugify,
    youtube_to_embed,
)

router = APIRouter(prefix="/admin-panel")

STATIC_DIR  = Path(__file__).resolve().parent.parent / "static"
COVERS_DIR  = STATIC_DIR / "images" / "cad" / "covers"
CAD_DOC_DIR = STATIC_DIR / "documents" / "cad"


# ──────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ──────────────────────────────────────────────────────────────────────────────

def _ctx(**kwargs) -> dict:
    return get_base_context(page_id="admin", **kwargs)


async def _save_cover(cover_image: UploadFile, slug: str) -> str:
    """Salva a imagem de capa e retorna a URL estática."""
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(cover_image.filename).suffix.lower() or ".png"
    dest = COVERS_DIR / f"{slug}{ext}"
    with open(dest, "wb") as f:
        shutil.copyfileobj(cover_image.file, f)
    return f"/static/images/cad/covers/{slug}{ext}"


async def _save_pdf_and_extract(pdf_file: UploadFile, slug: str) -> tuple[str, list[dict]]:
    """Salva o PDF, extrai as folhas como PNG e retorna (pdf_url, sheet_images)."""
    CAD_DOC_DIR.mkdir(parents=True, exist_ok=True)
    dest = CAD_DOC_DIR / f"{slug}.pdf"
    with open(dest, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)
    pdf_url = f"/static/documents/cad/{slug}.pdf"

    # Limpa folhas anteriores (re-extração)
    sheets_dir = STATIC_DIR / "images" / "cad" / slug
    if sheets_dir.exists():
        shutil.rmtree(sheets_dir, ignore_errors=True)

    paths = extract_pdf_sheets(dest, sheets_dir)
    sheet_images = [
        {"path": p, "caption": f"Folha {i + 1}", "description": ""}
        for i, p in enumerate(paths)
    ]
    return pdf_url, sheet_images


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def admin_dashboard(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    projects = get_all_projects()
    context = _ctx(page_title="Painel Admin | Laboratório CAD")
    return templates.TemplateResponse(
        "pages/admin/dashboard.html",
        {"request": request, "projects": projects, **context},
    )


# ──────────────────────────────────────────────────────────────────────────────
# Criar novo projeto
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/novo", response_class=HTMLResponse, include_in_schema=False)
async def admin_new_form(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    context = _ctx(page_title="Novo Projeto | Admin")
    return templates.TemplateResponse(
        "pages/admin/project_form.html",
        {"request": request, "project": None, "mode": "create", **context},
    )


@router.post("/novo", response_class=HTMLResponse, include_in_schema=False)
async def admin_create_project(
    request: Request,
    title: str             = Form(...),
    short_desc: str        = Form(...),
    desc_objective: str    = Form(default=""),
    desc_modeling: str     = Form(default=""),
    software: str          = Form(...),
    category: str          = Form(default="Modelagem 3D"),
    status: str            = Form(...),
    date: str              = Form(...),
    youtube_url: str       = Form(default=""),
    evolution_text: str    = Form(default=""),
    skills: List[str]      = Form(default=[]),
    cover_image: Optional[UploadFile] = File(default=None),
    pdf_file: Optional[UploadFile]    = File(default=None),
) -> RedirectResponse:
    slug      = slugify(title)
    embed_url = youtube_to_embed(youtube_url)

    cover_path   = ""
    pdf_path_str = ""
    sheet_images: list[dict] = []

    if cover_image and cover_image.filename:
        cover_path = await _save_cover(cover_image, slug)

    if pdf_file and pdf_file.filename:
        pdf_path_str, sheet_images = await _save_pdf_and_extract(pdf_file, slug)

    project = {
        "title":          title,
        "slug":           slug,
        "short_desc":     short_desc,
        "desc_objective": desc_objective,
        "desc_modeling":  desc_modeling,
        "cover_image":    cover_path,
        "pdf_path":       pdf_path_str,
        "youtube_url":    youtube_url,
        "embed_url":      embed_url,
        "software":       software,
        "category":       category,
        "status":         status,
        "date":           date,
        "skills":         [s.strip() for s in skills if s.strip()],
        "evolution_text": evolution_text,
        "sheet_images":   sheet_images,
    }
    save_project(project)
    return RedirectResponse(url="/admin-panel", status_code=303)


# ──────────────────────────────────────────────────────────────────────────────
# Editar projeto existente
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/editar/{project_id}", response_class=HTMLResponse, include_in_schema=False)
async def admin_edit_form(request: Request, project_id: str) -> HTMLResponse:
    templates = request.app.state.templates
    project = get_project_by_id(project_id)
    if not project:
        return RedirectResponse(url="/admin-panel", status_code=303)
    context = _ctx(page_title=f"Editar: {project['title']} | Admin")
    return templates.TemplateResponse(
        "pages/admin/project_form.html",
        {"request": request, "project": project, "mode": "edit", **context},
    )


@router.post("/editar/{project_id}", response_class=HTMLResponse, include_in_schema=False)
async def admin_update_project(
    request: Request,
    project_id: str,
    title: str             = Form(...),
    short_desc: str        = Form(...),
    desc_objective: str    = Form(default=""),
    desc_modeling: str     = Form(default=""),
    software: str          = Form(...),
    category: str          = Form(default="Modelagem 3D"),
    status: str            = Form(...),
    date: str              = Form(...),
    youtube_url: str       = Form(default=""),
    evolution_text: str    = Form(default=""),
    skills: List[str]      = Form(default=[]),
    cover_image: Optional[UploadFile] = File(default=None),
    pdf_file: Optional[UploadFile]    = File(default=None),
) -> RedirectResponse:
    project = get_project_by_id(project_id)
    if not project:
        return RedirectResponse(url="/admin-panel", status_code=303)

    slug      = project.get("slug") or slugify(title)
    embed_url = youtube_to_embed(youtube_url)

    # Preserva arquivos existentes se não forem substituídos
    cover_path   = project.get("cover_image", "")
    pdf_path_str = project.get("pdf_path", "")
    sheet_images = project.get("sheet_images", [])

    if cover_image and cover_image.filename:
        cover_path = await _save_cover(cover_image, slug)

    if pdf_file and pdf_file.filename:
        pdf_path_str, sheet_images = await _save_pdf_and_extract(pdf_file, slug)

    project.update({
        "title":          title,
        "slug":           slug,
        "short_desc":     short_desc,
        "desc_objective": desc_objective,
        "desc_modeling":  desc_modeling,
        "cover_image":    cover_path,
        "pdf_path":       pdf_path_str,
        "youtube_url":    youtube_url,
        "embed_url":      embed_url,
        "software":       software,
        "category":       category,
        "status":         status,
        "date":           date,
        "skills":         [s.strip() for s in skills if s.strip()],
        "evolution_text": evolution_text,
        "sheet_images":   sheet_images,
    })
    save_project(project)
    return RedirectResponse(url="/admin-panel", status_code=303)


# ──────────────────────────────────────────────────────────────────────────────
# Excluir projeto
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/excluir/{project_id}", response_class=HTMLResponse, include_in_schema=False)
async def admin_delete_confirm(request: Request, project_id: str) -> HTMLResponse:
    templates = request.app.state.templates
    project = get_project_by_id(project_id)
    if not project:
        return RedirectResponse(url="/admin-panel", status_code=303)
    context = _ctx(page_title=f"Excluir: {project['title']} | Admin")
    return templates.TemplateResponse(
        "pages/admin/delete_confirm.html",
        {"request": request, "project": project, **context},
    )


@router.post("/excluir/{project_id}", include_in_schema=False)
async def admin_delete_project(request: Request, project_id: str) -> RedirectResponse:
    delete_project(project_id)
    return RedirectResponse(url="/admin-panel", status_code=303)
