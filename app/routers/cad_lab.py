"""cad_lab.py — Rotas do Laboratório CAD.

GET /laboratorio-cad           → tela de seleção de software + catálogo filtrado
GET /laboratorio-cad/{slug}    → página individual do estudo de caso

Query param opcional: ?software=Fusion+360 | SolidWorks | AutoCAD
"""

from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context
from app.database import get_all_projects, get_project_by_slug

router = APIRouter()

# Softwares suportados no Laboratório CAD
CAD_SOFTWARES = ["Fusion 360", "SolidWorks", "AutoCAD"]


@router.get("/laboratorio-cad", response_class=HTMLResponse, include_in_schema=False)
async def cad_lab_catalog(
    request: Request,
    software: Optional[str] = Query(default=None),
) -> HTMLResponse:
    templates = request.app.state.templates
    all_projects = get_all_projects()

    # Normaliza o filtro recebido via query string
    active_software: Optional[str] = None
    if software:
        # Tenta encontrar correspondência case-insensitive
        for sw in CAD_SOFTWARES:
            if sw.lower() == software.strip().lower():
                active_software = sw
                break

    context = get_base_context(
        page_id="cad",
        page_title="Laboratório CAD | Carlos Daniel",
        description=(
            "Laboratório de projetos CAD de Carlos Daniel: modelagem 3D paramétrica, "
            "montagens técnicas e documentação em Fusion 360, SolidWorks e AutoCAD."
        ),
    )
    return templates.TemplateResponse(
        "pages/cad_lab.html",
        {
            "request": request,
            "projects": all_projects,
            "cad_softwares": CAD_SOFTWARES,
            "active_software": active_software,
            **context,
        },
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
