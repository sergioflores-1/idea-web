import json, os, requests
from flask import (Flask, render_template, request, session,
                   jsonify, Response, redirect, url_for, abort)
import markdown as md
import bcrypt

from data.data import (SAMPLE_ARTICLES, SAMPLE_FORUMS, SAMPLE_MEMBERS,
                       SAMPLE_PANELS, SAMPLE_EVENTS, CATEGORIES,
                       AI_MODULES, AI_PROMPTS, CONDUCT_RULES, TRENDING_TAGS,
                       CLAUDE_API_URL, CLAUDE_MODEL)
from models import db, User, Article, Forum, Comment

# ── App & DB setup ─────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "idea-blog-dev-secret-2025")

ADMIN_EMAIL   = os.environ.get("ADMIN_EMAIL", "sflores@alumni.stanford.edu")
CONTACT_EMAIL = ADMIN_EMAIL
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///idea.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"]        = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"]             = 25 * 1024 * 1024  # 25 MB max upload
db.init_app(app)

# ── Helpers ────────────────────────────────────────────────────────────────────

AVATAR_COLORS = ["#1d4ed8", "#15803d", "#533483", "#b45309", "#0f766e", "#b91c1c"]

def user_color(uid: int) -> str:
    return AVATAR_COLORS[(uid - 1) % len(AVATAR_COLORS)]

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def check_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

def is_admin() -> bool:
    u = session.get("user")
    return bool(u and u.get("email") == ADMIN_EMAIL)

def get_cat(cat_id):
    return next((c for c in CATEGORIES if c["id"] == cat_id),
                {"id": cat_id, "label": cat_id, "emoji": "📄",
                 "color": "#666", "bg": "#eee"})

def render_md(text: str) -> str:
    """Render Markdown or pass through HTML (from visual editor)."""
    if not text:
        return ""
    stripped = text.strip()
    if stripped.startswith("<") and stripped != "<p><br></p>":
        return stripped   # Ya es HTML del editor visual
    return md.markdown(stripped, extensions=["fenced_code", "tables", "nl2br"])

# ── DB initialisation & seed ───────────────────────────────────────────────────

def _ensure_pdf_columns():
    """Add is_pdf / pdf_data columns to existing article tables (safe migration)."""
    from sqlalchemy import text, inspect as sa_inspect
    insp = sa_inspect(db.engine)
    if not insp.has_table("articles"):
        return  # fresh DB — create_all will handle it
    existing = {col["name"] for col in insp.get_columns("articles")}
    is_pg = "postgresql" in str(db.engine.url)
    stmts = []
    if "is_pdf" not in existing:
        stmts.append(f"ALTER TABLE articles ADD COLUMN is_pdf BOOLEAN DEFAULT {'FALSE' if is_pg else '0'}")
    if "pdf_data" not in existing:
        stmts.append(f"ALTER TABLE articles ADD COLUMN pdf_data {'BYTEA' if is_pg else 'BLOB'}")
    if stmts:
        with db.engine.begin() as conn:
            for stmt in stmts:
                conn.execute(text(stmt))


def _seed_if_empty():
    """Populate tables on first deploy; skip if data already exists."""
    if Article.query.count() > 0:
        return

    # Admin user
    admin_pwd = os.environ.get("ADMIN_PASSWORD", "idea-admin-2025")
    admin_init = "SF"
    admin = User(
        email         = ADMIN_EMAIL,
        password_hash = hash_password(admin_pwd),
        first_name    = "Sergio",
        last_name     = "Flores",
        alias         = "sflores",
        init          = admin_init,
        is_admin      = True,
    )
    db.session.add(admin)

    # Sample articles
    for a in SAMPLE_ARTICLES:
        tags_csv = ",".join(a.get("tags", []))
        art = Article(
            id             = a["id"],
            category       = a["category"],
            featured       = a.get("featured", False),
            title          = a["title"],
            excerpt        = a["excerpt"],
            content        = a.get("content", ""),
            author         = a["author"],
            init           = a.get("init", ""),
            read_time      = a.get("read_time", 5),
            views          = a.get("views", 0),
            likes          = a.get("likes", 0),
            comments_count = a.get("comments", 0),
            _tags          = tags_csv,
        )
        db.session.add(art)

    # Sample forums (without comments)
    for f in SAMPLE_FORUMS:
        tags_csv = ",".join(f.get("tags", []))
        forum = Forum(
            id       = f["id"],
            category = f["category"],
            solved   = f.get("solved", False),
            title    = f["title"],
            body     = f.get("body", ""),
            author   = f["author"],
            init     = f.get("init", ""),
            votes    = f.get("votes", 0),
            views    = f.get("views", 0),
            _tags    = tags_csv,
        )
        db.session.add(forum)

    db.session.commit()


with app.app_context():
    db.create_all()
    _ensure_pdf_columns()
    _seed_if_empty()

# ── Context processor ──────────────────────────────────────────────────────────

@app.context_processor
def inject_globals():
    return dict(
        user          = session.get("user"),
        is_admin      = is_admin(),
        contact_email = CONTACT_EMAIL,
        categories    = CATEGORIES,
        trending_tags = TRENDING_TAGS,
        conduct_rules = CONDUCT_RULES,
        get_cat       = get_cat,
    )

# ── Pages ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    arts     = Article.query.order_by(Article.created_at.desc()).all()
    featured = next((a for a in arts if a.featured), arts[0] if arts else None)
    forums   = Forum.query.order_by(Forum.created_at.desc()).limit(3).all()
    return render_template("index.html",
                           articles=arts,
                           forums=forums,
                           featured=featured)


@app.route("/articles")
def articles():
    cat = request.args.get("cat", "all")
    q   = request.args.get("q", "").strip()
    query = Article.query
    if cat != "all":
        query = query.filter_by(category=cat)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Article.title.ilike(like)) | (Article.excerpt.ilike(like))
        )
    arts = query.order_by(Article.created_at.desc()).all()
    return render_template("articles.html", articles=arts, cat=cat, q=q)


@app.route("/articles/<int:article_id>")
def article_detail(article_id):
    art = Article.query.get(article_id)
    if not art:
        return redirect(url_for("articles"))
    art.views += 1
    db.session.commit()
    return render_template("article_detail.html",
                           article=art,
                           content_html=render_md(art.content))


@app.route("/articles/<int:article_id>/view-pdf")
def view_pdf(article_id):
    """Serve the raw PDF bytes stored for a PDF article."""
    art = Article.query.get(article_id)
    if not art or not art.is_pdf or not art.pdf_data:
        abort(404)
    return Response(art.pdf_data, mimetype="application/pdf",
                    headers={"Content-Disposition": "inline"})


@app.route("/articles/<int:article_id>/download")
def download_article(article_id):
    if not session.get("user"):
        return redirect(url_for("article_detail", article_id=article_id))
    art = Article.query.get(article_id)
    if not art:
        return redirect(url_for("articles"))

    import re, unicodedata

    # Nombre de archivo seguro
    safe = unicodedata.normalize("NFKD", art.title[:50])
    safe = re.sub(r"[^\w\s-]", "", safe).strip().lower()
    safe = re.sub(r"[\s]+", "-", safe)

    # Artículo PDF nativo → servir el PDF original directamente
    if art.is_pdf and art.pdf_data:
        return Response(
            art.pdf_data,
            mimetype="application/pdf",
            headers={"Content-Disposition":
                     f'attachment; filename="idea-{safe}.pdf"'},
        )

    content_html = render_md(art.content)
    cat          = get_cat(art.category)

    try:
        from weasyprint import HTML as WP_HTML
        html_str  = render_template("article_pdf.html",
                                    article=art,
                                    content_html=content_html,
                                    cat=cat)
        pdf_bytes = WP_HTML(string=html_str,
                            base_url=request.host_url).write_pdf()
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition":
                     f'attachment; filename="idea-{safe}.pdf"'},
        )
    except (ImportError, OSError):
        # Fallback: HTML standalone (entorno sin GTK, ej. Windows dev)
        html_str = render_template("article_download.html",
                                   article=art,
                                   content_html=content_html,
                                   get_cat=get_cat)
        return Response(
            html_str,
            mimetype="text/html",
            headers={"Content-Disposition":
                     f'attachment; filename="idea-{safe}.html"'},
        )


@app.route("/forums")
def forums():
    sort  = request.args.get("sort", "recent")
    query = Forum.query
    if sort == "votes":
        query = query.order_by(Forum.votes.desc())
    elif sort == "solved":
        query = query.filter_by(solved=True).order_by(Forum.created_at.desc())
    else:
        query = query.order_by(Forum.created_at.desc())
    fs = query.all()
    return render_template("forums.html", forums=fs, sort=sort)


@app.route("/forums/<int:forum_id>")
def forum_detail(forum_id):
    forum = Forum.query.get(forum_id)
    if not forum:
        return redirect(url_for("forums"))
    forum.views += 1
    db.session.commit()
    comments = Comment.query.filter_by(forum_id=forum_id)\
                            .order_by(Comment.created_at).all()
    return render_template("forum_detail.html", forum=forum, comments=comments)


@app.route("/panels")
def panels():
    return render_template("panels.html", panels=SAMPLE_PANELS)


@app.route("/events")
def events():
    return render_template("events.html", events=SAMPLE_EVENTS)


@app.route("/members")
def members():
    return render_template("members.html", members=SAMPLE_MEMBERS)


@app.route("/ai")
def ai_hub():
    mode    = request.args.get("mode", "assistant")
    prefill = request.args.get("text", "")
    return render_template("ai_hub.html",
                           modules=AI_MODULES,
                           mode=mode,
                           prefill=prefill)

# ── Auth ───────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["POST"])
def login():
    data  = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    pwd   = data.get("password") or ""

    if not email or not pwd:
        return jsonify({"error": "Completa todos los campos"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password(pwd, user.password_hash):
        return jsonify({"error": "Email o contraseña incorrectos"}), 401

    session["user"] = user.to_session()
    return jsonify({"ok": True, "user": session["user"]})


@app.route("/register", methods=["POST"])
def register():
    data  = request.get_json() or {}
    first = (data.get("first") or "").strip()
    last  = (data.get("last")  or "").strip()
    email = (data.get("email") or "").strip().lower()
    pwd   = data.get("password") or ""
    alias = (data.get("alias") or "").strip().lstrip("@")

    if not first or not email or not pwd:
        return jsonify({"error": "Completa los campos obligatorios"}), 400
    if len(pwd) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Ya existe una cuenta con ese email"}), 409

    if alias and User.query.filter_by(alias=alias).first():
        return jsonify({"error": "Ese alias ya está en uso"}), 409

    init = (first[0] + (last[0] if last else
            (first[1] if len(first) > 1 else "X"))).upper()

    user = User(
        email         = email,
        password_hash = hash_password(pwd),
        first_name    = first,
        last_name     = last,
        alias         = alias,
        init          = init,
        is_admin      = (email == ADMIN_EMAIL),
    )
    db.session.add(user)
    db.session.commit()

    session["user"] = user.to_session()
    return jsonify({"ok": True, "user": session["user"]})


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"ok": True})

# ── Claude SSE proxy ───────────────────────────────────────────────────────────

@app.route("/api/claude", methods=["POST"])
def claude_proxy():
    data     = request.get_json() or {}
    api_key  = (data.get("api_key") or "").strip()
    messages = data.get("messages", [])
    system   = data.get("system", "")

    if not api_key or not api_key.startswith("sk-"):
        return jsonify({"error": "API key inválida o faltante"}), 400

    def generate():
        payload = {
            "model":      CLAUDE_MODEL,
            "max_tokens": 2000,
            "stream":     True,
            "messages":   messages,
        }
        if system:
            payload["system"] = system

        headers = {
            "Content-Type":      "application/json",
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
        }
        try:
            with requests.post(CLAUDE_API_URL, headers=headers,
                               json=payload, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                for raw in resp.iter_lines():
                    if not raw:
                        continue
                    line = raw.decode("utf-8", errors="ignore")
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        yield "data: [DONE]\n\n"
                        break
                    try:
                        evt = json.loads(data_str)
                        if (evt.get("type") == "content_block_delta"
                                and evt.get("delta", {}).get("type") == "text_delta"):
                            chunk = evt["delta"]["text"]
                            yield f"data: {json.dumps({'text': chunk})}\n\n"
                    except json.JSONDecodeError:
                        pass
        except requests.exceptions.HTTPError as e:
            try:
                msg = e.response.json().get("error", {}).get("message", str(e))
            except Exception:
                msg = str(e)
            yield f"data: {json.dumps({'error': msg})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache",
                             "X-Accel-Buffering": "no"})


@app.route("/api/join-panel", methods=["POST"])
def join_panel():
    panel_id = (request.get_json() or {}).get("panel_id")
    panel = next((p for p in SAMPLE_PANELS if p["id"] == panel_id), None)
    if not panel:
        return jsonify({"error": "Panel no encontrado"}), 404
    return jsonify({"ok": True, "message": f"Te uniste a '{panel['name']}' ✓"})


@app.route("/api/register-event", methods=["POST"])
def register_event():
    event_id = (request.get_json() or {}).get("event_id")
    event = next((e for e in SAMPLE_EVENTS if e["id"] == event_id), None)
    if not event:
        return jsonify({"error": "Evento no encontrado"}), 404
    return jsonify({"ok": True,
                    "message": f"Registrado en '{event['title']}' ✓"})

# ── Preview Markdown ───────────────────────────────────────────────────────────

@app.route("/api/preview-md", methods=["POST"])
def preview_md():
    text = (request.get_json() or {}).get("text", "")
    return jsonify({"html": render_md(text)})


# ── Formatear texto con Claude (server-side) ──────────────────────────────────

@app.route("/api/format-md", methods=["POST"])
def format_md():
    if not session.get("user"):
        return jsonify({"error": "Debes iniciar sesión"}), 401
    if not CLAUDE_API_KEY:
        return jsonify({"error": "Configura CLAUDE_API_KEY en las variables de entorno de Railway"}), 503

    text = (request.get_json() or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "Texto vacío"}), 400

    system_prompt = (
        "Eres un editor técnico experto. Tu tarea es convertir texto plano "
        "extraído de un PDF en Markdown bien estructurado para un blog tecnológico. "
        "Reglas: usa # y ## para encabezados, **negrita** para términos clave, "
        "listas con - cuando corresponda, bloques de código con ``` si hay código, "
        "y > para citas. Conserva todo el contenido original sin resumirlo. "
        "Devuelve SOLO el texto en Markdown, sin explicaciones adicionales."
    )

    try:
        resp = requests.post(
            CLAUDE_API_URL,
            headers={
                "Content-Type": "application/json",
                "x-api-key": CLAUDE_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [{"role": "user", "content": text}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()
        md_text = result["content"][0]["text"]
        return jsonify({"ok": True, "text": md_text})
    except requests.exceptions.HTTPError as e:
        try:
            msg = e.response.json().get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        return jsonify({"error": msg}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Extracción de PDF ──────────────────────────────────────────────────────────

@app.route("/api/extract-pdf", methods=["POST"])
def extract_pdf():
    if not session.get("user"):
        return jsonify({"error": "Debes iniciar sesión"}), 401

    import pdfplumber, io, tempfile, os as _os

    def _pdf_to_text(file_bytes: bytes) -> str:
        # Intento 1: pdfplumber (mejor calidad de extracción)
        try:
            text_parts = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text_parts.append(t.strip())
            if text_parts:
                return "\n\n".join(text_parts)
        except Exception:
            pass

        # Intento 2: pypdf (más tolerante con PDFs mal formados)
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes), strict=False)
            text_parts = []
            for page in reader.pages:
                t = page.extract_text()
                if t and t.strip():
                    text_parts.append(t.strip())
            if text_parts:
                return "\n\n".join(text_parts)
        except Exception:
            pass

        raise ValueError("No se pudo extraer texto del PDF. "
                         "Puede estar dañado, protegido con contraseña, "
                         "o contener solo imágenes escaneadas.")

    # ── Desde URL ────────────────────────────────────────────────────────────
    if request.is_json:
        url = (request.get_json() or {}).get("url", "").strip()
        if not url:
            return jsonify({"error": "URL vacía"}), 400
        try:
            # Headers que imitan un navegador real para evitar bloqueos 403
            browser_headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "application/pdf,application/octet-stream,*/*;q=0.9",
                "Accept-Language": "es-419,es;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Referer": url,
            }
            session_req = requests.Session()
            session_req.headers.update(browser_headers)
            resp = session_req.get(url, timeout=60, allow_redirects=True,
                                   stream=True)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "").lower()
            if "pdf" not in content_type and not url.lower().split("?")[0].endswith(".pdf"):
                return jsonify({"error":
                    f"La URL no devuelve un PDF (tipo: {content_type or 'desconocido'})"}), 400
            file_bytes = resp.content
            text = _pdf_to_text(file_bytes)
            if not text.strip():
                return jsonify({"error": "El PDF no contiene texto extraíble (puede ser escaneado/imagen)"}), 400
            return jsonify({"ok": True, "text": text,
                            "pages": len(text.split("\n\n"))})
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response is not None else "?"
            msgs = {
                403: "Acceso denegado (403) — el sitio bloquea descargas automáticas. Descarga el PDF manualmente y súbelo con 'Desde archivo'.",
                404: "Archivo no encontrado (404). Verifica la URL.",
                401: "El PDF requiere autenticación (401).",
                429: "Demasiadas solicitudes (429). Intenta en unos minutos.",
            }
            return jsonify({"error": msgs.get(code, f"Error HTTP {code}: {e}")}), 400
        except requests.exceptions.Timeout:
            return jsonify({"error": "Tiempo de espera agotado. El servidor tardó demasiado. Intenta con 'Desde archivo'."}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"No se pudo descargar: {e}"}), 400
        except Exception as e:
            return jsonify({"error": f"Error al leer PDF: {e}"}), 500

    # ── Desde archivo subido ─────────────────────────────────────────────────
    file = request.files.get("pdf")
    if not file:
        return jsonify({"error": "No se recibió archivo"}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Solo se aceptan archivos PDF"}), 400
    try:
        text = _pdf_to_text(file.read())
        return jsonify({"ok": True, "text": text})
    except Exception as e:
        return jsonify({"error": f"Error al leer PDF: {e}"}), 500

# ── Subir PDF directamente como artículo ──────────────────────────────────────

@app.route("/api/upload-pdf-article", methods=["POST"])
def upload_pdf_article():
    if not session.get("user"):
        return jsonify({"error": "Debes iniciar sesión"}), 401

    file = request.files.get("pdf")
    if not file or not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Se requiere un archivo PDF"}), 400

    pdf_bytes = file.read()
    if len(pdf_bytes) < 4:
        return jsonify({"error": "Archivo PDF inválido"}), 400

    title    = request.form.get("title", "").strip()
    excerpt  = request.form.get("excerpt", "").strip()
    category = request.form.get("category", "ia")
    tags_str = request.form.get("tags", "")
    art_id   = request.form.get("article_id", "").strip()

    if not title:
        return jsonify({"error": "El título es obligatorio"}), 400
    if not excerpt:
        return jsonify({"error": "El extracto es obligatorio"}), 400

    u      = session["user"]
    author = u.get("display") or u.get("name")
    init   = u.get("init", "")
    tags   = [t.strip() for t in tags_str.split(",") if t.strip()]

    if art_id:
        art = Article.query.get(int(art_id))
        if not art:
            return jsonify({"error": "Artículo no encontrado"}), 404
        if not is_admin() and art.author != u.get("name") and art.author != u.get("display"):
            return jsonify({"error": "Sin permiso"}), 403
        art.title    = title
        art.excerpt  = excerpt
        art.category = category
        art.is_pdf   = True
        art.pdf_data = pdf_bytes
        art.content  = ""
        art.tags     = tags
    else:
        art = Article(
            category  = category,
            featured  = False,
            title     = title,
            excerpt   = excerpt,
            content   = "",
            author    = author,
            init      = init,
            read_time = 5,
            is_pdf    = True,
            pdf_data  = pdf_bytes,
        )
        art.tags = tags
        db.session.add(art)

    db.session.commit()
    return jsonify({"ok": True, "id": art.id})


# ── Comentarios ────────────────────────────────────────────────────────────────

@app.route("/forums/<int:forum_id>/comment", methods=["POST"])
def add_comment(forum_id):
    if not session.get("user"):
        return jsonify({"error": "Debes iniciar sesión"}), 401
    forum = Forum.query.get(forum_id)
    if not forum:
        return jsonify({"error": "Foro no encontrado"}), 404

    text = (request.get_json() or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "El comentario no puede estar vacío"}), 400

    u = session["user"]
    comment = Comment(
        forum_id = forum_id,
        author   = u.get("display") or u["name"],
        init     = u["init"],
        text     = text,
        votes    = 0,
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({"ok": True, "comment": comment.to_dict()})


@app.route("/forums/<int:forum_id>/comment/<int:comment_id>/vote",
           methods=["POST"])
def vote_comment(forum_id, comment_id):
    if not session.get("user"):
        return jsonify({"error": "Debes iniciar sesión"}), 401
    comment = Comment.query.filter_by(id=comment_id,
                                      forum_id=forum_id).first()
    if not comment:
        return jsonify({"error": "Comentario no encontrado"}), 404
    comment.votes += 1
    db.session.commit()
    return jsonify({"ok": True, "votes": comment.votes})


@app.route("/forums/<int:forum_id>/comment/<int:comment_id>/delete",
           methods=["POST"])
def delete_comment(forum_id, comment_id):
    if not is_admin():
        return jsonify({"error": "Sin permiso"}), 403
    comment = Comment.query.filter_by(id=comment_id,
                                      forum_id=forum_id).first()
    if comment:
        db.session.delete(comment)
        db.session.commit()
    return jsonify({"ok": True})

# ── Editor de artículos (usuarios registrados) ────────────────────────────────

@app.route("/articles/new", methods=["GET", "POST"])
def user_new_article():
    if not session.get("user"):
        return redirect(url_for("articles"))
    if is_admin():
        return redirect(url_for("admin_new_article"))
    if request.method == "POST":
        data    = request.get_json() or {}
        article = _build_article_from_data(data, session["user"])
        db.session.add(article)
        db.session.commit()
        return jsonify({"ok": True, "id": article.id})
    return render_template("article_editor.html",
                           article=None, categories=CATEGORIES)


@app.route("/articles/<int:article_id>/edit", methods=["GET", "POST"])
def user_edit_article(article_id):
    if not session.get("user"):
        return redirect(url_for("articles"))
    art = Article.query.get(article_id)
    if not art:
        return redirect(url_for("articles"))
    # Solo puede editar el propio autor (por nombre) o el admin
    u = session["user"]
    if not is_admin() and art.author != u.get("name") and art.author != u.get("display"):
        abort(403)
    if request.method == "POST":
        data = request.get_json() or {}
        _update_article_from_data(art, data)
        db.session.commit()
        return jsonify({"ok": True, "id": article_id})
    return render_template("article_editor.html",
                           article=art, categories=CATEGORIES)


# ── Editor de artículos (admin) ────────────────────────────────────────────────

@app.route("/admin/articles/new", methods=["GET", "POST"])
def admin_new_article():
    if not is_admin():
        abort(403)
    if request.method == "POST":
        data    = request.get_json() or {}
        article = _build_article_from_data(data)
        db.session.add(article)
        db.session.commit()
        return jsonify({"ok": True, "id": article.id})
    return render_template("admin_editor.html",
                           article=None, categories=CATEGORIES)


@app.route("/admin/articles/<int:article_id>/edit", methods=["GET", "POST"])
def admin_edit_article(article_id):
    if not is_admin():
        abort(403)
    art = Article.query.get(article_id)
    if not art:
        return redirect(url_for("admin_panel"))
    if request.method == "POST":
        data = request.get_json() or {}
        _update_article_from_data(art, data)
        db.session.commit()
        return jsonify({"ok": True, "id": article_id})
    return render_template("admin_editor.html",
                           article=art, categories=CATEGORIES)


def _build_article_from_data(data, current_user=None) -> Article:
    title    = (data.get("title")   or "").strip()
    excerpt  = (data.get("excerpt") or "").strip()
    content  = (data.get("content") or "").strip()
    category = data.get("category", "ia")
    # Admin puede poner cualquier autor; usuarios usan su propio nombre
    default_author = (current_user.get("display") or current_user.get("name")) \
                     if current_user else "Administrador"
    author   = (data.get("author")  or default_author).strip() or default_author
    featured = bool(data.get("featured"))
    tags     = [t.strip() for t in (data.get("tags") or "").split(",") if t.strip()]
    init     = (current_user.get("init") if current_user
                else "".join(w[0].upper() for w in author.split()[:2]))
    read_t   = max(1, len(content.split()) // 200)
    art = Article(
        category  = category,
        featured  = featured,
        title     = title,
        excerpt   = excerpt,
        content   = content,
        author    = author,
        init      = init,
        read_time = read_t,
    )
    art.tags = tags
    return art


def _update_article_from_data(art: Article, data) -> None:
    art.title    = (data.get("title")   or "").strip()
    art.excerpt  = (data.get("excerpt") or "").strip()
    art.content  = (data.get("content") or "").strip()
    art.category = data.get("category", art.category)
    art.featured = bool(data.get("featured"))
    author       = (data.get("author")  or art.author).strip() or art.author
    art.author   = author
    art.init     = "".join(w[0].upper() for w in author.split()[:2])
    art.read_time = max(1, len(art.content.split()) // 200)
    art.tags     = [t.strip() for t in
                    (data.get("tags") or "").split(",") if t.strip()]

# ── Admin panel ────────────────────────────────────────────────────────────────

@app.route("/admin")
def admin_panel():
    if not is_admin():
        abort(403)

    arts   = Article.query.order_by(Article.created_at.desc()).all()
    fors   = Forum.query.order_by(Forum.created_at.desc()).all()
    users  = User.query.order_by(User.created_at).all()

    # Enrich user records for the template
    member_rows = []
    for u in users:
        art_count = Article.query.filter(
            Article.author.ilike(f"%{u.first_name}%")
        ).count()
        member_rows.append({
            "id":       u.id,
            "name":     u.name,
            "init":     u.init,
            "color":    user_color(u.id),
            "role":     "Administrador" if u.is_admin else "Miembro",
            "articles": art_count,
            "badge":    "Admin" if u.is_admin else "Member",
        })

    return render_template("admin.html",
                           articles=arts,
                           forums=fors,
                           members=member_rows)


@app.route("/admin/delete/article/<int:article_id>", methods=["POST"])
def admin_delete_article(article_id):
    if not is_admin():
        abort(403)
    art = Article.query.get(article_id)
    if art:
        db.session.delete(art)
        db.session.commit()
    return jsonify({"ok": True})


@app.route("/admin/delete/forum/<int:forum_id>", methods=["POST"])
def admin_delete_forum(forum_id):
    if not is_admin():
        abort(403)
    forum = Forum.query.get(forum_id)
    if forum:
        db.session.delete(forum)
        db.session.commit()
    return jsonify({"ok": True})


@app.route("/admin/delete/member/<int:member_id>", methods=["POST"])
def admin_delete_member(member_id):
    if not is_admin():
        abort(403)
    u = User.query.get(member_id)
    if u and u.email != ADMIN_EMAIL:   # never delete the admin itself
        db.session.delete(u)
        db.session.commit()
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
