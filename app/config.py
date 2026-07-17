"""
config.py — Configurações centralizadas do portfólio.

Todos os dados do estudante e configurações globais ficam aqui.
Os routers importam este módulo para passar contexto aos templates.
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# Dados pessoais do estudante
# ──────────────────────────────────────────────────────────────────────────────
STUDENT = {
    "name":         "Carlos Daniel Alves da Silva",
    "nickname":     "Carlos Daniel",
    "initials":     "CD",
    "title":        "Estudante de Engenharia Mecânica · IFCE",
    "subtitle":     "Engenharia • Tecnologia • Inovação",
    "tagline":      "Transformando estudo em soluções reais.",
    "location":     "Maracanaú, Ceará – Brasil",
    "email":        "alves.silva.carlosd@gmail.com",
    "whatsapp":     "+55 (85) 98675-9763",
    "whatsapp_note": "Preferencialmente mensagens. Não realizo atendimento por chamadas.",
    "availability": "Disponível para estágios e projetos",
    "photo":        "/static/images/profile/carlos-daniel.webp",
    "cv":           "/static/documents/curriculo/Curriculo_Carlos_Daniel_Alves_da_Silva.pdf",
    "github":       "https://github.com/dev-carlosalves",
    "linkedin":     "https://www.linkedin.com/in/carlos-daniel-alves-da-silva-a07128311",
}

# ──────────────────────────────────────────────────────────────────────────────
# SEO — metadados globais (podem ser sobrescritos por página)
# ──────────────────────────────────────────────────────────────────────────────
SEO_BASE = {
    "site_name":    f"Portfólio · {STUDENT['name']}",
    "description":  (
        "Portfólio profissional de Carlos Daniel Alves da Silva, "
        "estudante de Engenharia Mecânica no IFCE. "
        "Projetos, habilidades técnicas e trajetória acadêmica."
    ),
    "keywords":     (
        "engenharia mecânica, IFCE, portfólio, CAD, Fusion 360, "
        "Carlos Daniel, estudante engenharia, projetos mecânicos, Python, FastAPI"
    ),
    "author":       STUDENT["name"],
    "og_image":     "/static/images/og/og-image.png",
    "twitter_card": "summary_large_image",
    "robots":       "index, follow",
    "locale":       "pt_BR",
    "base_url":     "https://carlosdaniel.dev",    # Atualizar ao publicar
}

# ──────────────────────────────────────────────────────────────────────────────
# Navegação — itens do menu principal
# ──────────────────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    {"label": "Início",          "href": "/",                "id": "nav-home"},
    {"label": "Minha Jornada",   "href": "/jornada",         "id": "nav-journey"},
    {"label": "Projetos",        "href": "/projetos",        "id": "nav-projects"},
    {"label": "Laboratório CAD", "href": "/laboratorio-cad", "id": "nav-cad"},
    {"label": "Tecnologias",     "href": "/tecnologias",     "id": "nav-technologies"},
    {"label": "Currículo",       "href": "/curriculo",       "id": "nav-resume"},
    {"label": "Contato",         "href": "/contato",         "id": "nav-contact"},
]


def get_base_context(page_id: str = "home", **kwargs) -> dict:
    """
    Retorna o contexto base passado a todos os templates.
    Cada router pode sobrescrever title, description, etc.
    """
    return {
        "student":   STUDENT,
        "seo":       SEO_BASE,
        "nav_items": NAV_ITEMS,
        "page_id":   page_id,
        **kwargs,
    }
