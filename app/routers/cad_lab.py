"""cad_lab.py — Rota da página Laboratório CAD (/laboratorio-cad)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context

router = APIRouter()


@router.get("/laboratorio-cad", response_class=HTMLResponse, include_in_schema=False)
async def cad_lab(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    context = get_base_context(
        page_id     = "cad",
        page_title  = "Laboratório CAD | Carlos Daniel",
        description = (
            "Galeria de projetos CAD de Carlos Daniel: modelagem 3D, "
            "renderizações e prototipagem no SolidWorks e Fusion 360."
        ),
    )
    return templates.TemplateResponse("pages/cad_lab.html", {"request": request, **context})
