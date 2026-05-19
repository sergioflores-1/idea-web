# IDEA Blog — Contexto del proyecto

## Qué es este proyecto
Aplicación web Flask del blog **IDEA** (comunidad tecnológica latinoamericana).
Conversión de una app de escritorio Python/Tkinter al stack web para deploy en Railway.

## Stack técnico
- **Backend**: Python 3 + Flask + Jinja2
- **Frontend**: HTML/CSS vanilla + JavaScript (sin frameworks)
- **IA**: Claude API via SSE streaming (proxy en `/api/claude`)
- **Deploy**: Railway (nixpacks) con gunicorn
- **Repo GitHub**: `sergioflores-1/idea-blog`

## Estructura de archivos
```
idea-web/
├── app.py                  # Flask app principal — todas las rutas
├── data/data.py            # Datos de muestra (artículos, foros, miembros, etc.)
├── templates/
│   ├── base.html           # Layout: sidebar + topbar + 4 modales
│   ├── index.html          # Home: hero + artículos + foros activos
│   ├── articles.html       # Lista filtrable de artículos
│   ├── article_detail.html # Detalle + botón descarga
│   ├── article_download.html # Template HTML standalone para descarga
│   ├── forums.html         # Lista foros con tabs (recientes/votos/resueltos)
│   ├── forum_detail.html   # Hilo de foro con respuestas
│   ├── panels.html         # Grid de paneles temáticos
│   ├── events.html         # Lista de eventos con registro
│   ├── members.html        # Grid de miembros destacados
│   └── ai_hub.html         # Chat con Claude (SSE streaming)
├── static/
│   ├── css/style.css       # Tema dark-purple completo
│   └── js/main.js          # Modales, auth, toast, joinPanel, registerEvent
├── requirements.txt        # flask, gunicorn, requests, markdown, python-dotenv
├── Procfile                # gunicorn app:app --bind 0.0.0.0:$PORT
└── railway.toml            # nixpacks + healthcheck
```

## Rutas Flask
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Home |
| GET | `/articles` | Lista artículos (filtro ?cat=, ?q=) |
| GET | `/articles/<id>` | Detalle artículo |
| GET | `/articles/<id>/download` | Descarga HTML (requiere sesión) |
| GET | `/forums` | Lista foros (sort=recent/votes/solved) |
| GET | `/forums/<id>` | Hilo de foro |
| GET | `/panels` | Paneles temáticos |
| GET | `/events` | Eventos |
| GET | `/members` | Miembros |
| GET | `/ai` | Hub de IA con Claude |
| POST | `/login` | Auth (JSON) |
| POST | `/register` | Registro (JSON) |
| POST | `/logout` | Cerrar sesión |
| POST | `/api/claude` | Proxy SSE a Claude API |
| POST | `/api/join-panel` | Unirse a panel |
| POST | `/api/register-event` | Registrarse en evento |

## Reglas de negocio implementadas
- **Lectura libre**: cualquier visitante puede leer artículos, foros, paneles, eventos, miembros
- **Interacción requiere cuenta**: al intentar interactuar (unirse a panel, registrarse en evento, responder foro, descargar artículo) → aparece modal de **registro** (no login) con mensaje contextual
- **Usuarios con sesión**: ven botones de acción directamente
- **Descarga de artículos**: solo usuarios registrados, genera HTML standalone con estilos
- **IA / Claude**: cualquier visitante puede acceder, pero necesita su propia API key (se guarda en localStorage)

## Patrones de código importantes

### requireAuth en JS (main.js)
```javascript
function requireAuth(hint) {
  const sub = document.querySelector('#registerModal .sub');
  if (sub) sub.textContent = hint
    ? `Crea tu cuenta gratuita ${hint}.`
    : 'Únete a la comunidad IDEA para participar.';
  openModal('registerModal');
}
// Uso: onclick="requireAuth('para unirte a paneles')"
```

### Context processor (app.py)
Inyecta automáticamente en todos los templates:
- `user` — sesión actual
- `categories` — lista de 6 categorías
- `trending_tags` — 10 tags
- `conduct_rules` — 6 reglas de conducta
- `get_cat` — función para obtener datos de categoría por id

### SSE streaming Claude (app.py `/api/claude`)
El cliente manda `{api_key, messages, system}` → Flask hace proxy a la API de Anthropic
y reenvía chunks como `data: {"text": "..."}` → JS lee con `ReadableStream`.

## Variables de entorno (Railway)
```
SECRET_KEY=valor-secreto-largo
PORT=     # Railway lo inyecta automáticamente
```

## Para correr localmente
```bash
cd "G:\Gper\My Drive\Claude\idea-web"
pip install flask markdown requests python-dotenv
python app.py
# → http://localhost:5000
```

## Diseño visual
- Fondo sidebar/topbar: `#12102a` (dark navy)
- Acento principal: `#e94560` (rojo-rosa)
- Acento secundario: `#533483` (púrpura)
- Dorado: `#f5a623`
- Fondo página: `#f6f7fb`
- Tarjetas: `#ffffff` con borde `#e2e2ea`

## Estado del proyecto
- ✅ App completa y funcional (todas las rutas devuelven 200)
- ✅ Deploy en Railway configurado (repo: sergioflores-1/idea-blog)
- ✅ Descarga de artículos para usuarios registrados
- ✅ Flujo registro-primero para nuevos usuarios
- 🔲 Base de datos real (actualmente usa datos de muestra en memoria)
- 🔲 Sistema de comentarios real
- 🔲 Upload de imágenes para artículos
