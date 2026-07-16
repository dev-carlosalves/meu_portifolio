"""technologies.py — Rota da página de Tecnologias e Competências (/tecnologias)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context

router = APIRouter()


@router.get("/tecnologias", response_class=HTMLResponse, include_in_schema=False)
async def technologies(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    context = get_base_context(
        page_id     = "technologies",
        page_title  = "Tecnologias & Competências | Carlos Daniel",
        description = (
            "Explore as tecnologias e competências de Carlos Daniel: "
            "Python, FastAPI, modelagem tridimensional com Fusion 360 e mais."
        ),
    )
    return templates.TemplateResponse("pages/technologies.html", {"request": request, **context})
