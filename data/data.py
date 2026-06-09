CLAUDE_MODEL   = "claude-sonnet-4-20250514"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

CATEGORIES = [
    {"id": "ia",         "label": "Inteligencia Artificial", "emoji": "🤖", "color": "#1d4ed8", "bg": "#dbeafe"},
    {"id": "dev",        "label": "Desarrollo",              "emoji": "💻", "color": "#15803d", "bg": "#dcfce7"},
    {"id": "edu",        "label": "Educación",               "emoji": "📚", "color": "#533483", "bg": "#f5f3ff"},
    {"id": "innovation", "label": "Innovación",              "emoji": "💡", "color": "#b45309", "bg": "#fef3c7"},
    {"id": "devops",     "label": "DevOps & Cloud",          "emoji": "☁️", "color": "#0f766e", "bg": "#ccfbf1"},
    {"id": "security",   "label": "Ciberseguridad",          "emoji": "🔐", "color": "#b91c1c", "bg": "#fee2e2"},
    {"id": "energia",    "label": "Energía",                 "emoji": "⚡", "color": "#c2410c", "bg": "#ffedd5"},
]

AI_MODULES = [
    {"id": "assistant",    "label": "Asistente IDEA",     "emoji": "🤖", "desc": "Chat sobre tecnología y IA"},
    {"id": "summarizer",   "label": "Resumidor",          "emoji": "📝", "desc": "Resume textos técnicos"},
    {"id": "codereviewer", "label": "Revisor de Código",  "emoji": "💻", "desc": "Analiza y mejora código"},
    {"id": "forumhelper",  "label": "Ayuda para Foros",   "emoji": "💬", "desc": "Genera respuestas técnicas"},
    {"id": "ideas",        "label": "Generador de Ideas", "emoji": "💡", "desc": "Propone artículos y proyectos"},
]

AI_PROMPTS = {
    "assistant":    "Eres el asistente del blog IDEA, comunidad tecnológica latinoamericana. Responde en español, de forma clara y amigable.",
    "summarizer":   "Genera un resumen estructurado: 1) Resumen ejecutivo, 2) 5 puntos clave, 3) Términos técnicos, 4) Aplicación práctica para LATAM. Responde en español.",
    "codereviewer": "Eres un senior developer. Revisa el código, detecta bugs y malas prácticas. Proporciona código mejorado con explicaciones en español.",
    "forumhelper":  "Genera respuestas técnicas completas para preguntas de foros tecnológicos. Sé específico, incluye código cuando sea útil. Responde en español.",
    "ideas":        "Genera ideas creativas para artículos o proyectos tecnológicos para la comunidad latinoamericana. Incluye título, descripción, dificultad y tiempo estimado. Responde en español.",
}

SAMPLE_ARTICLES = [
    {"id": 1, "category": "ia", "featured": True,
     "title": "El Futuro de la IA Generativa en la Educación Superior",
     "excerpt": "Análisis de cómo los LLMs redefinen los paradigmas de enseñanza en universidades latinoamericanas.",
     "author": "Dra. María Pérez", "init": "MP", "read_time": 12,
     "views": 4200, "likes": 312, "comments": 87,
     "tags": ["IA", "Educación", "LLMs"],
     "content": """La inteligencia artificial generativa ha cruzado el umbral de la experimentación para convertirse en una realidad cotidiana en las aulas universitarias.

## El cambio de paradigma

Durante décadas, la educación superior operó bajo un modelo transmisivo. La IA generativa rompe esta ecuación de tres maneras:

**1. Tutoría personalizada a escala**: Herramientas como Khanmigo pueden ofrecer retroalimentación individualizada a miles de estudiantes simultáneamente.

**2. Evaluación continua y adaptativa**: Los sistemas de IA detectan patrones en las respuestas y ajustan la dificultad en tiempo real.

**3. Generación de contenido contextualizado**: Los docentes pueden crear materiales didácticos personalizados en minutos.

## Desafíos pedagógicos

La pregunta central es: ¿cómo preservar el pensamiento crítico cuando las respuestas correctas son accesibles al instante?

## Conclusión

Las instituciones que integren IA de forma crítica y ética estarán mejor posicionadas para formar profesionales del siglo XXI."""},

    {"id": 2, "category": "dev", "featured": False,
     "title": "RAG con LangChain y Pinecone: Guía práctica paso a paso",
     "excerpt": "Construye un sistema de Retrieval-Augmented Generation que potencia tus apps con conocimiento actualizado.",
     "author": "Carlos Mendoza", "init": "CM", "read_time": 8,
     "views": 3100, "likes": 228, "comments": 54,
     "tags": ["RAG", "LangChain", "Python"],
     "content": """El paradigma RAG se ha consolidado como la arquitectura de referencia para apps de IA con información actualizada.

## ¿Por qué RAG y no fine-tuning?

- **Actualización en tiempo real**: Agrega documentos sin re-entrenar
- **Menor costo**: Sin GPU para entrenamiento
- **Trazabilidad**: Puedes citar las fuentes exactas

## Instalación

```bash
pip install langchain pinecone-client openai
```

## Indexar documentos

```python
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vectorstore = Pinecone.from_documents(
    documents, embeddings, index_name="idea-rag"
)
```

## Query con RAG

```python
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4"),
    retriever=vectorstore.as_retriever()
)
result = qa.run("¿Cómo implementar autenticación OAuth?")
```"""},

    {"id": 3, "category": "edu", "featured": False,
     "title": "Diseño de Micro-credenciales con Metodología Competencial",
     "excerpt": "Framework práctico para diseñar micro-credenciales alineadas con el mercado tecnológico latinoamericano.",
     "author": "Dra. Laura Vásquez", "init": "LV", "read_time": 14,
     "views": 1900, "likes": 156, "comments": 31,
     "tags": ["Educación", "EdTech", "Curriculum"],
     "content": """Las micro-credenciales son una respuesta ágil a la brecha entre la educación formal y el mercado.

## Marco de diseño en 5 etapas

1. **Análisis de demanda laboral** — Relevamiento con empleadores
2. **Mapeo de competencias** — Traducción a objetivos medibles
3. **Diseño instruccional** — Actividades alineadas al perfil de egreso
4. **Evaluación auténtica** — Proyectos reales, no exámenes teóricos
5. **Validación con la industria** — Revisión externa y ajuste continuo

## Ejemplo: Micro-credencial en MLOps

| Componente | Detalle |
|---|---|
| Duración | 80 horas |
| Modalidad | Online asíncrono |
| Proyecto final | Pipeline de ML en producción |
| Evaluador | Senior de empresa aliada |"""},

    {"id": 4, "category": "innovation", "featured": False,
     "title": "Design Sprint para Equipos Remotos en 2025",
     "excerpt": "Adapta el Design Sprint de Google para equipos distribuidos sin perder energía creativa.",
     "author": "Ing. Roberto Silva", "init": "RS", "read_time": 9,
     "views": 2400, "likes": 181, "comments": 38,
     "tags": ["Design Sprint", "Innovación", "Remote"],
     "content": """El Design Sprint de 5 días es perfectamente adaptable al formato remoto con las herramientas correctas.

## Herramientas por fase

| Fase      | Herramienta | Propósito              |
|-----------|-------------|------------------------|
| Entender  | Miro        | Mapas de empatía       |
| Bocetar   | FigJam      | Crazy 8s digitales     |
| Decidir   | Mentimeter  | Dot voting anónimo     |
| Prototipar| Figma       | Prototipo navegable    |
| Testear   | Maze        | Pruebas asíncronas     |

## Claves para el éxito remoto

- **Facilitador dedicado**: Alguien que no participa en el contenido
- **Bloques de 90 min máximo**: Mantiene la energía
- **Async entre sesiones**: Usa Loom para actualizaciones"""},

    {"id": 5, "category": "devops", "featured": False,
     "title": "Kubernetes para Startups: ¿Cuándo adoptarlo?",
     "excerpt": "Análisis honesto sobre los costos reales de Kubernetes vs soluciones más simples.",
     "author": "Patricia Morales", "init": "PM", "read_time": 10,
     "views": 2200, "likes": 167, "comments": 45,
     "tags": ["Kubernetes", "DevOps", "Cloud"],
     "content": """La pregunta no es si Kubernetes es bueno, sino si es el momento correcto.

## Señales de que AÚN no lo necesitas

- Menos de 5 servicios en producción
- Equipo de ingeniería menor a 10 personas
- Sin necesidad de auto-scaling frecuente

## Alternativas más simples

- **Railway** — Deploy en segundos, pricing por uso
- **Render** — Free tier generoso, Postgres incluido
- **Fly.io** — Contenedores sin la complejidad de K8s

## Cuándo SÍ tiene sentido

Cuando tienes más de 20 microservicios, necesitas scheduling avanzado de jobs, o tu equipo ya tiene experiencia con contenedores y quieres portabilidad multi-cloud."""},
]

SAMPLE_FORUMS = [
    {"id": 1, "category": "ia", "solved": False, "votes": 47,
     "title": "¿Mejor estrategia para fine-tuning con datasets pequeños (<1000 ejemplos)?",
     "body": "Trabajo con ~800 ejemplos etiquetados. Probé LoRA y QLoRA con resultados mixtos. ¿Experiencias?",
     "author": "Jorge Mendoza", "init": "JM", "answers": 23, "views": 1200,
     "tags": ["LLMs", "Fine-tuning", "LoRA"]},
    {"id": 2, "category": "dev", "solved": True, "votes": 38,
     "title": "¿React o Vue en 2025 para proyectos empresariales medianos?",
     "body": "Necesito recomendar un stack para 8 desarrolladores que vienen de jQuery. El proyecto es un ERP web.",
     "author": "Andrés R.", "init": "AR", "answers": 61, "views": 3400,
     "tags": ["React", "Vue", "Frontend"]},
    {"id": 3, "category": "edu", "solved": False, "votes": 29,
     "title": "Experiencias con IA en aulas universitarias de primer año",
     "body": "Implemento un piloto con 120 estudiantes de Ing. Sistemas. ¿Cómo balancear IA vs dependencia?",
     "author": "Laura V.", "init": "LV", "answers": 17, "views": 890,
     "tags": ["IA Educativa", "Universidad"]},
    {"id": 4, "category": "devops", "solved": False, "votes": 33,
     "title": "Migración de monolito Django a microservicios sin downtime",
     "body": "Tenemos un monolito Django de 8 años con ~300k líneas. El CTO exige zero downtime. ¿Estrategia recomendada?",
     "author": "Patricia M.", "init": "PM", "answers": 41, "views": 2600,
     "tags": ["Microservicios", "Django", "Migración"]},
]

SAMPLE_MEMBERS = [
    {"id": 1, "name": "Dra. María Pérez",   "init": "MP", "color": "#1d4ed8", "role": "IA & ML Research",    "articles": 24, "forums": 89, "followers": 1840, "reputation": 4200, "badge": "Top Contributor",
     "bio": "Investigadora en NLP y modelos generativos. Doctora en Ciencias de la Computación, UNAM.",
     "skills": ["LLMs", "Python", "NLP", "PyTorch"]},
    {"id": 2, "name": "Carlos Mendoza",     "init": "CM", "color": "#15803d", "role": "Senior Developer",     "articles": 18, "forums": 112, "followers": 1200, "reputation": 3800, "badge": "Expert",
     "bio": "Full-stack developer con 10 años de experiencia. Apasionado por arquitecturas limpias y open source.",
     "skills": ["React", "Node.js", "PostgreSQL", "Docker"]},
    {"id": 3, "name": "Dra. Laura Vásquez", "init": "LV", "color": "#533483", "role": "EdTech Specialist",    "articles": 15, "forums": 67, "followers": 980,  "reputation": 3100, "badge": "Educator",
     "bio": "Especialista en tecnología educativa y diseño instruccional. Promueve el uso ético de la IA en aulas.",
     "skills": ["EdTech", "Moodle", "Pedagogía", "UX"]},
    {"id": 4, "name": "Ing. Roberto Silva", "init": "RS", "color": "#b45309", "role": "Innovation Lead",      "articles": 12, "forums": 54, "followers": 870,  "reputation": 2900, "badge": "Innovator",
     "bio": "Lidera iniciativas de innovación en startups latinoamericanas. Mentor de emprendedores tech.",
     "skills": ["Lean Startup", "Product", "Agile", "Go"]},
    {"id": 5, "name": "Andrés Torres",      "init": "AT", "color": "#0f766e", "role": "Backend Architect",    "articles": 10, "forums": 78, "followers": 720,  "reputation": 2400, "badge": "Builder",
     "bio": "Arquitecto de sistemas distribuidos. Especialista en microservicios y optimización de bases de datos.",
     "skills": ["Microservicios", "Kafka", "Redis", "Kubernetes"]},
    {"id": 6, "name": "Patricia Morales",   "init": "PM", "color": "#b91c1c", "role": "DevOps Engineer",      "articles": 9,  "forums": 91, "followers": 650,  "reputation": 2100, "badge": "Builder",
     "bio": "Ingeniera DevOps con expertise en CI/CD y seguridad cloud. AWS Certified Solutions Architect.",
     "skills": ["AWS", "Terraform", "GitHub Actions", "Docker"]},
]

SAMPLE_PANELS = [
    {"id": "ia",         "emoji": "🤖", "name": "IA & Machine Learning",       "description": "Modelos, algoritmos, ética y aplicaciones de IA en LATAM",       "members": 2300, "posts": 342, "color": "#1d4ed8", "activity": "Alta actividad", "tags": ["LLMs", "Python", "NLP"]},
    {"id": "dev",        "emoji": "💻", "name": "Desarrollo Web & Mobile",     "description": "Frontend, backend, mobile y arquitecturas modernas y escalables", "members": 3100, "posts": 518, "color": "#15803d", "activity": "Muy activo",    "tags": ["React", "Node.js", "APIs"]},
    {"id": "edu",        "emoji": "📚", "name": "EdTech & Pedagogía Digital",  "description": "Innovación educativa, e-learning y gamificación en el aula",      "members": 1800, "posts": 247, "color": "#533483", "activity": "Activo",        "tags": ["Moodle", "IA Edu", "UX"]},
    {"id": "innovation", "emoji": "💡", "name": "Innovación & Startups",       "description": "Lean startup, design thinking y emprendimiento tecnológico",       "members": 1500, "posts": 198, "color": "#b45309", "activity": "Activo",        "tags": ["Startup", "Producto", "Agile"]},
    {"id": "devops",     "emoji": "☁️", "name": "DevOps & Cloud",              "description": "CI/CD, contenedores, Kubernetes y cloud providers en producción",  "members": 1200, "posts": 165, "color": "#0f766e", "activity": "Activo",        "tags": ["Docker", "K8s", "AWS"]},
    {"id": "security",   "emoji": "🔐", "name": "Seguridad & Ciberseguridad",  "description": "Ethical hacking, OWASP, criptografía y seguridad en la nube",     "members": 980,  "posts": 134, "color": "#b91c1c", "activity": "Creciendo",     "tags": ["OWASP", "Pentest", "CTF"]},
]

SAMPLE_EVENTS = [
    {"id": 1, "date_label": "22 Ene", "title": "Webinar: Prompt Engineering Avanzado",
     "type": "Online",     "time": "18:00 ECT", "location": "Zoom",              "registered": 340, "capacity": 500,
     "description": "Técnicas avanzadas de prompt engineering para aplicaciones de producción con Claude y GPT-4."},
    {"id": 2, "date_label": "28 Ene", "title": "Panel: El Futuro del Desarrollo con IA",
     "type": "Online",     "time": "17:00 ECT", "location": "YouTube Live",      "registered": 210, "capacity": 300,
     "description": "Debate entre líderes técnicos sobre cómo la IA está transformando el ciclo de desarrollo de software."},
    {"id": 3, "date_label": "05 Feb", "title": "Taller: Arquitecturas de Microservicios",
     "type": "Presencial", "time": "09:00 ECT", "location": "Bogotá, Colombia",  "registered": 45,  "capacity": 60,
     "description": "Taller práctico de 6 horas: diseña, despliega y monitoriza una arquitectura de microservicios real."},
    {"id": 4, "date_label": "12 Feb", "title": "Hackathon IDEA 2025: Soluciones con IA",
     "type": "Híbrido",    "time": "08:00 ECT", "location": "CDMX + Online",     "registered": 120, "capacity": 200,
     "description": "48 horas para construir soluciones innovadoras con IA que impacten positivamente en LATAM."},
    {"id": 5, "date_label": "19 Feb", "title": "Conferencia: IA en la Educación Superior LATAM",
     "type": "Online",     "time": "15:00 ECT", "location": "Google Meet",       "registered": 280, "capacity": 400,
     "description": "Perspectivas de rectores, docentes e investigadores sobre la integración de IA en universidades."},
]

CONDUCT_RULES = [
    ("Respeto mutuo",  "Críticas a las ideas, nunca a las personas."),
    ("Calidad",        "Contenido original, veraz y bien fundamentado."),
    ("Inclusividad",   "Todos son bienvenidos: principiantes y expertos."),
    ("Colaboración",   "Comparte conocimiento y contribuye positivamente."),
    ("Privacidad",     "No compartas datos personales de otros miembros."),
    ("Transparencia",  "Declara abiertamente tus conflictos de interés."),
]

TRENDING_TAGS = [
    "#ChatGPT", "#Python", "#LLMs", "#EdTech", "#DevOps",
    "#Startup", "#MachineLearning", "#Cloud", "#React", "#LangChain",
]
