/* ================================================================
   main.js — Portfolio site JS
   Handles: skill bar animation, project filter, chatbot widget
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Active nav link ──────────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      link.classList.add('active');
    } else if (href === '/' && currentPath === '/') {
      link.classList.add('active');
    }
  });

  // ── Skill bar animation (triggered when bars scroll into view) ─
  const bars = document.querySelectorAll('.skill-bar-fill');
  if (bars.length) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          el.style.width = el.dataset.pct + '%';
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.3 });
    bars.forEach(bar => observer.observe(bar));
  }

  // ── Project category filter ───────────────────────────────────
  const filterBtns = document.querySelectorAll('.filter-btn');
  const projectCards = document.querySelectorAll('.project-card');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;
      projectCards.forEach(card => {
        if (filter === 'all' || card.dataset.category === filter) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // ── Floating chatbot widget ───────────────────────────────────
  const toggleBtn = document.getElementById('chat-toggle-btn');
  const panel = document.getElementById('chat-panel');
  const messagesEl = document.getElementById('chat-messages');
  const chatInput = document.getElementById('chat-widget-input');
  const sendBtn = document.getElementById('chat-widget-send');

  if (!toggleBtn) return; // widget not present on chat page itself

  let sessionId = localStorage.getItem('chatSessionId') || null;

  toggleBtn.addEventListener('click', () => {
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden') && messagesEl.children.length === 0) {
      appendMsg('assistant', "Hi! I'm Marco's AI assistant. Ask me anything about his background, projects, or skills.");
    }
    chatInput && chatInput.focus();
  });

  function appendMsg(role, text) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.textContent = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function showTyping() {
    const el = document.createElement('div');
    el.className = 'chat-typing';
    el.id = 'typing-indicator';
    el.innerHTML = '<span class="dots"><span>•</span><span>•</span><span>•</span></span>';
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function removeTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
  }

  async function sendMessage(text) {
    if (!text.trim()) return;
    appendMsg('user', text);
    showTyping();
    sendBtn.disabled = true;

    try {
      const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
      const res = await fetch('/chat/api/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      const data = await res.json();
      removeTyping();

      if (res.status === 429) {
        appendMsg('assistant', 'You have reached the message limit for this session. Please refresh to start a new conversation.');
        return;
      }

      if (data.session_id) sessionId = data.session_id;
      localStorage.setItem('chatSessionId', sessionId);
      appendMsg('assistant', data.reply || 'Sorry, I had trouble understanding that.');
    } catch {
      removeTyping();
      appendMsg('assistant', 'Something went wrong. Please try again.');
    } finally {
      sendBtn.disabled = false;
    }
  }

  sendBtn && sendBtn.addEventListener('click', () => {
    const text = chatInput.value.trim();
    chatInput.value = '';
    sendMessage(text);
  });

  chatInput && chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const text = chatInput.value.trim();
      chatInput.value = '';
      sendMessage(text);
    }
  });

});
