"""overleaf_projects.py — Rota da Trilha Overleaf (LaTeX).

GET /projetos/overleaf → página de trilha Overleaf (LaTeX)
GET /projetos/overleaf/aula/{aula_id} → página de reprodução e detalhes da aula
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context
from app.database import calculate_trail_progress, get_lesson_context, get_trail_data

router = APIRouter()


@router.get("/projetos/overleaf", response_class=HTMLResponse, include_in_schema=False)
async def trail_overleaf(request: Request) -> HTMLResponse:
    """Página de trilha Overleaf (LaTeX)."""
    templates = request.app.state.templates
    trail = get_trail_data("overleaf")
    if not trail:
        context = get_base_context(page_id="projetos", page_title="Trilha não encontrada")
        return templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )
    progress = calculate_trail_progress(trail)
    context = get_base_context(
        page_id="projetos",
        page_title="Trilha Overleaf (LaTeX) | Carlos Daniel",
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


@router.get("/projetos/overleaf/aula/{aula_id}", response_class=HTMLResponse, include_in_schema=False)
async def overleaf_lesson_watch(request: Request, aula_id: str) -> HTMLResponse:
    """Página de reprodução e detalhes de uma aula da trilha Overleaf (LaTeX)."""
    data = get_lesson_context("overleaf", aula_id)
    if not data:
        context = get_base_context(page_id="projetos", page_title="Aula não encontrada")
        return request.app.state.templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )

    trail = data["trail"]
    aula = data["aula"]
    context = get_base_context(
        page_id="projetos",
        page_title=f"{aula['titulo']} — Overleaf (LaTeX) | Carlos Daniel",
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
            "trail_url": "/projetos/overleaf",
            "breadcrumb_parent": {"label": "Projetos", "href": "/projetos"},
            **context,
        },
    )
