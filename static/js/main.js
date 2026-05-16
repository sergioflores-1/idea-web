// ── IDEA Blog — main.js ──────────────────────────────────────────────────────

// ── Modals ──────────────────────────────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'flex';
}

// Show register modal with optional context hint (e.g. "para comentar en foros")
function requireAuth(hint) {
  const sub = document.querySelector('#registerModal .sub');
  if (sub) {
    sub.textContent = hint
      ? `Crea tu cuenta gratuita ${hint}.`
      : 'Únete a la comunidad IDEA para participar.';
  }
  openModal('registerModal');
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
async function doLogin(e) {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value.trim();
  const pwd   = document.getElementById('loginPwd').value;
  const errEl = document.getElementById('loginError');
  errEl.textContent = '';

  try {
    const r = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password: pwd }),
    });
    const data = await r.json();
    if (!r.ok) { errEl.textContent = data.error || 'Error al iniciar sesión'; return; }
    showToast(`Bienvenido, ${data.user.name} ✓`);
    setTimeout(() => location.reload(), 800);
  } catch {
    errEl.textContent = 'Error de conexión';
  }
}

async function doRegister(e) {
  e.preventDefault();
  const first = document.getElementById('regFirst').value.trim();
  const last  = document.getElementById('regLast').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const pwd   = document.getElementById('regPwd').value;
  const errEl = document.getElementById('registerError');
  errEl.textContent = '';

  try {
    const r = await fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ first, last, email, password: pwd }),
    });
    const data = await r.json();
    if (!r.ok) { errEl.textContent = data.error || 'Error al registrarse'; return; }
    showToast(`Cuenta creada, bienvenido ${data.user.name} ✓`);
    setTimeout(() => location.reload(), 800);
  } catch {
    errEl.textContent = 'Error de conexión';
  }
}

async function doLogout() {
  await fetch('/logout', { method: 'POST' });
  showToast('Sesión cerrada');
  setTimeout(() => location.reload(), 600);
}

// ── Search ────────────────────────────────────────────────────────────────────
function doSearch(e) {
  if (e.key !== 'Enter') return;
  const q = e.target.value.trim();
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

// ── Wire up forms on DOMContentLoaded ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const loginForm    = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  if (loginForm)    loginForm.addEventListener('submit', doLogin);
  if (registerForm) registerForm.addEventListener('submit', doRegister);
});
