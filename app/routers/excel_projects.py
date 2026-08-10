"""excel_projects.py — Rota da Trilha Excel.

GET /projetos/excel → página de trilha Excel diretamente
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context
from app.database import calculate_trail_progress, get_trail_data

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
