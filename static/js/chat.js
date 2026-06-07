/* ═══════════════════════════════════════════
   ZConnect — Real-time Chat (WebSocket)
   ═══════════════════════════════════════════ */

class ZChat {
  constructor(roomType, roomId, currentUserId) {
    this.roomType = roomType;
    this.roomId = roomId;
    this.myId = parseInt(currentUserId);
    this.ws = null;
    this.reconnectDelay = 1000;
    this.typingTimer = null;
    this.isTyping = false;
    this.lastSenderId = null;
    this.lastDate = null;

    this.msgList = document.getElementById('messages-list');
    this.chatInput = document.getElementById('chat-input');
    this.sendBtn = document.getElementById('send-btn');
    this.typingEl = document.getElementById('typing-indicator');
    this.fileInput = document.getElementById('file-input');

    this.bindEvents();
    this.connect();
    this.scrollToBottom();
  }

  connect() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${proto}://${location.host}/ws/chat/${this.roomType}/${this.roomId}/`;
    this.ws = new WebSocket(url);
    this.ws.onopen = () => { console.log('Chat WS connected'); this.reconnectDelay = 1000; };
    this.ws.onmessage = e => this.onMessage(JSON.parse(e.data));
    this.ws.onclose = () => {
      console.log('Chat WS closed, reconnecting...');
      setTimeout(() => this.connect(), this.reconnectDelay);
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 10000);
    };
    this.ws.onerror = err => console.error('WS error', err);
  }

  onMessage(data) {
    if (data.type === 'message') {
      this.renderMessage(data.data, true);
      this.scrollToBottom(true);
    } else if (data.type === 'typing') {
      this.showTyping(data.user_name, data.is_typing);
    } else if (data.type === 'deleted') {
      const el = document.querySelector(`[data-msg-id="${data.msg_id}"]`);
      if (el) el.querySelector('.msg-text').innerHTML = '<em style="color:var(--text-3)">[Message deleted]</em>';
    }
  }

  send() {
    const content = this.chatInput.value.trim();
    if (!content || !this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({ type: 'message', content }));
    this.chatInput.value = '';
    this.chatInput.style.height = 'auto';
    this.stopTyping();
  }

  sendTyping(isTyping) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'typing', is_typing: isTyping }));
    }
  }

  stopTyping() {
    if (this.isTyping) {
      this.isTyping = false;
      this.sendTyping(false);
    }
    clearTimeout(this.typingTimer);
  }

  showTyping(userName, isTyping) {
    if (!this.typingEl) return;
    if (isTyping) {
      this.typingEl.textContent = `${userName} is typing...`;
    } else {
      this.typingEl.textContent = '';
    }
  }

  renderMessage(msg, isNew = false) {
    const isMine = msg.sender_id === this.myId;
    const isConsecutive = msg.sender_id === this.lastSenderId;
    const isNewDate = msg.date !== this.lastDate;

    if (isNewDate) {
      const div = document.createElement('div');
      div.className = 'day-divider';
      div.innerHTML = `<span>${this.formatDate(msg.date)}</span>`;
      this.msgList.appendChild(div);
      this.lastDate = msg.date;
    }

    const row = document.createElement('div');
    row.className = `message-row${isConsecutive && !isNewDate ? ' consecutive' : ''}`;
    row.setAttribute('data-msg-id', msg.id);
    row.setAttribute('data-sender-id', msg.sender_id);

    const avatarHtml = isConsecutive && !isNewDate
      ? `<div class="msg-avatar-spacer"></div>`
      : `<div class="avatar avatar-36 msg-avatar" style="background:var(--accent)">
           ${msg.sender_avatar && !msg.sender_avatar.includes('default') ? `<img src="${msg.sender_avatar}" alt="">` : msg.sender_initials || msg.sender_name[0]}
         </div>`;

    const metaHtml = isConsecutive && !isNewDate ? '' : `
      <div class="msg-meta">
        <span class="msg-name">${this.esc(msg.sender_name)}${isMine ? ' <span style="color:var(--text-3);font-size:11px">(you)</span>' : ''}</span>
        <span class="msg-time">${msg.timestamp}</span>
      </div>`;

    let contentHtml = '';
    if (msg.is_deleted) {
      contentHtml = '<div class="msg-text deleted"><em>[Message deleted]</em></div>';
    } else if (msg.file) {
      contentHtml = this.renderFile(msg.file);
    } else {
      contentHtml = `<div class="msg-text">${this.linkify(this.esc(msg.content))}</div>`;
    }

    row.innerHTML = `
      ${avatarHtml}
      <div class="msg-body">
        ${metaHtml}
        ${contentHtml}
      </div>
      ${isMine ? `<div class="msg-actions" style="display:none;gap:4px">
        <button class="btn btn-ghost btn-sm delete-msg" data-msg-id="${msg.id}" title="Delete">🗑️</button>
      </div>` : ''}
    `;

    row.addEventListener('mouseenter', () => { const a = row.querySelector('.msg-actions'); if (a) a.style.display = 'flex'; });
    row.addEventListener('mouseleave', () => { const a = row.querySelector('.msg-actions'); if (a) a.style.display = 'none'; });

    const delBtn = row.querySelector('.delete-msg');
    if (delBtn) {
      delBtn.addEventListener('click', () => {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({ type: 'delete', msg_id: parseInt(delBtn.dataset.msgId) }));
        }
      });
    }

    this.msgList.appendChild(row);
    this.lastSenderId = msg.sender_id;
    if (!isNewDate) { /* keep last date */ }
  }

  renderFile(file) {
    if (file.is_image) {
      return `<div class="msg-file"><img src="${file.url}" alt="${this.esc(file.name)}" loading="lazy" onclick="window.open('${file.url}','_blank')"></div>`;
    }
    const icons = { 'application/pdf': '📄', 'application/zip': '🗜️', 'text/': '📝', 'video/': '🎥', 'audio/': '🎵' };
    let icon = '📎';
    for (const [k, v] of Object.entries(icons)) { if (file.type.startsWith(k)) { icon = v; break; } }
    return `<div class="msg-file">
      <div class="msg-file-info">
        <div class="msg-file-icon">${icon}</div>
        <div class="msg-file-meta">
          <div class="msg-file-name">${this.esc(file.name)}</div>
          <div class="msg-file-size">${file.size}</div>
        </div>
        <a href="${file.url}" download="${this.esc(file.name)}" class="msg-file-dl">⬇ Download</a>
      </div>
    </div>`;
  }

  scrollToBottom(smooth = false) {
    const area = document.getElementById('chat-area');
    if (area) area.scrollTo({ top: area.scrollHeight, behavior: smooth ? 'smooth' : 'instant' });
  }

  esc(s) {
    if (!s) return '';
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  linkify(text) {
    return text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
  }

  formatDate(dateStr) {
    const d = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today); yesterday.setDate(today.getDate() - 1);
    if (d.toDateString() === today.toDateString()) return 'Today';
    if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
    return d.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });
  }

  async uploadFile(file) {
    if (file.size > 52428800) { showToast('File too large (max 50MB)', 'error'); return; }
    const fd = new FormData();
    fd.append('file', file);
    fd.append('csrfmiddlewaretoken', getCsrf());
    showToast(`Uploading ${file.name}...`, 'info', 2000);
    try {
      const res = await fetch(`/upload/${this.roomType}/${this.roomId}/`, { method: 'POST', body: fd }).then(r => r.json());
      if (res.success) {
        // Broadcast the file message via WS (server already saved it, just re-render)
        this.renderMessage(res.data, true);
        this.scrollToBottom(true);
      } else {
        showToast(res.error || 'Upload failed', 'error');
      }
    } catch (err) {
      showToast('Upload error', 'error');
    }
  }

  bindEvents() {
    // Send on Enter (Shift+Enter = newline)
    this.chatInput?.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.send(); }
    });

    // Auto-resize textarea
    this.chatInput?.addEventListener('input', () => {
      this.chatInput.style.height = 'auto';
      this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 150) + 'px';
      // Typing indicator
      if (!this.isTyping) { this.isTyping = true; this.sendTyping(true); }
      clearTimeout(this.typingTimer);
      this.typingTimer = setTimeout(() => this.stopTyping(), 2000);
    });

    this.sendBtn?.addEventListener('click', () => this.send());

    // File upload via toolbar
    this.fileInput?.addEventListener('change', () => {
      const file = this.fileInput.files[0];
      if (file) { this.uploadFile(file); this.fileInput.value = ''; }
    });

    // Drag-and-drop file upload
    const chatArea = document.getElementById('chat-area');
    chatArea?.addEventListener('dragover', e => { e.preventDefault(); chatArea.style.background = 'rgba(124,92,191,.08)'; });
    chatArea?.addEventListener('dragleave', () => { chatArea.style.background = ''; });
    chatArea?.addEventListener('drop', e => {
      e.preventDefault(); chatArea.style.background = '';
      const file = e.dataTransfer.files[0];
      if (file) this.uploadFile(file);
    });

    // Load more on scroll up
    chatArea?.addEventListener('scroll', async () => {
      if (chatArea.scrollTop < 100) {
        const firstMsg = this.msgList?.querySelector('[data-msg-id]');
        if (!firstMsg) return;
        const beforeId = firstMsg.dataset.msgId;
        const res = await fetch(`/messages/load/${this.roomType}/${this.roomId}/?before=${beforeId}`).then(r => r.json());
        if (res.messages && res.messages.length > 0) {
          const prevH = chatArea.scrollHeight;
          const savedLast = this.lastSenderId;
          const savedDate = this.lastDate;
          this.lastSenderId = null; this.lastDate = null;
          const temp = document.createDocumentFragment();
          res.messages.forEach(m => this.renderMessagePrepend(m, temp));
          this.msgList.prepend(temp);
          chatArea.scrollTop = chatArea.scrollHeight - prevH;
          this.lastSenderId = savedLast;
          this.lastDate = savedDate;
        }
      }
    });
  }

  renderMessagePrepend(msg, container) {
    // Simplified prepend version
    const row = document.createElement('div');
    row.className = 'message-row';
    row.setAttribute('data-msg-id', msg.id);
    row.setAttribute('data-sender-id', msg.sender_id);
    let contentHtml = msg.is_deleted ? '<div class="msg-text deleted"><em>[Message deleted]</em></div>' :
      msg.file ? this.renderFile(msg.file) : `<div class="msg-text">${this.linkify(this.esc(msg.content))}</div>`;
    row.innerHTML = `
      <div class="avatar avatar-36 msg-avatar" style="background:var(--accent)">${msg.sender_initials || msg.sender_name[0]}</div>
      <div class="msg-body">
        <div class="msg-meta">
          <span class="msg-name">${this.esc(msg.sender_name)}</span>
          <span class="msg-time">${msg.timestamp}</span>
        </div>
        ${contentHtml}
      </div>`;
    container.appendChild(row);
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  const chatEl = document.getElementById('chat-root');
  if (chatEl) {
    window.zChat = new ZChat(
      chatEl.dataset.roomType,
      chatEl.dataset.roomId,
      chatEl.dataset.userId,
    );
  }
});
