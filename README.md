# Portfólio Profissional — Carlos Daniel Alves da Silva

> Portfólio de estudante de Engenharia Mecânica no IFCE, construído com FastAPI + Jinja2 + TailwindCSS.

---

## 🚀 Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Backend | FastAPI · Jinja2 · Python 3.11+ |
| Frontend | HTML5 · CSS3 · JavaScript ES6+ |
| Estilo | TailwindCSS (CDN) · CSS Custom Properties |
| Fontes | Google Fonts (Poppins + Inter) |
| Ícones | Font Awesome 6 |
| Animações | AOS (Animate On Scroll) |
| Contato | EmailJS (Sprint 7) |

---

## 📁 Estrutura do Projeto

```
meu_portifolio/
│
├── app/
│   ├── __init__.py
│   ├── main.py              ← FastAPI app
│   ├── config.py            ← Dados do estudante + configurações
│   │
│   ├── routers/             ← Uma rota por página
│   │   ├── home.py
│   │   ├── journey.py
│   │   ├── projects.py
│   │   ├── cad_lab.py
│   │   ├── resume.py
│   │   └── contact.py
│   │
│   ├── templates/           ← Jinja2 templates
│   │   ├── base.html        ← Layout base (head, navbar, footer)
│   │   ├── partials/
│   │   │   ├── navbar.html
│   │   │   ├── footer.html
│   │   │   └── section_header.html
│   │   └── pages/
│   │       ├── home.html
│   │       ├── journey.html
│   │       ├── projects.html
│   │       ├── cad_lab.html
│   │       ├── resume.html
│   │       ├── contact.html
│   │       └── 404.html
│   │
│   └── static/
│       ├── css/
│       │   ├── base.css        ← Design tokens, reset, tipografia
│       │   ├── layout.css      ← Navbar, footer, container
│       │   ├── components.css  ← Todos os componentes reutilizáveis
│       │   ├── sections.css    ← Estilos específicos por seção
│       │   └── animations.css  ← Keyframes e microinterações
│       ├── js/
│       │   ├── main.js         ← Bootstrap principal
│       │   ├── navbar.js       ← Comportamento da navbar
│       │   ├── aos-init.js     ← Configuração AOS
│       │   └── contact.js      ← Formulário de contato
│       ├── images/
│       │   ├── profile/        ← Foto de Carlos Daniel
│       │   ├── projects/       ← Screenshots de projetos
│       │   ├── cad/            ← Capturas CAD/3D
│       │   └── og/             ← Imagem Open Graph
│       ├── icons/              ← Favicon, ícones SVG
│       ├── videos/             ← Vídeos futuros
│       └── documents/
│           ├── curriculo/      ← Currículo PDF
│           └── certificates/   ← Certificados
│
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

---

## ⚙️ Como Rodar Localmente

### Pré-requisitos
- Python 3.11+
- pip

### 1. Criar ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com seus dados (obrigatório apenas na Sprint 7)
```

### 4. Rodar o servidor

```bash
uvicorn app.main:app --reload
```

Acesse: **http://localhost:8000**

---

## 🌐 Páginas

| Rota | Descrição | Sprint |
|------|-----------|--------|
| `/` | Página principal (Hero + About + Skills) | 2 |
| `/jornada` | Linha do tempo acadêmica | 3 |
| `/projetos` | Grid de projetos com filtros | 4 |
| `/laboratorio-cad` | Galeria de modelagem 3D | 5 |
| `/curriculo` | Currículo com PDF viewer | 6 |
| `/contato` | Formulário de contato | 7 |

---

## 🎨 Design System

### Paleta de Cores

| Token | Hex | Uso |
|-------|-----|-----|
| `--color-bg-primary` | `#09090B` | Fundo principal |
| `--color-bg-secondary` | `#18181B` | Seções alternadas |
| `--color-bg-card` | `#27272A` | Cards |
| `--color-text` | `#FAFAFA` | Texto principal |
| `--color-text-muted` | `#A1A1AA` | Texto secundário |
| `--color-accent` | `#06B6D4` | Destaque (ciano) |
| `--color-accent-hover` | `#22D3EE` | Hover do destaque |

### Tipografia

| Uso | Fonte |
|-----|-------|
| Títulos | Poppins (700, 800, 900) |
| Texto | Inter (300, 400, 500, 600) |

---

## 📋 Sprint Roadmap

| Sprint | Status | Objetivo |
|--------|--------|----------|
| 1 | ✅ Completo | Arquitetura, design system, componentes base |
| 2 | ⏳ Próximo | Conteúdo real: Hero, About, Skills |
| 3 | 🔲 Pendente | Minha Jornada (timeline acadêmica) |
| 4 | 🔲 Pendente | Projetos (cards + filtros) |
| 5 | 🔲 Pendente | Laboratório CAD (galeria 3D) |
| 6 | 🔲 Pendente | Currículo (PDF viewer) |
| 7 | 🔲 Pendente | Contato (integração EmailJS) |
| 8 | 🔲 Pendente | Performance, SEO, testes, deploy |

---

## 📄 Licença

Projeto pessoal de Carlos Daniel Alves da Silva.
Todos os direitos reservados.
