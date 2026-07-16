"""
main.py — Ponto de entrada da aplicação FastAPI.

Responsabilidades:
- Inicializar o app FastAPI com metadata
- Montar arquivos estáticos
- Registrar todos os routers
- Configurar Jinja2Templates
- Definir handler de erros globais
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_base_context
from app.routers import (
    cad_lab,
    contact,
    home,
    journey,
    projects,
    resume,
    technologies,
)

# ──────────────────────────────────────────────────────────────────────────────
# Caminhos base
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent
STATIC_DIR    = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# ──────────────────────────────────────────────────────────────────────────────
# Instância FastAPI
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "Portfólio — Carlos Daniel Alves da Silva",
    description = "Portfólio profissional de estudante de Engenharia Mecânica do IFCE.",
    version     = "1.0.0",
    docs_url    = None,   # Desabilita /docs em produção
    redoc_url   = None,
)

# ──────────────────────────────────────────────────────────────────────────────
# Arquivos estáticos
# ──────────────────────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ──────────────────────────────────────────────────────────────────────────────
# Templates Jinja2 — disponível globalmente via request.app.state
# ──────────────────────────────────────────────────────────────────────────────
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.state.templates = templates

# ──────────────────────────────────────────────────────────────────────────────
# Routers
# ──────────────────────────────────────────────────────────────────────────────
app.include_router(home.router)
app.include_router(journey.router)
app.include_router(projects.router)
app.include_router(cad_lab.router)
app.include_router(technologies.router)
app.include_router(resume.router)
app.include_router(contact.router)


# ──────────────────────────────────────────────────────────────────────────────
# Handlers de erro customizados
# ──────────────────────────────────────────────────────────────────────────────
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> HTMLResponse:
    context = get_base_context(
        page_id     = "404",
        page_title  = "Página Não Encontrada | Carlos Daniel",
        description = "Página não encontrada no portfólio de Carlos Daniel.",
    )
    return templates.TemplateResponse(
        "pages/404.html",
        {"request": request, **context},
        status_code=404,
    )
