/* ═══════════════════════════════════════════
   ZConnect — Main UI utilities
   ═══════════════════════════════════════════ */

// ── Toast notifications ───────────────────────────────────────────────────────
function showToast(msg, type = 'info', duration = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = { success: '✅', error: '❌', warn: '⚠️', info: 'ℹ️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || icons.info}</span><span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(100%)'; toast.style.transition = '.3s'; setTimeout(() => toast.remove(), 300); }, duration);
}

// ── Modal helpers ─────────────────────────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.add('open'); el.querySelector('.modal')?.focus(); }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.classList.remove('open');
  }
  if (e.target.classList.contains('modal-close')) {
    e.target.closest('.modal-backdrop')?.classList.remove('open');
  }
});

// Close modal on Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-backdrop.open').forEach(m => m.classList.remove('open'));
  }
});

// ── CSRF helper ───────────────────────────────────────────────────────────────
function getCsrf() {
  return document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';
}

async function postJSON(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCsrf() },
    body: new URLSearchParams(data),
  });
  return res.json();
}

// ── Create project form ───────────────────────────────────────────────────────
const createProjectForm = document.getElementById('create-project-form');
if (createProjectForm) {
  createProjectForm.addEventListener('submit', async e => {
    e.preventDefault();
    const fd = new FormData(createProjectForm);
    const res = await postJSON('/project/create/', Object.fromEntries(fd));
    if (res.success) {
      showToast('Project created!', 'success');
      setTimeout(() => window.location.href = res.redirect, 500);
    } else {
      showToast(res.error || 'Failed to create project', 'error');
    }
  });
}

// ── Add channel ───────────────────────────────────────────────────────────────
const addChannelForm = document.getElementById('add-channel-form');
if (addChannelForm) {
  addChannelForm.addEventListener('submit', async e => {
    e.preventDefault();
    const fd = new FormData(addChannelForm);
    const projectId = addChannelForm.dataset.projectId;
    const res = await postJSON(`/project/${projectId}/channel/add/`, Object.fromEntries(fd));
    if (res.success) {
      showToast('Channel added!', 'success');
      closeModal('add-channel-modal');
      location.reload();
    } else {
      showToast(res.error || 'Failed', 'error');
    }
  });
}

// ── Invite member ─────────────────────────────────────────────────────────────
const inviteForm = document.getElementById('invite-form');
if (inviteForm) {
  const searchInput = inviteForm.querySelector('#invite-search');
  const results = document.getElementById('invite-results');
  let searchTimeout;

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      const q = searchInput.value.trim();
      if (q.length < 2) { results.innerHTML = ''; return; }
      searchTimeout = setTimeout(async () => {
        const r = await fetch(`/api/users/search/?q=${encodeURIComponent(q)}`).then(r => r.json());
        results.innerHTML = r.users.map(u => `
          <div class="invite-result-item" data-username="${u.username}" style="padding:8px;cursor:pointer;border-radius:6px;display:flex;align-items:center;gap:8px;transition:background .1s">
            <div class="avatar avatar-32" style="background:var(--accent)">${(u.display_name||u.username)[0].toUpperCase()}</div>
            <div>
              <div style="font-size:13px;font-weight:600">${u.display_name || u.username}</div>
              <div style="font-size:11px;color:var(--text-3)">@${u.username}</div>
            </div>
          </div>
        `).join('');
        results.querySelectorAll('.invite-result-item').forEach(item => {
          item.addEventListener('mouseenter', () => item.style.background = 'var(--bg-hover)');
          item.addEventListener('mouseleave', () => item.style.background = '');
          item.addEventListener('click', () => {
            searchInput.value = item.dataset.username;
            results.innerHTML = '';
          });
        });
      }, 250);
    });
  }

  inviteForm.addEventListener('submit', async e => {
    e.preventDefault();
    const projectId = inviteForm.dataset.projectId;
    const username = inviteForm.querySelector('[name="username"]').value.trim();
    if (!username) return;
    const res = await postJSON(`/project/${projectId}/invite/`, { username });
    if (res.success) {
      showToast(res.message || 'Member added!', 'success');
      closeModal('invite-modal');
      location.reload();
    } else {
      showToast(res.error || 'Failed', 'error');
    }
  });
}

// ── Status update ─────────────────────────────────────────────────────────────
document.querySelectorAll('[data-set-status]').forEach(btn => {
  btn.addEventListener('click', async () => {
    const status = btn.dataset.setStatus;
    const res = await postJSON('/status/update/', { status });
    if (res.success) {
      showToast(`Status: ${status}`, 'success');
      document.querySelectorAll('.my-status-dot').forEach(d => {
        d.style.background = res.color;
      });
    }
  });
});

// ── Copy invite link ──────────────────────────────────────────────────────────
document.querySelectorAll('[data-copy]').forEach(btn => {
  btn.addEventListener('click', () => {
    navigator.clipboard.writeText(btn.dataset.copy).then(() => showToast('Copied to clipboard!', 'success'));
  });
});

// ── Delete project ────────────────────────────────────────────────────────────
const delProjectBtn = document.getElementById('delete-project-btn');
if (delProjectBtn) {
  delProjectBtn.addEventListener('click', async () => {
    if (!confirm('Delete this project? This cannot be undone.')) return;
    const projectId = delProjectBtn.dataset.projectId;
    const res = await postJSON(`/project/${projectId}/delete/`, {});
    if (res.success) {
      showToast('Project deleted', 'warn');
      setTimeout(() => window.location.href = res.redirect || '/dashboard/', 600);
    }
  });
}

// ── File size formatter ───────────────────────────────────────────────────────
function formatBytes(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b / 1024).toFixed(0) + ' KB';
  return (b / 1048576).toFixed(1) + ' MB';
}
