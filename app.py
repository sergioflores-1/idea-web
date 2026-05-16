import json, os, requests
from flask import (Flask, render_template, request, session,
                   jsonify, Response, redirect, url_for)
import markdown as md

from data.data import (SAMPLE_ARTICLES, SAMPLE_FORUMS, SAMPLE_MEMBERS,
                       SAMPLE_PANELS, SAMPLE_EVENTS, CATEGORIES,
                       AI_MODULES, AI_PROMPTS, CONDUCT_RULES, TRENDING_TAGS,
                       CLAUDE_API_URL, CLAUDE_MODEL)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "idea-blog-dev-secret-2025")


def get_cat(cat_id):
    return next((c for c in CATEGORIES if c["id"] == cat_id),
                {"label": cat_id, "emoji": "📄", "color": "#666", "bg": "#eee"})


def render_md(text):
    return md.markdown(text or "", extensions=["fenced_code", "tables", "nl2br"])


@app.context_processor
def inject_globals():
    return dict(
        user=session.get("user"),
        categories=CATEGORIES,
        trending_tags=TRENDING_TAGS,
        conduct_rules=CONDUCT_RULES,
        get_cat=get_cat,
    )


# ── Pages ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    featured = next((a for a in SAMPLE_ARTICLES if a["featured"]), SAMPLE_ARTICLES[0])
    return render_template("index.html",
                           articles=SAMPLE_ARTICLES,
                           forums=SAMPLE_FORUMS[:3],
                           featured=featured)


@app.route("/articles")
def articles():
    cat = request.args.get("cat", "all")
    q   = request.args.get("q", "").strip()
    arts = SAMPLE_ARTICLES
    if cat != "all":
        arts = [a for a in arts if a["category"] == cat]
    if q:
        arts = [a for a in arts
                if q.lower() in a["title"].lower() or q.lower() in a["excerpt"].lower()]
    return render_template("articles.html", articles=arts, cat=cat, q=q)


@app.route("/articles/<int:article_id>")
def article_detail(article_id):
    art = next((a for a in SAMPLE_ARTICLES if a["id"] == article_id), None)
    if not art:
        return redirect(url_for("articles"))
    return render_template("article_detail.html",
                           article=art,
                           content_html=render_md(art["content"]))


@app.route("/articles/<int:article_id>/download")
def download_article(article_id):
    if not session.get("user"):
        return redirect(url_for("article_detail", article_id=article_id))
    art = next((a for a in SAMPLE_ARTICLES if a["id"] == article_id), None)
    if not art:
        return redirect(url_for("articles"))
    html = render_template("article_download.html",
                           article=art,
                           content_html=render_md(art["content"]),
                           get_cat=get_cat)
    filename = f"idea-{art['title'][:40].lower().replace(' ', '-')}.html"
    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )


@app.route("/forums")
def forums():
    sort = request.args.get("sort", "recent")
    fs = list(SAMPLE_FORUMS)
    if sort == "votes":
        fs.sort(key=lambda x: x["votes"], reverse=True)
    elif sort == "solved":
        fs = [f for f in fs if f["solved"]]
    return render_template("forums.html", forums=fs, sort=sort)


@app.route("/forums/<int:forum_id>")
def forum_detail(forum_id):
    forum = next((f for f in SAMPLE_FORUMS if f["id"] == forum_id), None)
    if not forum:
        return redirect(url_for("forums"))
    return render_template("forum_detail.html", forum=forum)


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
    data = request.get_json()
    email = (data.get("email") or "").strip()
    pwd   = data.get("password") or ""
    if not email or not pwd:
        return jsonify({"error": "Completa todos los campos"}), 400
    name = email.split("@")[0].replace(".", " ").title()
    init = "".join(w[0].upper() for w in name.split()[:2])
    session["user"] = {"name": name, "email": email, "init": init}
    return jsonify({"ok": True, "user": session["user"]})


@app.route("/register", methods=["POST"])
def register():
    data  = request.get_json()
    first = (data.get("first") or "").strip()
    last  = (data.get("last")  or "").strip()
    email = (data.get("email") or "").strip()
    pwd   = data.get("password") or ""
    if not first or not email or not pwd:
        return jsonify({"error": "Completa los campos obligatorios"}), 400
    name = f"{first} {last}".strip()
    init = (first[0] + (last[0] if last else (first[1] if len(first) > 1 else "X"))).upper()
    session["user"] = {"name": name, "email": email, "init": init}
    return jsonify({"ok": True, "user": session["user"]})


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"ok": True})


# ── Claude SSE proxy ───────────────────────────────────────────────────────────

@app.route("/api/claude", methods=["POST"])
def claude_proxy():
    data     = request.get_json()
    api_key  = (data.get("api_key") or "").strip()
    messages = data.get("messages", [])
    system   = data.get("system", "")

    if not api_key or not api_key.startswith("sk-"):
        return jsonify({"error": "API key inválida o faltante"}), 400

    def generate():
        payload = {
            "model": CLAUDE_MODEL,
            "max_tokens": 2000,
            "stream": True,
            "messages": messages,
        }
        if system:
            payload["system"] = system

        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
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
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


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
    return jsonify({"ok": True, "message": f"Registrado en '{event['title']}' ✓"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
