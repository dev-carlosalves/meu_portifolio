"""projects.py — Rota da página de Projetos (/projetos)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context

router = APIRouter()


@router.get("/projetos", response_class=HTMLResponse, include_in_schema=False)
async def projects(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    context = get_base_context(
        page_id     = "projects",
        page_title  = "Projetos | Carlos Daniel",
        description = (
            "Veja os projetos desenvolvidos por Carlos Daniel durante a "
            "graduação em Engenharia Mecânica: simulações, CAD, programação e mais."
        ),
    )
    return templates.TemplateResponse("pages/projects.html", {"request": request, **context})
