function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('open');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('open');
}

document.addEventListener('click', function(e) {
  if (e.target.classList.contains('modal-close')) {
    const modal = e.target.closest('.modal-backdrop');
    if (modal) modal.classList.remove('open');
  }
  if (e.target.classList.contains('modal-backdrop') && e.target.classList.contains('open')) {
    e.target.classList.remove('open');
  }
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie) {
    document.cookie.split(';').forEach(function(c) {
      c = c.trim();
      if (c.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(c.substring(name.length + 1));
      }
    });
  }
  return cookieValue;
}

console.log('✅ Main.js ready');
