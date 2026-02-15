from flask import Flask, render_template

app = Flask(__name__)

# --- DADOS DO PORTFÓLIO ---

info = {
    "name": "Carlos Daniel Alves",
    "role": "Engenharia Mecânica & Desenvolvimento Python",
    "highlight": "Integro conhecimentos de engenharia mecânica com programação para criar soluções digitais eficientes para empresas.",
    "social": {
        "github": "https://github.com/dev-carlosalves",
        # SEU LINKEDIN NOVO AQUI EMBAIXO:
        "linkedin": "https://www.linkedin.com/in/carlos-daniel-alves-da-silva-a07128311", 
        "email": "carlos.alves@exemplo.com"
    }
}

about_text = [
    "Sou estudante de Engenharia Mecânica no IFCE – Campus Maracanaú (3º semestre) e Técnico em Mecânica Industrial, com experiência prática no setor automotivo diesel e forte interesse em tecnologia aplicada à resolução de problemas empresariais.",
    "Atualmente estou me desenvolvendo na área de programação com foco em Python para automação de tarefas, análise de dados e criação de aplicações web com Flask. Busco unir meus conhecimentos técnicos da engenharia com soluções digitais que otimizem processos, reduzam falhas e aumentem a eficiência operacional das empresas.",
    "Possuo base sólida em disciplinas da engenharia como metrologia, manutenção industrial, desenho técnico e análise de dados, o que me permite compreender processos produtivos e transformá-los em soluções práticas por meio da tecnologia.",
    "Sou dedicado, organizado, curioso e estou em constante aprendizado, sempre buscando evoluir técnica e profissionalmente."
]

tech_stack = [
    {"name": "Python (Intermediário)", "level": 60, "icon": "fab fa-python"},
    {"name": "HTML5 (Básico)", "level": 25, "icon": "fab fa-html5"},
    {"name": "CSS3 (Básico)", "level": 25, "icon": "fab fa-css3-alt"},
]

tools = [
    "Autodesk Inventor (3D)",
    "AutoCAD (Desenhos Técnicos)",
    "Leitura de Desenhos Técnicos",
    "Análise Técnica com Planilhas"
]

education = [
    {
        "course": "Engenharia Mecânica",
        "school": "IFCE Campus Maracanaú",
        "status": "3º semestre – Em andamento"
    },
    {
        "course": "Técnico em Mecânica Industrial",
        "school": "Instituição Técnica",
        "status": "Concluído"
    }
]

extra_courses = [
    "Autodesk Inventor (Tesla Treinamentos) — Do básico ao avançado",
    "Excel Intermediário ao Avançado",
    "Formação em Python para Automação e Dados",
    "Inglês (CLM) — Em aprendizado"
]

competencies = [
    "Automação de Processos Industriais",
    "Desenvolvimento Web (Flask)",
    "Aplicação de Conceitos de Engenharia",
    "Organização de Dados Técnicos",
    "Resolução de Problemas Operacionais",
    "Melhoria Contínua de Processos"
]

@app.route("/")
def home():
    return render_template(
        "index.html", 
        info=info, 
        about_text=about_text, 
        tech_stack=tech_stack, 
        tools=tools,
        education=education,
        extra_courses=extra_courses,
        competencies=competencies
        # Removi "projects=projects" daqui pois não vamos mais usar
    )

if __name__ == "__main__":
    app.run(debug=True)