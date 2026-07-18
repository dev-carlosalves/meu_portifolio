"""cad_lab.py — Rotas do Laboratório CAD.

GET /laboratorio-cad       → catálogo de projetos (lista de cards)
GET /laboratorio-cad/{slug} → página individual do estudo de caso
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context
from app.database import get_all_projects, get_project_by_slug

router = APIRouter()


@router.get("/laboratorio-cad", response_class=HTMLResponse, include_in_schema=False)
async def cad_lab_catalog(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    projects = get_all_projects()
    context = get_base_context(
        page_id="cad",
        page_title="Laboratório CAD | Carlos Daniel",
        description=(
            "Laboratório de projetos CAD de Carlos Daniel: modelagem 3D paramétrica, "
            "documentação técnica, montagens e vista explodida no Fusion 360."
        ),
    )
    return templates.TemplateResponse(
        "pages/cad_lab.html",
        {"request": request, "projects": projects, **context},
    )


@router.get("/laboratorio-cad/{slug}", response_class=HTMLResponse, include_in_schema=False)
async def cad_project_detail(request: Request, slug: str) -> HTMLResponse:
    templates = request.app.state.templates
    project = get_project_by_slug(slug)
    if not project:
        context = get_base_context(
            page_id="cad",
            page_title="Projeto não encontrado | Carlos Daniel",
        )
        return templates.TemplateResponse(
            "pages/404.html",
            {"request": request, **context},
            status_code=404,
        )
    context = get_base_context(
        page_id="cad",
        page_title=f"{project['title']} | Laboratório CAD | Carlos Daniel",
        description=project.get("short_desc", ""),
    )
    return templates.TemplateResponse(
        "pages/cad_project.html",
        {"request": request, "project": project, **context},
    )
