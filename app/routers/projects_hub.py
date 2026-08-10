"""projects_hub.py — Rota do Hub de Projetos.

GET /projetos → página de seleção entre Projetos CAD e Projetos Excel.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context

router = APIRouter()


@router.get("/projetos", response_class=HTMLResponse, include_in_schema=False)
async def projects_hub(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    context = get_base_context(
        page_id="projetos",
        page_title="Projetos | Carlos Daniel",
        description=(
            "Explore os estudos e projetos de Carlos Daniel: modelagem CAD em SolidWorks e AutoCAD, "
            "e práticas de análise de dados em Excel com dashboards e planilhas dinâmicas."
        ),
    )
    return templates.TemplateResponse(
        "pages/projects_hub.html",
        {"request": request, **context},
    )
