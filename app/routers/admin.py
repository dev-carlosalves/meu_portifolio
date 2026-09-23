"""admin.py — Painel administrativo do Portfólio.

Rotas — Dashboard:
  GET  /admin-panel                              → Dashboard principal

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
  GET  /admin-panel/api/trail-modules/{slug}     → Módulos leves para select
  POST /admin-panel/api/upload-url               → URL para upload direto
  POST /admin-panel/api/record-blob-file         → Registro de anexo
"""

from __future__ import annotations

import json
import re
import shutil
import uuid
from pathlib import Path
from typing import List, Optional

import httpx
from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from app.blob_storage import blob_put_file, generate_client_upload_token
from app.config import get_base_context
from app.database import (
    add_modulo_to_trail,
    delete_aula_from_trail,
    get_all_trails_summary,
    get_trail_data,
    reorder_aulas_in_modulo,
    save_aula_to_trail,
    slugify,
    youtube_to_embed,
)

router = APIRouter(prefix="/admin-panel")

STATIC_DIR    = Path(__file__).resolve().parent.parent / "static"
TRAIL_DOC_DIR = STATIC_DIR / "documents" / "trilhas"

TRAIL_LABELS = {
    "excel":      "Excel",
    "powerbi":    "Power BI",
    "autocad":    "AutoCAD",
    "solidworks": "SolidWorks",
    "overleaf":   "Overleaf (LaTeX)",
}


# ──────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ──────────────────────────────────────────────────────────────────────────────

def _ctx(**kwargs) -> dict:
    return get_base_context(page_id="admin", **kwargs)


async def _save_download_files(
    aula_id: str,
    trail_slug: str,
    files: list[UploadFile],
) -> list[dict]:
    """
    Salva arquivos de download de uma aula.
    Prioriza o upload para o Vercel Blob (produção).
    Tenta salvar cópia local em /static/documents/trilhas/... (desenvolvimento local).
    Se o Blob falhar ou não estiver configurado, utiliza a URL estática local como fallback.
    Retorna lista de { nome, url, tipo }.
    """
    saved = []
    local_aula_dir = TRAIL_DOC_DIR / trail_slug / aula_id
    try:
        local_aula_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        print(f"[INFO] Filesystem local read-only (ambiente Serverless Vercel): {exc}")

    for f in files:
        if not f or not getattr(f, "filename", None) or not str(f.filename).strip():
            continue
        filename = Path(f.filename.strip()).name
        if not filename:
            continue
        try:
            content = await f.read()
            if not content:
                continue

            content_type = getattr(f, "content_type", None) or "application/octet-stream"
            local_url = f"/static/documents/trilhas/{trail_slug}/{aula_id}/{filename}"
            final_url = local_url

            # 1. Upload para o Vercel Blob (produção)
            try:
                blob_path = f"trilhas/{trail_slug}/{aula_id}/{filename}"
                blob_url = blob_put_file(blob_path, content, content_type=content_type)
                if blob_url:
                    final_url = blob_url
                    print(f"[OK] Arquivo {filename} salvo no Vercel Blob: {blob_url}")
            except Exception as exc:
                print(f"[AVISO] Upload no Blob falhou para {filename}, usando URL local como fallback: {exc}")

            # 2. Cópia local para desenvolvimento (tolerante a read-only filesystem)
            try:
                local_dest = local_aula_dir / filename
                local_dest.write_bytes(content)
            except Exception as exc:
                print(f"[INFO] Cópia local não gravada (read-only no Vercel): {exc}")

            ext = Path(filename).suffix.lower().lstrip(".")
            saved.append({
                "nome": filename,
                "url":  final_url,
                "tipo": ext,
            })
        except Exception as exc:
            print(f"[ERRO] Falha ao processar arquivo {filename}: {exc}")
    return saved


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def admin_dashboard(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    trails    = get_all_trails_summary()
    context   = _ctx(page_title="Painel Admin | Portfólio")
    return templates.TemplateResponse(
        "pages/admin/dashboard.html",
        {"request": request, "trails": trails, **context},
    )


# ──────────────────────────────────────────────────────────────────────────────
# API — YouTube oEmbed proxy
# ──────────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────────────
# API — Módulos de uma trilha (leve, sem aulas)
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/api/trail-modules/{slug}", include_in_schema=False)
async def api_trail_modules(slug: str) -> JSONResponse:
    """
    Retorna apenas os módulos (id, numero, titulo) de uma trilha, sem aulas.
    Usado pelo JS do lesson_form para popular o select de módulo ao trocar de área.
    Resposta leve — não inclui dados das aulas para evitar payloads grandes.
    """
    trail = get_trail_data(slug)
    if not trail:
        return JSONResponse({"modulos": []}, status_code=404)
    modulos_leves = [
        {"id": m["id"], "numero": m.get("numero", ""), "titulo": m.get("titulo", "")}
        for m in trail.get("modulos", [])
    ]
    return JSONResponse({"modulos": modulos_leves})


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


@router.post("/api/request-upload", include_in_schema=False)
async def api_request_upload(request: Request) -> JSONResponse:
    """
    Gera um token de upload client-side para o Vercel Blob.
    O browser faz o PUT diretamente em blob.vercel-storage.com, sem passar
    pelo serverless da Vercel — contorna o limite de 4.5 MB do request body.

    Recebe JSON: { filename, slug, aula_id? } ou { pathname }
    Retorna:     { client_token, upload_url, pathname, clean_name, ext }
    """
    try:
        body = await request.json()
        pathname = str(body.get("pathname", "")).strip()
        filename = str(body.get("filename", "")).strip()
        slug = str(body.get("slug", "geral")).strip()
        aula_id = str(body.get("aula_id", "")).strip() or str(uuid.uuid4())
        max_size_mb = int(body.get("max_size_mb", 100))

        if not pathname:
            if not filename:
                return JSONResponse({"error": "pathname ou filename é obrigatório"}, status_code=400)
            clean_name = Path(filename).name
            clean_name = re.sub(r"[^\w\.\-\_]", "_", clean_name)
            pathname = f"trilhas/{slug}/{aula_id}/{clean_name}"
        else:
            clean_name = Path(pathname).name

        ext = clean_name.rsplit(".", 1)[-1].lower() if "." in clean_name else ""
        result = generate_client_upload_token(pathname, max_size_mb=max_size_mb)
        result["clean_name"] = clean_name
        result["ext"] = ext
        return JSONResponse(result)
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

    # Cria versão leve da trilha (sem aulas) para evitar resposta HTML > 4.5 MB
    # que causa erro 413 FUNCTION_PAYLOAD_TOO_LARGE no Vercel.
    trail_leve = {
        **trail,
        "modulos": [
            {"id": m["id"], "numero": m.get("numero", ""), "titulo": m.get("titulo", ""), "aulas": []}
            for m in trail.get("modulos", [])
        ],
    }

    context = _ctx(page_title=f"Nova Aula — {trail['nome']} | Admin")
    return templates.TemplateResponse(
        "pages/admin/lesson_form.html",
        {
            "request":    request,
            "trail":      trail_leve,
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
    try:
        form = await request.form()
        modulo_id = str(form.get("modulo_id", "")).strip()
        titulo = str(form.get("titulo", "")).strip()
        descricao = str(form.get("descricao", "")).strip()
        tipo_conteudo = str(form.get("tipo_conteudo", "video")).strip()
        duracao = str(form.get("duracao", "")).strip()
        url_youtube = str(form.get("url_youtube", "")).strip()
        nova_secao_titulo = str(form.get("nova_secao_titulo", "")).strip()

        download_files = [
            item for item in form.getlist("download_files")
            if hasattr(item, "filename") and item.filename and str(item.filename).strip()
        ]

        # Cria nova seção se solicitado
        if modulo_id == "__nova__" and nova_secao_titulo:
            novo_mod = add_modulo_to_trail(slug, nova_secao_titulo)
            if novo_mod:
                modulo_id = novo_mod["id"]
            else:
                return RedirectResponse(url=f"/admin-panel/trilhas/{slug}", status_code=303)

        aula_id = str(form.get("aula_id", "")).strip() or str(uuid.uuid4())

        # Arquivos pré-enviados diretamente ao Vercel Blob pelo browser
        pre_uploaded_json = form.get("pre_uploaded_files", "")
        pre_uploaded: list[dict] = []
        if pre_uploaded_json:
            try:
                pre_uploaded = json.loads(str(pre_uploaded_json))
            except Exception as e:
                print(f"[AVISO] Falha ao decodificar pre_uploaded_files: {e}")
                pre_uploaded = []

        # Salva arquivos de download primeiro com o ID da aula
        arquivos: list[dict] = list(pre_uploaded)  # inicia com os já enviados ao Blob
        if download_files:
            arquivos += await _save_download_files(aula_id, slug, download_files)

        aula: dict = {
            "id":                  aula_id,
            "titulo":              titulo,
            "descricao":           descricao,
            "tipoConteudo":        tipo_conteudo,
            "duracao":             duracao,
            "urlYoutube":          url_youtube,
            "arquivosParaDownload": arquivos,
            "concluida":           False,
        }

        save_aula_to_trail(slug, modulo_id, aula)
    except Exception as exc:
        print(f"[ERRO] Falha ao criar aula na trilha {slug}: {exc}")

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

    # Cria versão leve da trilha (sem aulas) para evitar resposta HTML > 4.5 MB
    # que causa erro 413 FUNCTION_PAYLOAD_TOO_LARGE no Vercel.
    trail_leve = {
        **trail,
        "modulos": [
            {"id": m["id"], "numero": m.get("numero", ""), "titulo": m.get("titulo", ""), "aulas": []}
            for m in trail.get("modulos", [])
        ],
    }

    context = _ctx(page_title=f"Editar Aula — {aula['titulo']} | Admin")
    return templates.TemplateResponse(
        "pages/admin/lesson_form.html",
        {
            "request":   request,
            "trail":     trail_leve,
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
    try:
        form = await request.form()
        modulo_id = str(form.get("modulo_id", "")).strip()
        titulo = str(form.get("titulo", "")).strip()
        descricao = str(form.get("descricao", "")).strip()
        tipo_conteudo = str(form.get("tipo_conteudo", "video")).strip()
        duracao = str(form.get("duracao", "")).strip()
        url_youtube = str(form.get("url_youtube", "")).strip()
        nova_secao_titulo = str(form.get("nova_secao_titulo", "")).strip()

        if modulo_id == "__nova__" and nova_secao_titulo:
            novo_mod = add_modulo_to_trail(slug, nova_secao_titulo)
            if novo_mod:
                modulo_id = novo_mod["id"]

        download_files = [
            item for item in form.getlist("download_files")
            if hasattr(item, "filename") and item.filename and str(item.filename).strip()
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
                    if not modulo_id:
                        modulo_id = mod["id"]
                    break
            if existing_aula:
                break

        arquivos_existentes = existing_aula.get("arquivosParaDownload", []) if existing_aula else []

        # Se o formulário informou o gerenciamento de arquivos existentes
        tem_arquivos_existentes = "tem_arquivos_existentes" in form
        if tem_arquivos_existentes:
            manter_arquivos = set(form.getlist("manter_arquivos"))
            arquivos_preservados = [
                arq for arq in arquivos_existentes
                if arq.get("url") in manter_arquivos or arq.get("nome") in manter_arquivos
            ]
        else:
            arquivos_preservados = arquivos_existentes

        # Adiciona novos arquivos de download (servidor) + pré-enviados ao Blob
        pre_uploaded_json = form.get("pre_uploaded_files", "")
        pre_uploaded_novos: list[dict] = []
        if pre_uploaded_json:
            try:
                pre_uploaded_novos = json.loads(str(pre_uploaded_json))
            except Exception as e:
                print(f"[AVISO] Falha ao decodificar pre_uploaded_files: {e}")
                pre_uploaded_novos = []

        novos: list[dict] = list(pre_uploaded_novos)
        if download_files:
            novos += await _save_download_files(aula_id, slug, download_files)

        aula = {
            "id":                  aula_id,
            "titulo":              titulo,
            "descricao":           descricao,
            "tipoConteudo":        tipo_conteudo,
            "duracao":             duracao,
            "urlYoutube":          url_youtube,
            "arquivosParaDownload": arquivos_preservados + novos,
            "concluida":           existing_aula.get("concluida", False) if existing_aula else False,
        }

        save_aula_to_trail(slug, modulo_id, aula)
    except Exception as exc:
        print(f"[ERRO] Falha ao atualizar aula {aula_id} na trilha {slug}: {exc}")

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

