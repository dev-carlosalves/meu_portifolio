"""cad_projects.py — Rotas dos Projetos CAD.

GET /projetos/cad           → catálogo de projetos CAD (SolidWorks e AutoCAD)
GET /projetos/cad/{slug}    → página individual do projeto CAD
"""

from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context
from app.database import get_all_projects, get_project_by_slug

router = APIRouter()

# Softwares suportados — sem Fusion 360
CAD_SOFTWARES = ["SolidWorks", "AutoCAD"]


@router.get("/projetos/cad", response_class=HTMLResponse, include_in_schema=False)
async def cad_projects_catalog(
    request: Request,
    software: Optional[str] = Query(default=None),
) -> HTMLResponse:
    templates = request.app.state.templates
    all_projects = get_all_projects()

    # Normaliza o filtro recebido via query string
    active_software: Optional[str] = None
    if software:
        for sw in CAD_SOFTWARES:
            if sw.lower() == software.strip().lower():
                active_software = sw
                break

    context = get_base_context(
        page_id="projetos",
        page_title="Projetos CAD | Carlos Daniel",
        description=(
            "Projetos de modelagem CAD de Carlos Daniel: modelagem 3D paramétrica, "
            "montagens técnicas e documentação em SolidWorks e AutoCAD."
        ),
    )
    return templates.TemplateResponse(
        "pages/cad_projects.html",
        {
            "request": request,
            "projects": all_projects,
            "cad_softwares": CAD_SOFTWARES,
            "active_software": active_software,
            **context,
        },
    )


@router.get("/projetos/cad/{slug}", response_class=HTMLResponse, include_in_schema=False)
async def cad_project_detail(request: Request, slug: str) -> HTMLResponse:
    templates = request.app.state.templates
    project = get_project_by_slug(slug)
    if not project:
        context = get_base_context(
            page_id="projetos",
            page_title="Projeto não encontrado | Carlos Daniel",
        )
        return templates.TemplateResponse(
            "pages/404.html",
            {"request": request, **context},
            status_code=404,
        )
    context = get_base_context(
        page_id="projetos",
        page_title=f"{project['title']} | Projetos CAD | Carlos Daniel",
        description=project.get("short_desc", ""),
    )
    return templates.TemplateResponse(
        "pages/cad_project.html",
        {"request": request, "project": project, **context},
    )
