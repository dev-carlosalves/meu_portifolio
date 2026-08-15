"""excel_projects.py — Rota da Trilha Excel.

GET /projetos/excel → página de trilha Excel diretamente
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context
from app.database import calculate_trail_progress, get_lesson_context, get_trail_data

router = APIRouter()


@router.get("/projetos/excel", response_class=HTMLResponse, include_in_schema=False)
async def trail_excel(request: Request) -> HTMLResponse:
    """Página de trilha Excel — sem tela intermediária de seleção."""
    templates = request.app.state.templates
    trail = get_trail_data("excel")
    if not trail:
        context = get_base_context(page_id="projetos", page_title="Trilha não encontrada")
        return templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )
    progress = calculate_trail_progress(trail)
    context = get_base_context(
        page_id="projetos",
        page_title="Trilha Excel | Carlos Daniel",
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


@router.get("/projetos/excel/aula/{aula_id}", response_class=HTMLResponse, include_in_schema=False)
async def excel_lesson_watch(request: Request, aula_id: str) -> HTMLResponse:
    """Página de reprodução e detalhes de uma aula da trilha Excel."""
    data = get_lesson_context("excel", aula_id)
    if not data:
        context = get_base_context(page_id="projetos", page_title="Aula não encontrada")
        return request.app.state.templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )

    trail = data["trail"]
    aula = data["aula"]
    context = get_base_context(
        page_id="projetos",
        page_title=f"{aula['titulo']} — Excel | Carlos Daniel",
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
            "trail_url": "/projetos/excel",
            "breadcrumb_parent": {"label": "Projetos", "href": "/projetos"},
            **context,
        },
    )

