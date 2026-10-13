"""bi_projects.py — Rota da Área de Business Intelligence (BI).

GET /projetos/bi                  → página completa da área de BI com explicação das ferramentas e trilha
GET /projetos/bi/aula/{aula_id}   → página de reprodução e detalhes da aula de BI
GET /projetos/overleaf            → redirecionamento 301 para /projetos/bi
GET /projetos/overleaf/aula/{id}  → redirecionamento 301 para /projetos/bi
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import get_base_context
from app.database import calculate_trail_progress, get_lesson_context, get_trail_data

router = APIRouter()


@router.get("/projetos/bi", response_class=HTMLResponse, include_in_schema=False)
async def trail_bi(request: Request) -> HTMLResponse:
    """Página de trilha Business Intelligence (BI)."""
    templates = request.app.state.templates
    trail = get_trail_data("bi")
    if not trail:
        context = get_base_context(page_id="projetos", page_title="Trilha não encontrada")
        return templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )
    progress = calculate_trail_progress(trail)
    context = get_base_context(
        page_id="projetos",
        page_title="Trilha BI (Business Intelligence) | Carlos Daniel",
        description=trail.get("descricao", ""),
    )
    return templates.TemplateResponse(
        "pages/trail_page.html",
        {
            "request": request,
            "trail": trail,
            "progress": progress,
            "breadcrumb_parent": {"label": "Projetos", "href": "/projetos"},
            **context,
        },
    )


@router.get("/projetos/bi/aula/{aula_id}", response_class=HTMLResponse, include_in_schema=False)
async def bi_lesson_watch(request: Request, aula_id: str) -> HTMLResponse:
    """Página de reprodução e detalhes de uma aula da trilha de BI."""
    data = get_lesson_context("bi", aula_id)
    if not data:
        context = get_base_context(page_id="projetos", page_title="Aula não encontrada")
        return request.app.state.templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )

    trail = data["trail"]
    aula = data["aula"]
    context = get_base_context(
        page_id="projetos",
        page_title=f"{aula['titulo']} — BI (Business Intelligence) | Carlos Daniel",
        description=aula.get("descricao") or trail.get("descricao", ""),
    )

    return request.app.state.templates.TemplateResponse(
        "pages/lesson_page.html",
        {
            "request": request,
            "trail": trail,
            "modulo": data["modulo"],
            "aula": aula,
            "prev_aula": data["prev_aula"],
            "prev_modulo": data["prev_modulo"],
            "next_aula": data["next_aula"],
            "next_modulo": data["next_modulo"],
            "progress": data["progress"],
            "trail_url": "/projetos/bi",
            "breadcrumb_parent": {"label": "BI (Business Intelligence)", "href": "/projetos/bi"},
            **context,
        },
    )


# ──────────────────────────────────────────────────────────────────────────────
# Redirecionamentos de migração (Overleaf → BI)
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/projetos/overleaf", include_in_schema=False)
async def redirect_overleaf_to_bi() -> RedirectResponse:
    return RedirectResponse(url="/projetos/bi", status_code=301)


@router.get("/projetos/overleaf/aula/{aula_id}", include_in_schema=False)
async def redirect_overleaf_aula_to_bi(aula_id: str) -> RedirectResponse:
    return RedirectResponse(url="/projetos/bi", status_code=301)
