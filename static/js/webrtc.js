/* ═══════════════════════════════════════════
   ZConnect — WebRTC Call Engine
   Supports: video, audio, screen share, group calls
   ═══════════════════════════════════════════ */

const STUN_SERVERS = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    { urls: 'stun:stun2.l.google.com:19302' },
  ],
};

class ZCallEngine {
  constructor(opts) {
    this.roomId = opts.roomId;
    this.myId = parseInt(opts.myId);
    this.myName = opts.myName;
    this.myInitials = opts.myInitials;
    this.callType = opts.callType || 'video';

    this.ws = null;
    this.localStream = null;
    this.screenStream = null;
    this.peers = new Map(); // userId → RTCPeerConnection
    this.streams = new Map(); // userId → MediaStream
    this.isMuted = false;
    this.isCamOff = false;
    this.isScreenSharing = false;
    this.callStartTime = null;
    this.timerInterval = null;

    // DOM refs
    this.videosGrid = document.getElementById('call-videos');
    this.timerEl = document.getElementById('call-timer');
    this.muteBtn = document.getElementById('btn-mute');
    this.camBtn = document.getElementById('btn-cam');
    this.screenBtn = document.getElementById('btn-screen');
    this.endBtn = document.getElementById('btn-end');

    this.init();
  }

  async init() {
    await this.getLocalMedia();
    this.renderLocalTile();
    this.connectWS();
    this.bindControls();
    this.startTimer();
  }

  async getLocalMedia() {
    const constraints = { audio: true, video: this.callType === 'video' ? { width: 1280, height: 720 } : false };
    try {
      this.localStream = await navigator.mediaDevices.getUserMedia(constraints);
    } catch (err) {
      console.warn('Media access denied:', err);
      this.localStream = new MediaStream();
      showToast('Camera/microphone not available', 'warn');
    }
  }

  renderLocalTile() {
    const tile = this.createTile(this.myId, `${this.myName} (You)`, this.myInitials, true);
    const video = tile.querySelector('video');
    video.srcObject = this.localStream;
    video.muted = true;
    video.play().catch(() => {});
    this.videosGrid.appendChild(tile);
    this.updateGridLayout();
  }

  createTile(userId, name, initials, isLocal = false) {
    const tile = document.createElement('div');
    tile.className = 'video-tile';
    tile.id = `tile-${userId}`;
    tile.innerHTML = `
      <video autoplay playsinline ${isLocal ? 'muted' : ''}></video>
      <div class="tile-avatar">
        <div class="avatar avatar-80" style="background:var(--accent);font-size:28px">${initials || name[0]}</div>
      </div>
      <div class="tile-label">${name}</div>
      <div class="tile-controls">
        <div class="tile-mic-off" title="Muted">🔇</div>
        <div class="tile-cam-off" title="Camera off">📷</div>
      </div>
    `;
    return tile;
  }

  connectWS() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    this.ws = new WebSocket(`${proto}://${location.host}/ws/call/${this.roomId}/`);
    this.ws.onopen = () => { console.log('Call WS connected'); };
    this.ws.onmessage = e => this.onSignal(JSON.parse(e.data));
    this.ws.onclose = () => {
      console.log('Call WS closed');
      setTimeout(() => this.connectWS(), 2000);
    };
  }

  async onSignal(data) {
    const { type, from_id, user_id } = data;

    if (type === 'peer_joined') {
      if (data.user_id === this.myId) return;
      // I'm the existing user, create offer for the new peer
      await this.createPeerConnection(data.user_id, data.user_name, data.user_initials);
      await this.sendOffer(data.user_id);
    }
    else if (type === 'peer_left') {
      this.removePeer(data.user_id);
    }
    else if (type === 'offer') {
      if (from_id === this.myId) return;
      // Create PC and send answer
      const pc = await this.createPeerConnection(from_id, `User ${from_id}`, '?');
      await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      this.wsend({ type: 'answer', sdp: pc.localDescription, target_id: from_id });
    }
    else if (type === 'answer') {
      if (from_id === this.myId) return;
      const pc = this.peers.get(from_id);
      if (pc && pc.signalingState !== 'stable') {
        await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
      }
    }
    else if (type === 'ice') {
      if (from_id === this.myId) return;
      const pc = this.peers.get(from_id);
      if (pc && data.candidate) {
        try { await pc.addIceCandidate(new RTCIceCandidate(data.candidate)); } catch (e) {}
      }
    }
    else if (type === 'control') {
      this.handleRemoteControl(data);
    }
  }

  async createPeerConnection(userId, userName, initials) {
    if (this.peers.has(userId)) return this.peers.get(userId);

    const pc = new RTCPeerConnection(STUN_SERVERS);
    this.peers.set(userId, pc);

    // Add local tracks
    this.localStream.getTracks().forEach(track => pc.addTrack(track, this.localStream));
    if (this.screenStream) {
      this.screenStream.getTracks().forEach(track => pc.addTrack(track, this.screenStream));
    }

    // Remote stream
    const remoteStream = new MediaStream();
    this.streams.set(userId, remoteStream);

    pc.ontrack = e => {
      remoteStream.addTrack(e.track);
      const tile = document.getElementById(`tile-${userId}`);
      if (tile) {
        const video = tile.querySelector('video');
        video.srcObject = remoteStream;
        video.play().catch(() => {});
      }
    };

    pc.onicecandidate = e => {
      if (e.candidate) {
        this.wsend({ type: 'ice', candidate: e.candidate.toJSON(), target_id: userId });
      }
    };

    pc.onconnectionstatechange = () => {
      if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
        this.removePeer(userId);
      }
    };

    // Create tile
    const tile = this.createTile(userId, userName, initials);
    this.videosGrid.appendChild(tile);
    this.updateGridLayout();

    return pc;
  }

  async sendOffer(targetId) {
    const pc = this.peers.get(targetId);
    if (!pc) return;
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    this.wsend({ type: 'offer', sdp: pc.localDescription, target_id: targetId });
  }

  removePeer(userId) {
    const pc = this.peers.get(userId);
    if (pc) { pc.close(); this.peers.delete(userId); }
    this.streams.delete(userId);
    const tile = document.getElementById(`tile-${userId}`);
    if (tile) tile.remove();
    this.updateGridLayout();
    showToast(`User left the call`, 'info', 2000);
  }

  handleRemoteControl(data) {
    const tile = document.getElementById(`tile-${data.user_id}`);
    if (!tile) return;
    if (data.action === 'mute') tile.classList.toggle('muted', data.value);
    if (data.action === 'cam') tile.classList.toggle('cam-off', data.value);
  }

  // ── Controls ──────────────────────────────────────────────────────────────

  toggleMute() {
    this.isMuted = !this.isMuted;
    this.localStream.getAudioTracks().forEach(t => t.enabled = !this.isMuted);
    this.muteBtn.classList.toggle('off', this.isMuted);
    this.muteBtn.title = this.isMuted ? 'Unmute' : 'Mute';
    this.muteBtn.textContent = this.isMuted ? '🔇' : '🎙️';
    const myTile = document.getElementById(`tile-${this.myId}`);
    if (myTile) myTile.classList.toggle('muted', this.isMuted);
    this.broadcastControl('mute', this.isMuted);
  }

  toggleCam() {
    this.isCamOff = !this.isCamOff;
    this.localStream.getVideoTracks().forEach(t => t.enabled = !this.isCamOff);
    this.camBtn.classList.toggle('off', this.isCamOff);
    this.camBtn.textContent = this.isCamOff ? '📷' : '🎥';
    const myTile = document.getElementById(`tile-${this.myId}`);
    if (myTile) myTile.classList.toggle('cam-off', this.isCamOff);
    this.broadcastControl('cam', this.isCamOff);
  }

  async toggleScreenShare() {
    if (this.isScreenSharing) {
      // Stop screen share, restore camera
      this.screenStream.getTracks().forEach(t => t.stop());
      this.screenStream = null;
      this.isScreenSharing = false;
      this.screenBtn.classList.remove('active');
      this.screenBtn.textContent = '🖥️';

      // Remove screen share tile
      const screenTile = document.getElementById('screen-share-tile');
      if (screenTile) screenTile.remove();

      // Replace video tracks in all peer connections with camera
      const camTrack = this.localStream.getVideoTracks()[0];
      if (camTrack) {
        this.peers.forEach(pc => {
          const sender = pc.getSenders().find(s => s.track?.kind === 'video');
          if (sender) sender.replaceTrack(camTrack);
        });
      }
    } else {
      try {
        this.screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
        this.isScreenSharing = true;
        this.screenBtn.classList.add('active');
        this.screenBtn.textContent = '🛑';

        const screenTrack = this.screenStream.getVideoTracks()[0];
        screenTrack.addEventListener('ended', () => { if (this.isScreenSharing) this.toggleScreenShare(); });

        // Show local screen share tile
        const screenTile = document.createElement('div');
        screenTile.className = 'video-tile screen-share-tile';
        screenTile.id = 'screen-share-tile';
        screenTile.innerHTML = `<video autoplay muted playsinline></video><div class="tile-label">📺 Your screen</div>`;
        screenTile.querySelector('video').srcObject = this.screenStream;
        screenTile.querySelector('video').play().catch(() => {});
        this.videosGrid.prepend(screenTile);

        // Replace video tracks in all peer connections
        this.peers.forEach(pc => {
          const sender = pc.getSenders().find(s => s.track?.kind === 'video');
          if (sender) sender.replaceTrack(screenTrack).catch(() => {
            pc.addTrack(screenTrack, this.screenStream);
          });
        });
      } catch (err) {
        if (err.name !== 'NotAllowedError') showToast('Screen share failed', 'error');
      }
    }
    this.updateGridLayout();
  }

  async endCall() {
    // Stop all streams
    this.localStream?.getTracks().forEach(t => t.stop());
    this.screenStream?.getTracks().forEach(t => t.stop());
    this.peers.forEach(pc => pc.close());

    // Notify server
    try {
      await fetch(`/call/${this.roomId}/end/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() },
      });
    } catch (e) {}

    this.ws?.close();
    clearInterval(this.timerInterval);
    window.location.href = '/dashboard/';
  }

  broadcastControl(action, value) {
    this.wsend({ type: 'control', action, value });
  }

  wsend(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  updateGridLayout() {
    const count = this.videosGrid.children.length;
    this.videosGrid.className = 'call-videos';
    if (count === 1) this.videosGrid.classList.add('solo');
    else if (count === 2) this.videosGrid.classList.add('pair');
  }

  startTimer() {
    this.callStartTime = Date.now();
    this.timerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - this.callStartTime) / 1000);
      const m = Math.floor(elapsed / 60).toString().padStart(2, '0');
      const s = (elapsed % 60).toString().padStart(2, '0');
      if (this.timerEl) this.timerEl.textContent = `${m}:${s}`;
    }, 1000);
  }

  bindControls() {
    this.muteBtn?.addEventListener('click', () => this.toggleMute());
    this.camBtn?.addEventListener('click', () => this.toggleCam());
    this.screenBtn?.addEventListener('click', () => this.toggleScreenShare());
    this.endBtn?.addEventListener('click', () => this.endCall());

    // Hide cam button for audio-only calls
    if (this.callType === 'audio' && this.camBtn) {
      this.camBtn.style.display = 'none';
      this.screenBtn.style.display = 'none';
    }

    window.addEventListener('beforeunload', () => {
      this.localStream?.getTracks().forEach(t => t.stop());
    });
  }
}

// Boot on page load
document.addEventListener('DOMContentLoaded', () => {
  const callRoot = document.getElementById('call-root');
  if (callRoot) {
    window.zCall = new ZCallEngine({
      roomId: callRoot.dataset.roomId,
      myId: callRoot.dataset.myId,
      myName: callRoot.dataset.myName,
      myInitials: callRoot.dataset.myInitials,
      callType: callRoot.dataset.callType,
    });
  }
});
