"""admin.py — Painel administrativo do Portfólio.

Rotas — Dashboard:
  GET  /admin-panel                              → Dashboard principal (tabs)

Rotas — Trilhas de Aprendizado:
  GET  /admin-panel/trilhas/{slug}               → Gestão de aulas de uma trilha
  GET  /admin-panel/trilhas/{slug}/nova-aula     → Formulário de nova aula
  POST /admin-panel/trilhas/{slug}/nova-aula     → Salvar nova aula
  GET  /admin-panel/trilhas/{slug}/editar-aula/{aula_id}  → Editar aula
  POST /admin-panel/trilhas/{slug}/editar-aula/{aula_id}  → Atualizar aula
  POST /admin-panel/trilhas/{slug}/excluir-aula  → Excluir aula (via form)
  POST /admin-panel/trilhas/{slug}/reordenar     → Reordenar aulas (JSON)
  POST /admin-panel/trilhas/{slug}/nova-secao    → Criar nova seção/módulo
  GET  /admin-panel/api/youtube-info             → Proxy oEmbed do YouTube

Rotas — Projetos CAD (legado, mantido):
  GET  /admin-panel/novo                         → Formulário de novo projeto
  POST /admin-panel/novo                         → Criar projeto
  GET  /admin-panel/editar/{id}                  → Formulário de edição
  POST /admin-panel/editar/{id}                  → Atualizar projeto
  GET  /admin-panel/excluir/{id}                 → Confirmação de exclusão
  POST /admin-panel/excluir/{id}                 → Executar exclusão

Nota: autenticação não implementada por decisão do desenvolvedor.
A estrutura está preparada para adicionar um middleware de autenticação
futuramente sem alterar os handlers abaixo.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional

import httpx
from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from app.blob_storage import blob_put_file
from app.config import get_base_context
from app.database import (
    add_modulo_to_trail,
    delete_aula_from_trail,
    delete_project,
    extract_pdf_sheets,
    get_all_projects,
    get_all_trails_summary,
    get_project_by_id,
    get_trail_data,
    reorder_aulas_in_modulo,
    save_aula_to_trail,
    save_project,
    slugify,
    youtube_to_embed,
)

router = APIRouter(prefix="/admin-panel")

STATIC_DIR   = Path(__file__).resolve().parent.parent / "static"
COVERS_DIR   = STATIC_DIR / "images" / "cad" / "covers"
CAD_DOC_DIR  = STATIC_DIR / "documents" / "cad"
TRAIL_DOC_DIR = STATIC_DIR / "documents" / "trilhas"

TRAIL_LABELS = {
    "excel":      "Excel",
    "autocad":    "AutoCAD",
    "solidworks": "SolidWorks",
}


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


async def _save_download_files(
    aula_id: str,
    trail_slug: str,
    files: list[UploadFile],
) -> list[dict]:
    """
    Salva arquivos de download de uma aula no Vercel Blob.
    Retorna lista de { nome, url, tipo }.
    """
    saved = []
    for f in files:
        if not f or not f.filename or not f.filename.strip():
            continue
        filename = f.filename.strip()
        try:
            content = await f.read()
            if not content:
                continue
            content_type = f.content_type or "application/octet-stream"
            blob_path = f"trilhas/{trail_slug}/{aula_id}/{filename}"
            url = blob_put_file(blob_path, content, content_type=content_type)
            ext = Path(filename).suffix.lower().lstrip(".")
            saved.append({
                "nome": filename,
                "url":  url,
                "tipo": ext,
            })
        except Exception:
            pass
    return saved



# ──────────────────────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def admin_dashboard(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    projects  = get_all_projects()
    trails    = get_all_trails_summary()
    context   = _ctx(page_title="Painel Admin | Portfólio")
    return templates.TemplateResponse(
        "pages/admin/dashboard.html",
        {"request": request, "projects": projects, "trails": trails, **context},
    )


# ──────────────────────────────────────────────────────────────────────────────
# API — YouTube oEmbed proxy
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/api/youtube-info", include_in_schema=False)
async def youtube_info(url: str) -> JSONResponse:
    """
    Busca metadados de um vídeo do YouTube via oEmbed (sem chave de API).
    Retorna: { title, thumbnail_url, author_name } ou { error }.
    """
    if not url:
        return JSONResponse({"error": "URL não informada"}, status_code=400)
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(oembed_url)
        if resp.status_code != 200:
            return JSONResponse(
                {"error": f"YouTube retornou status {resp.status_code}"},
                status_code=400,
            )
        data = resp.json()
        return JSONResponse({
            "title":         data.get("title", ""),
            "thumbnail_url": data.get("thumbnail_url", ""),
            "author_name":   data.get("author_name", ""),
        })
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


# ──────────────────────────────────────────────────────────────────────────────
# Trilhas — Gestão de aulas
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/trilhas/{slug}", response_class=HTMLResponse, include_in_schema=False)
async def admin_trail_manager(request: Request, slug: str) -> HTMLResponse:
    templates = request.app.state.templates
    trail = get_trail_data(slug)
    if not trail:
        return RedirectResponse(url="/admin-panel", status_code=303)
    context = _ctx(page_title=f"Trilha {trail['nome']} | Admin")
    return templates.TemplateResponse(
        "pages/admin/trail_manager.html",
        {"request": request, "trail": trail, "slug": slug, **context},
    )


@router.get("/trilhas/{slug}/nova-aula", response_class=HTMLResponse, include_in_schema=False)
async def admin_lesson_new_form(request: Request, slug: str) -> HTMLResponse:
    templates = request.app.state.templates
    trail = get_trail_data(slug)
    if not trail:
        return RedirectResponse(url="/admin-panel", status_code=303)
    context = _ctx(page_title=f"Nova Aula — {trail['nome']} | Admin")
    return templates.TemplateResponse(
        "pages/admin/lesson_form.html",
        {
            "request":    request,
            "trail":      trail,
            "slug":       slug,
            "aula":       None,
            "modulo_id":  request.query_params.get("modulo", ""),
            "mode":       "create",
            **context,
        },
    )


@router.post("/trilhas/{slug}/nova-aula", response_class=HTMLResponse, include_in_schema=False)
async def admin_lesson_create(
    request: Request,
    slug: str,
) -> RedirectResponse:
    form = await request.form()
    modulo_id = str(form.get("modulo_id", "")).strip()
    titulo = str(form.get("titulo", "")).strip()
    tipo_conteudo = str(form.get("tipo_conteudo", "video")).strip()
    duracao = str(form.get("duracao", "")).strip()
    url_youtube = str(form.get("url_youtube", "")).strip()
    nova_secao_titulo = str(form.get("nova_secao_titulo", "")).strip()

    download_files = [
        item for item in form.getlist("download_files")
        if isinstance(item, UploadFile) and item.filename and item.filename.strip()
    ]

    # Cria nova seção se solicitado
    if modulo_id == "__nova__" and nova_secao_titulo:
        novo_mod = add_modulo_to_trail(slug, nova_secao_titulo)
        if novo_mod:
            modulo_id = novo_mod["id"]
        else:
            return RedirectResponse(url=f"/admin-panel/trilhas/{slug}", status_code=303)

    aula: dict = {
        "titulo":              titulo,
        "tipoConteudo":        tipo_conteudo,
        "duracao":             duracao,
        "urlYoutube":          url_youtube,
        "arquivosParaDownload": [],
        "concluida":           False,
    }

    # Salva primeiro (gera o ID)
    saved = save_aula_to_trail(slug, modulo_id, aula)
    if not saved:
        return RedirectResponse(url=f"/admin-panel/trilhas/{slug}", status_code=303)

    # Salva arquivos de download e atualiza a aula
    if download_files:
        arquivos = await _save_download_files(saved["id"], slug, download_files)
        if arquivos:
            saved["arquivosParaDownload"] = arquivos
            save_aula_to_trail(slug, modulo_id, saved)

    return RedirectResponse(url=f"/admin-panel/trilhas/{slug}", status_code=303)


@router.get(
    "/trilhas/{slug}/editar-aula/{aula_id}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def admin_lesson_edit_form(
    request: Request,
    slug: str,
    aula_id: str,
) -> HTMLResponse:
    templates = request.app.state.templates
    trail = get_trail_data(slug)
    if not trail:
        return RedirectResponse(url="/admin-panel", status_code=303)

    # Localiza a aula dentro dos módulos
    aula = None
    modulo_id = ""
    for mod in trail.get("modulos", []):
        for a in mod.get("aulas", []):
            if a.get("id") == aula_id:
                aula = a
                modulo_id = mod["id"]
                break
        if aula:
            break

    if not aula:
        return RedirectResponse(url=f"/admin-panel/trilhas/{slug}", status_code=303)

    context = _ctx(page_title=f"Editar Aula — {aula['titulo']} | Admin")
    return templates.TemplateResponse(
        "pages/admin/lesson_form.html",
        {
            "request":   request,
            "trail":     trail,
            "slug":      slug,
            "aula":      aula,
            "modulo_id": modulo_id,
            "mode":      "edit",
            **context,
        },
    )


@router.post(
    "/trilhas/{slug}/editar-aula/{aula_id}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def admin_lesson_update(
    request: Request,
    slug: str,
    aula_id: str,
) -> RedirectResponse:
    form = await request.form()
    modulo_id = str(form.get("modulo_id", "")).strip()
    titulo = str(form.get("titulo", "")).strip()
    tipo_conteudo = str(form.get("tipo_conteudo", "video")).strip()
    duracao = str(form.get("duracao", "")).strip()
    url_youtube = str(form.get("url_youtube", "")).strip()

    download_files = [
        item for item in form.getlist("download_files")
        if isinstance(item, UploadFile) and item.filename and item.filename.strip()
    ]

    # Localiza a aula existente para preservar campos não editados
    trail = get_trail_data(slug)
    if not trail:
        return RedirectResponse(url="/admin-panel", status_code=303)

    existing_aula = None
    for mod in trail.get("modulos", []):
        for a in mod.get("aulas", []):
            if a.get("id") == aula_id:
                existing_aula = a
                break

    arquivos_existentes = existing_aula.get("arquivosParaDownload", []) if existing_aula else []

    aula = {
        "id":                  aula_id,
        "titulo":              titulo,
        "tipoConteudo":        tipo_conteudo,
        "duracao":             duracao,
        "urlYoutube":          url_youtube,
        "arquivosParaDownload": arquivos_existentes,
        "concluida":           existing_aula.get("concluida", False) if existing_aula else False,
    }

    # Adiciona novos arquivos de download (sem remover os existentes)
    if download_files:
        novos = await _save_download_files(aula_id, slug, download_files)
        if novos:
            aula["arquivosParaDownload"] = arquivos_existentes + novos

    save_aula_to_trail(slug, modulo_id, aula)
    return RedirectResponse(url=f"/admin-panel/trilhas/{slug}", status_code=303)



@router.post(
    "/trilhas/{slug}/excluir-aula",
    include_in_schema=False,
)
async def admin_lesson_delete(
    request: Request,
    slug: str,
    aula_id: str = Form(...),
    modulo_id: str = Form(...),
) -> RedirectResponse:
    delete_aula_from_trail(slug, modulo_id, aula_id)
    return RedirectResponse(url=f"/admin-panel/trilhas/{slug}", status_code=303)


@router.post("/trilhas/{slug}/reordenar", include_in_schema=False)
async def admin_lesson_reorder(
    request: Request,
    slug: str,
) -> JSONResponse:
    """Recebe JSON { modulo_id, ordered_ids: [] } e reordena as aulas."""
    try:
        body = await request.json()
        modulo_id   = body["modulo_id"]
        ordered_ids = body["ordered_ids"]
        ok = reorder_aulas_in_modulo(slug, modulo_id, ordered_ids)
        return JSONResponse({"ok": ok})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


@router.post("/trilhas/{slug}/nova-secao", include_in_schema=False)
async def admin_trail_new_section(
    request: Request,
    slug: str,
    titulo: str = Form(...),
) -> RedirectResponse:
    add_modulo_to_trail(slug, titulo)
    return RedirectResponse(url=f"/admin-panel/trilhas/{slug}", status_code=303)


# ──────────────────────────────────────────────────────────────────────────────
# Projetos CAD — CRUD (legado, mantido integralmente)
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


@router.get("/excluir/{project_id}", response_class=HTMLResponse, include_in_schema=False)
async def admin_delete_confirm(request: Request, project_id: str) -> HTMLResponse:
    templates = request.app.state.templates
    project = get_project_by_id(project_id)
    if not project:
        return RedirectResponse(url="/admin-panel", status_code=303)
    context = _ctx(page_title=f"Excluir: {project['title']} | Admin")
    return templates.TemplateResponse(
        "pages/admin/delete_confirm.html",
        {
            "request":     request,
            "project":     project,
            "item_type":   "projeto",
            "back_url":    "/admin-panel",
            "delete_url":  f"/admin-panel/excluir/{project['id']}",
            **context,
        },
    )


@router.post("/excluir/{project_id}", include_in_schema=False)
async def admin_delete_project(request: Request, project_id: str) -> RedirectResponse:
    delete_project(project_id)
    return RedirectResponse(url="/admin-panel", status_code=303)
