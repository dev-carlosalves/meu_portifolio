"""cad_projects.py — Rotas dos Projetos CAD.

GET /projetos/cad             → seleção de software (AutoCAD / SolidWorks)
GET /projetos/cad/autocad     → página de trilha AutoCAD
GET /projetos/cad/solidworks  → página de trilha SolidWorks
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context
from app.database import calculate_trail_progress, get_trail_data

router = APIRouter()


@router.get("/projetos/cad", response_class=HTMLResponse, include_in_schema=False)
async def cad_software_selection(request: Request) -> HTMLResponse:
    """Tela intermediária: escolher entre AutoCAD e SolidWorks."""
    templates = request.app.state.templates
    context = get_base_context(
        page_id="projetos",
        page_title="Projetos CAD | Carlos Daniel",
        description=(
            "Escolha sua trilha CAD: AutoCAD para desenho técnico 2D "
            "ou SolidWorks para modelagem 3D paramétrica e engenharia mecânica."
        ),
    )
    return templates.TemplateResponse(
        "pages/cad_projects.html",
        {"request": request, **context},
    )


@router.get("/projetos/cad/autocad", response_class=HTMLResponse, include_in_schema=False)
async def trail_autocad(request: Request) -> HTMLResponse:
    """Página de trilha AutoCAD."""
    templates = request.app.state.templates
    trail = get_trail_data("autocad")
    if not trail:
        context = get_base_context(page_id="projetos", page_title="Trilha não encontrada")
        return templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )
    progress = calculate_trail_progress(trail)
    context = get_base_context(
        page_id="projetos",
        page_title="Trilha AutoCAD | Carlos Daniel",
        description=trail.get("descricao", ""),
    )
    return templates.TemplateResponse(
        "pages/trail_page.html",
        {
            "request": request,
            "trail": trail,
            "progress": progress,
            "breadcrumb_parent": {"label": "Projetos CAD", "href": "/projetos/cad"},
            **context,
        },
    )


@router.get("/projetos/cad/solidworks", response_class=HTMLResponse, include_in_schema=False)
async def trail_solidworks(request: Request) -> HTMLResponse:
    """Página de trilha SolidWorks."""
    templates = request.app.state.templates
    trail = get_trail_data("solidworks")
    if not trail:
        context = get_base_context(page_id="projetos", page_title="Trilha não encontrada")
        return templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )
    progress = calculate_trail_progress(trail)
    context = get_base_context(
        page_id="projetos",
        page_title="Trilha SolidWorks | Carlos Daniel",
        description=trail.get("descricao", ""),
    )
    return templates.TemplateResponse(
        "pages/trail_page.html",
        {
            "request": request,
            "trail": trail,
            "progress": progress,
            "breadcrumb_parent": {"label": "Projetos CAD", "href": "/projetos/cad"},
            **context,
        },
    )
