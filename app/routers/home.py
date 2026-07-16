"""home.py — Rota da página principal (/)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_base_context

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    context = get_base_context(
        page_id     = "home",
        page_title  = "Carlos Daniel | Engenharia Mecânica · IFCE",
        description = (
            "Portfólio de Carlos Daniel Alves da Silva, estudante de "
            "Engenharia Mecânica no IFCE. Conheça meus projetos e trajetória."
        ),
    )
    return templates.TemplateResponse("pages/home.html", {"request": request, **context})
