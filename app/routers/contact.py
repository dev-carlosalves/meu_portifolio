"""contact.py — Rotas da página de Contato (/contato)."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.config import get_base_context

router = APIRouter()


@router.get("/contato", response_class=HTMLResponse, include_in_schema=False)
async def contact_page(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    context = get_base_context(
        page_id     = "contact",
        page_title  = "Contato | Carlos Daniel",
        description = (
            "Entre em contato com Carlos Daniel para projetos, estágios "
            "ou colaborações em engenharia e tecnologia."
        ),
    )
    return templates.TemplateResponse("pages/contact.html", {"request": request, **context})


# Rota POST reservada para integração futura (EmailJS / SMTP)
@router.post("/api/contact", include_in_schema=False)
async def contact_submit(request: Request) -> JSONResponse:
    """
    Placeholder para envio de formulário de contato.
    Será implementado na Sprint 7 com EmailJS ou SMTP.
    """
    return JSONResponse(
        {"status": "ok", "message": "Endpoint reservado para Sprint 7."},
        status_code=200,
    )
