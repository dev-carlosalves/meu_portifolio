"""cad_projects.py — Rotas dos Projetos CAD.

GET /projetos/cad             → seleção de software (AutoCAD / SolidWorks)
GET /projetos/cad/autocad     → página de trilha AutoCAD
GET /projetos/cad/solidworks  → página de trilha SolidWorks
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context
from app.database import calculate_trail_progress, get_lesson_context, get_trail_data

router = APIRouter()


@router.get("/projetos/cad", response_class=HTMLResponse, include_in_schema=False)
async def cad_software_selection(request: Request) -> HTMLResponse:
    """Tela intermediária: escolher entre AutoCAD e SolidWorks."""
    templates = request.app.state.templates
    context = get_base_context(
        page_id="projetos",
        page_title="Projetos CAD | Carlos Daniel",
        description=(
            "Escolha uma trilha de estudos CAD: desenhos técnicos 2D em AutoCAD "
            "ou modelagem 3D paramétrica no SolidWorks aplicada a estudos de engenharia mecânica."
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


@router.get("/projetos/cad/{slug}/aula/{aula_id}", response_class=HTMLResponse, include_in_schema=False)
async def cad_lesson_watch(request: Request, slug: str, aula_id: str) -> HTMLResponse:
    """Página de reprodução e detalhes de uma aula das trilhas CAD."""
    if slug not in ("autocad", "solidworks"):
        context = get_base_context(page_id="projetos", page_title="Aula não encontrada")
        return request.app.state.templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )

    data = get_lesson_context(slug, aula_id)
    if not data:
        context = get_base_context(page_id="projetos", page_title="Aula não encontrada")
        return request.app.state.templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )

    trail = data["trail"]
    aula = data["aula"]
    context = get_base_context(
        page_id="projetos",
        page_title=f"{aula['titulo']} — {trail['nome']} | Carlos Daniel",
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
            "trail_url": f"/projetos/cad/{slug}",
            "breadcrumb_parent": {"label": "Projetos CAD", "href": "/projetos/cad"},
            **context,
        },
    )

