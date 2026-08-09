"""excel_projects.py — Rotas dos Projetos Excel.

GET /projetos/excel → catálogo de projetos/planilhas em Excel
"""

from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context
from app.database import get_all_excel_projects

router = APIRouter()

# Categorias de projetos Excel
EXCEL_CATEGORIES = ["Dashboard", "Relatório", "Automação", "Análise de Dados", "Financeiro"]


@router.get("/projetos/excel", response_class=HTMLResponse, include_in_schema=False)
async def excel_projects_catalog(
    request: Request,
    categoria: Optional[str] = Query(default=None),
) -> HTMLResponse:
    templates = request.app.state.templates
    all_projects = get_all_excel_projects()

    # Normaliza o filtro recebido via query string
    active_category: Optional[str] = None
    if categoria:
        for cat in EXCEL_CATEGORIES:
            if cat.lower() == categoria.strip().lower():
                active_category = cat
                break

    context = get_base_context(
        page_id="projetos",
        page_title="Projetos Excel | Carlos Daniel",
        description=(
            "Projetos e dashboards em Excel de Carlos Daniel: "
            "análise de dados, automações, relatórios e dashboards interativos."
        ),
    )
    return templates.TemplateResponse(
        "pages/excel_projects.html",
        {
            "request": request,
            "projects": all_projects,
            "excel_categories": EXCEL_CATEGORIES,
            "active_category": active_category,
            **context,
        },
    )
