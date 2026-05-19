// ── IDEA Blog — main.js ──────────────────────────────────────────────────────

// ── Modals ──────────────────────────────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'flex';
}

// Show welcome modal with optional context hint (e.g. "para comentar en foros")
function requireAuth(hint) {
  const hintBox  = document.getElementById('welcomeHint');
  const hintText = document.getElementById('welcomeHintText');
  if (hintBox && hintText) {
    if (hint) {
      hintText.textContent = '👉 Necesitas una cuenta ' + hint + '.';
      hintBox.style.display = 'block';
    } else {
      hintBox.style.display = 'none';
    }
  }
  openModal('welcomeModal');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'none';
}

document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.style.display = 'none';
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay').forEach(m => m.style.display = 'none');
  }
});

// ── Toast ────────────────────────────────────────────────────────────────────
function showToast(msg, duration = 3000) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove('show'), duration);
}

// ── Auth ─────────────────────────────────────────────────────────────────────
async function doLogout() {
  await fetch('/logout', { method: 'POST' });
  showToast('Sesión cerrada');
  setTimeout(() => location.reload(), 600);
}

// ── Search ────────────────────────────────────────────────────────────────────
function doSearch(value) {
  const q = (value || '').trim();
  if (!q) return;
  window.location.href = `/articles?q=${encodeURIComponent(q)}`;
}

// ── Panel join ────────────────────────────────────────────────────────────────
async function joinPanel(panelId, btn) {
  try {
    const r = await fetch('/api/join-panel', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ panel_id: panelId }),
    });
    const data = await r.json();
    if (data.ok) {
      showToast(data.message);
      btn.textContent = '✓ Unido';
      btn.disabled = true;
      btn.classList.remove('btn-primary');
      btn.classList.add('btn-ghost');
    } else {
      showToast(data.error || 'Error al unirse');
    }
  } catch {
    showToast('Error de conexión');
  }
}

// ── Event register ────────────────────────────────────────────────────────────
async function registerEvent(eventId, btn) {
  try {
    const r = await fetch('/api/register-event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event_id: eventId }),
    });
    const data = await r.json();
    if (data.ok) {
      showToast(data.message);
      btn.textContent = '✓ Registrado';
      btn.disabled = true;
      btn.classList.remove('btn-primary');
      btn.classList.add('btn-ghost');
    } else {
      showToast(data.error || 'Error al registrarse');
    }
  } catch {
    showToast('Error de conexión');
  }
}

// ── Auth form submit helpers ──────────────────────────────────────────────────
function submitLogin() {
  const email = document.getElementById('loginEmail').value.trim();
  const pwd   = document.getElementById('loginPwd').value;
  doLogin({ email, password: pwd });
}

async function doLogin({ email, password }) {
  const errEl = document.getElementById('loginError');
  if (errEl) errEl.textContent = '';
  try {
    const r = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await r.json();
    if (!r.ok) { if (errEl) errEl.textContent = data.error || 'Error al iniciar sesión'; return; }
    showToast(`Bienvenido, ${data.user.display || data.user.name} ✓`);
    setTimeout(() => location.reload(), 800);
  } catch { if (errEl) errEl.textContent = 'Error de conexión'; }
}

function submitRegister() {
  const first = document.getElementById('regFirst').value.trim();
  const last  = document.getElementById('regLast').value.trim();
  const alias = (document.getElementById('regAlias')?.value || '').trim();
  const email = document.getElementById('regEmail').value.trim();
  const pwd   = document.getElementById('regPwd').value;
  doRegister({ first, last, alias, email, password: pwd });
}

async function doRegister({ first, last, alias, email, password }) {
  const errEl = document.getElementById('registerError');
  if (errEl) errEl.textContent = '';
  try {
    const r = await fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ first, last, alias, email, password }),
    });
    const data = await r.json();
    if (!r.ok) { if (errEl) errEl.textContent = data.error || 'Error al registrarse'; return; }
    showToast(`¡Bienvenido, ${data.user.display || data.user.name}! ✓`);
    setTimeout(() => location.reload(), 800);
  } catch { if (errEl) errEl.textContent = 'Error de conexión'; }
}

// ── Auto-show welcome modal en primera visita (sin sesión) ────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const isLoggedIn   = document.body.dataset.loggedIn === 'true';
  const alreadySeen  = localStorage.getItem('idea_welcome_seen');
  if (!isLoggedIn && !alreadySeen) {
    setTimeout(() => openModal('welcomeModal'), 600);
    localStorage.setItem('idea_welcome_seen', '1');
  }
});
