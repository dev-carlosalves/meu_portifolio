# Portfólio — Carlos Daniel Alves da Silva

<!-- Banner: adicionar imagem aqui quando disponível -->
<!-- ![Banner do portfólio](app/static/images/og/og-image.png) -->

---

Sou estudante de Engenharia Mecânica no IFCE Campus Maracanaú e comecei a desenvolver esse portfólio porque precisava de um lugar para reunir e documentar tudo que estou construindo ao longo da graduação.

Não queria apenas um site com projetos acabados — queria algo que contasse minha evolução real. Então resolvi construí-lo do zero, aprender o que fosse necessário no processo, e deixar tudo documentado aqui.

O resultado foi bem além do que eu esperava quando comecei.

---

## O que tem aqui

- **Home** — apresentação geral, quem sou e o que estou desenvolvendo
- **Minha Jornada** — linha do tempo da minha trajetória acadêmica e profissional, contada de forma cronológica
- **Projetos em Programação** — projetos Python que desenvolvi, incluindo o Pesquisar+
- **Laboratório CAD** — meus estudos em modelagem 3D com Fusion 360
- **Currículo** — versão interativa do meu currículo, com download do PDF disponível
- **Tecnologias & Competências** — como e por que uso cada tecnologia que aprendi
- **Contato** — formulário funcional (via EmailJS), WhatsApp, LinkedIn e GitHub

---

## Objetivos do projeto

- Reunir meus projetos em um lugar só, com histórico real de evolução
- Ter um currículo online que recrutadores possam acessar rapidamente
- Documentar o que aprendo, não apenas o que já sei
- Servir como vitrine profissional durante a graduação
- Facilitar o contato com empresas, professores e outros estudantes

---

## Tecnologias utilizadas

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — framework que escolhi por ser moderno, rápido e bem documentado
- [Jinja2](https://jinja.palletsprojects.com/) — renderização de templates HTML no servidor
- [Uvicorn](https://www.uvicorn.org/) — servidor ASGI para rodar a aplicação
- Python 3.11+

**Frontend**
- HTML5 e CSS3 (vanilla, sem frameworks CSS)
- JavaScript ES6+ (sem bibliotecas pesadas)
- [AOS](https://michalsnik.github.io/aos/) — animações de scroll
- [Font Awesome 6](https://fontawesome.com/) — ícones
- [Google Fonts](https://fonts.google.com/) — Poppins (títulos) e Inter (texto)

**Integrações**
- [EmailJS](https://www.emailjs.com/) — envio de formulário de contato sem backend próprio, carregado sob demanda

**Versionamento**
- Git + GitHub

**Modelagem CAD**
- Autodesk Fusion 360 — utilizado nos projetos mecânicos documentados no Laboratório CAD

---

## Estrutura do projeto

```
meu_portifolio/
│
├── app/
│   ├── main.py              ← aplicação FastAPI + rota 404 customizada
│   ├── config.py            ← dados pessoais, SEO e itens de navegação centralizados
│   │
│   ├── routers/             ← uma rota por página
│   │   ├── home.py
│   │   ├── journey.py
│   │   ├── projects.py
│   │   ├── cad_lab.py
│   │   ├── resume.py
│   │   ├── technologies.py
│   │   └── contact.py
│   │
│   ├── templates/
│   │   ├── base.html        ← layout base: head, navbar, footer, scripts
│   │   ├── partials/        ← navbar, footer, section_header reutilizáveis
│   │   └── pages/           ← template de cada página
│   │
│   └── static/
│       ├── css/             ← base, layout, components, sections, animations
│       ├── js/              ← main, navbar, aos-init, contact
│       ├── images/          ← profile, projects, cad, og
│       ├── icons/           ← favicon
│       └── documents/       ← currículo PDF e certificados
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Como rodar localmente

**Pré-requisitos:** Python 3.11+

```bash
# 1. Clone o repositório
git clone https://github.com/dev-carlosalves/meu_portifolio.git
cd meu_portifolio

# 2. Crie e ative o ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o servidor
uvicorn app.main:app --reload
```

Acesse: **http://localhost:8000**

---

## Configurando o formulário de contato (EmailJS)

O formulário de contato usa EmailJS. Para funcionar, você precisa substituir as credenciais no arquivo `app/static/js/contact.js`:

```javascript
const EMAILJS_PUBLIC_KEY  = 'sua_public_key';
const EMAILJS_SERVICE_ID  = 'seu_service_id';
const EMAILJS_TEMPLATE_ID = 'seu_template_id';
```

Os campos que o template do EmailJS precisa receber são: `name`, `email`, `subject` e `message`.

---

## Sobre o Pesquisar+

O principal projeto que estou desenvolvendo atualmente. É uma plataforma de busca acadêmica que integra diversas fontes de pesquisa em uma única interface.

O repositório permanece privado enquanto o desenvolvimento está em andamento, mas a aplicação está disponível publicamente:

🔗 **[pesquisar-plus.onrender.com](https://pesquisar-plus.onrender.com/)**

Várias funcionalidades ainda estão sendo desenvolvidas — é um trabalho em progresso deliberado.

---

## Ainda vou fazer

- Adicionar foto de perfil real
- Publicar os primeiros projetos do Laboratório CAD à medida que os modelos ficam prontos
- Gravar um vídeo curto de apresentação do portfólio
- Adicionar mais projetos Python conforme avanço nos estudos
- Melhorar o SEO e fazer o deploy em produção
- Expandir a seção de tecnologias com novos aprendizados

---

## O que aprendi construindo isso

Quando comecei, tinha uma ideia simples. Conforme fui desenvolvendo, percebi que um projeto desse tipo envolve muito mais do que parece.

Aprendi bastante sobre como estruturar uma aplicação de verdade — separar responsabilidades, criar componentes reutilizáveis, centralizar configurações. FastAPI me mostrou como um backend Python pode ser elegante. Jinja2 me ensinou como renderização server-side funciona na prática.

No frontend, escrever CSS vanilla do zero, sem frameworks, me fez entender o que os frameworks realmente resolvem. Criar um design system próprio com variáveis CSS foi uma das partes mais satisfatórias do projeto.

Git e GitHub se tornaram naturais no processo. E o maior aprendizado foi perceber que documentar enquanto você constrói é completamente diferente de tentar documentar depois.

---

## Contato

Se tiver interesse em conversar sobre oportunidades, projetos ou só trocar ideia:

- **E-mail:** alves.silva.carlosd@gmail.com
- **WhatsApp:** +55 (85) 98675-9763 *(preferencialmente mensagens)*
- **LinkedIn:** [carlos-daniel-alves-da-silva](https://www.linkedin.com/in/carlos-daniel-alves-da-silva-a07128311)
- **GitHub:** [dev-carlosalves](https://github.com/dev-carlosalves)

---

## Licença

Projeto pessoal desenvolvido para fins acadêmicos e profissionais.  
Todos os direitos reservados a Carlos Daniel Alves da Silva.
