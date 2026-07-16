"""resume.py — Rota da página Currículo (/curriculo)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context

router = APIRouter()


@router.get("/curriculo", response_class=HTMLResponse, include_in_schema=False)
async def resume(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    context = get_base_context(
        page_id     = "resume",
        page_title  = "Currículo | Carlos Daniel",
        description = (
            "Currículo completo de Carlos Daniel Alves da Silva: "
            "formação, habilidades técnicas, certificados e experiências."
        ),
    )
    return templates.TemplateResponse("pages/resume.html", {"request": request, **context})
