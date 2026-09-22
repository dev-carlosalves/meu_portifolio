"""data_analysis_projects.py — Rotas dos Projetos de Análise de Dados e Trilha Power BI.

GET /projetos/analise-dados                → Seleção entre Excel e Power BI
GET /projetos/powerbi                      → Página de trilha Power BI
GET /projetos/powerbi/aula/{aula_id}       → Página de reprodução e detalhes de aula Power BI
GET /projetos/analise-dados/powerbi        → Redirecionamento para /projetos/powerbi
GET /projetos/analise-dados/excel          → Redirecionamento para /projetos/excel
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import get_base_context
from app.database import calculate_trail_progress, get_lesson_context, get_trail_data

router = APIRouter()


@router.get("/projetos/analise-dados", response_class=HTMLResponse, include_in_schema=False)
async def data_analysis_selection(request: Request) -> HTMLResponse:
    """Tela intermediária: escolher entre Excel e Power BI."""
    templates = request.app.state.templates
    context = get_base_context(
        page_id="projetos",
        page_title="Projetos de Análise de Dados | Carlos Daniel",
        description=(
            "Explore projetos e trilhas de estudo em Análise de Dados: relatórios e dashboards "
            "interativos em Power BI e práticas analíticas com fórmulas, tabelas dinâmicas e automações em Excel."
        ),
    )
    return templates.TemplateResponse(
        "pages/data_analysis_projects.html",
        {"request": request, **context},
    )


@router.get("/projetos/analise-dados/powerbi", include_in_schema=False)
async def redirect_analise_dados_powerbi() -> RedirectResponse:
    return RedirectResponse(url="/projetos/powerbi", status_code=301)


@router.get("/projetos/analise-dados/excel", include_in_schema=False)
async def redirect_analise_dados_excel() -> RedirectResponse:
    return RedirectResponse(url="/projetos/excel", status_code=301)


@router.get("/projetos/powerbi", response_class=HTMLResponse, include_in_schema=False)
async def trail_powerbi(request: Request) -> HTMLResponse:
    """Página de trilha Power BI."""
    templates = request.app.state.templates
    trail = get_trail_data("powerbi")
    if not trail:
        context = get_base_context(page_id="projetos", page_title="Trilha não encontrada")
        return templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )
    progress = calculate_trail_progress(trail)
    context = get_base_context(
        page_id="projetos",
        page_title="Trilha Power BI | Carlos Daniel",
        description=trail.get("descricao", ""),
    )
    return templates.TemplateResponse(
        "pages/trail_page.html",
        {
            "request": request,
            "trail": trail,
            "progress": progress,
            "breadcrumb_parent": {"label": "Análise de Dados", "href": "/projetos/analise-dados"},
            **context,
        },
    )


@router.get("/projetos/powerbi/aula/{aula_id}", response_class=HTMLResponse, include_in_schema=False)
async def powerbi_lesson_watch(request: Request, aula_id: str) -> HTMLResponse:
    """Página de reprodução e detalhes de uma aula da trilha Power BI."""
    data = get_lesson_context("powerbi", aula_id)
    if not data:
        context = get_base_context(page_id="projetos", page_title="Aula não encontrada")
        return request.app.state.templates.TemplateResponse(
            "pages/404.html", {"request": request, **context}, status_code=404
        )

    trail = data["trail"]
    aula = data["aula"]
    context = get_base_context(
        page_id="projetos",
        page_title=f"{aula['titulo']} — Power BI | Carlos Daniel",
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
            "trail_url": "/projetos/powerbi",
            "breadcrumb_parent": {"label": "Análise de Dados", "href": "/projetos/analise-dados"},
            **context,
        },
    )
