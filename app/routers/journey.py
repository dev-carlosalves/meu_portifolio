"""journey.py — Rota da página Minha Jornada (/jornada)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context

router = APIRouter()


@router.get("/jornada", response_class=HTMLResponse, include_in_schema=False)
async def journey(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    context = get_base_context(
        page_id     = "journey",
        page_title  = "Minha Jornada | Carlos Daniel",
        description = (
            "Acompanhe a trajetória acadêmica e profissional de Carlos Daniel "
            "na Engenharia Mecânica do IFCE — semestre a semestre."
        ),
    )
    return templates.TemplateResponse("pages/journey.html", {"request": request, **context})
