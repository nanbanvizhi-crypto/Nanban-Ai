"""
Client-side upgrades injected on page load:
  👁️ Vizhi — hands-free voice assistant (JARVIS-style): wake word, listen → act → speak,
     live transcript, natural voice, follow-up conversation, self-healing, sound-reactive orb.
  🎤 one-shot voice input · 🔊 read-aloud answers · 🌓 light/dark theme.

All in the browser (free, private) via the Web Speech API — best in Chrome / Edge / Android.
Delivered through demo.load(js=INIT_JS).
"""

INIT_JS = r"""
() => {
  try {
    // ---------- theme ----------
    const applyTheme = (t) => {
      const dark = t === 'dark';
      document.body.classList.toggle('dark', dark);
      document.querySelectorAll('gradio-app, .gradio-container').forEach(el => el.classList.toggle('dark', dark));
      try { localStorage.setItem('nb-theme', t); } catch(e) {}
    };
    let saved = 'light';
    try { saved = localStorage.getItem('nb-theme') || 'dark'; } catch(e) {}
    applyTheme(saved);

    // ---------- left navigation (replaces the top tab bar) + chat-history clicks ----------
    try { if (!window.__nbNav) { window.__nbNav = true;
      // sub-menus that exist as tabs INSIDE a section (rendered lazily, so listed here)
      const SUBS = { 'Learn': ['Sandbox', 'Guided Labs', 'SOC Sim', 'Progress'] };
      const split = (txt) => { txt = (txt || '').replace(/\s+/g, ' ').trim();
        const m = txt.match(/^(\S+)\s+(.*)$/); return m ? { ico: m[1], name: m[2] } : { ico: '•', name: txt }; };
      const topBtns = () => {
        const wrap = document.querySelector('.tabs > .tab-wrapper'); if (!wrap) return [];
        const a = Array.from(wrap.querySelectorAll('[role="tablist"] button[role="tab"]'));
        wrap.querySelectorAll('.overflow-dropdown button').forEach(b => a.push(b));
        return a.filter(b => (b.innerText || '').trim());
      };
      const clickTop = (name) => { const b = topBtns().find(x => split(x.innerText).name === name); if (b) b.click(); return !!b; };
      const modeLabels = () => Array.from(document.querySelectorAll('#modes label'));
      const clickSub = (sub, n) => {
        const b = Array.from(document.querySelectorAll('.tabitem .tabs [role="tab"], .tabitem .tabs .overflow-dropdown button'))
          .find(x => (x.innerText || '').includes(sub));
        if (b) { b.click(); return; }
        if ((n || 0) < 30) setTimeout(() => clickSub(sub, (n || 0) + 1), 150);   // panel still rendering
      };
      let open = { Chat: true };
      try { open = Object.assign(open, JSON.parse(localStorage.getItem('nb-nav-open') || '{}')); } catch (e) {}
      const saveOpen = () => { try { localStorage.setItem('nb-nav-open', JSON.stringify(open)); } catch (e) {} };
      let activeSub = {};
      const el = (tag, cls, text) => { const x = document.createElement(tag); if (cls) x.className = cls; if (text != null) x.textContent = text; return x; };

      const render = () => {
        const nav = document.getElementById('nb-nav'); if (!nav) return;
        const btns = topBtns(); if (!btns.length) return;
        const modes = modeLabels();
        const sig = btns.map(b => b.innerText.trim() + (b.classList.contains('selected') ? '*' : '')).join('|') + '#'
                  + modes.map(l => l.innerText.trim() + (l.classList.contains('selected') ? '*' : '')).join('|') + '#'
                  + JSON.stringify(open) + JSON.stringify(activeSub);
        if (nav.dataset.sig === sig) return;
        nav.dataset.sig = sig; nav.innerHTML = '';
        btns.forEach(b => {
          const { ico, name } = split(b.innerText);
          const active = b.classList.contains('selected') || b.getAttribute('aria-selected') === 'true';
          let subs = [];
          if (name === 'Chat') subs = modes.map(l => Object.assign(split(l.innerText),
            { active: l.classList.contains('selected'), go: () => { clickTop('Chat'); l.click(); } }));
          else if (SUBS[name]) subs = SUBS[name].map(sn => ({ ico: '›', name: sn, active: activeSub[name] === sn,
            go: () => { clickTop(name); activeSub[name] = sn; clickSub(sn, 0); } }));
          const item = el('div', 'nbn-item' + (active ? ' active' : '') + (subs.length && open[name] ? ' open' : ''));
          item.append(el('span', 'nbn-ico', ico), el('span', 'nbn-name', name));
          if (subs.length) item.append(el('span', 'nbn-chev', '▾'));
          item.onclick = (e) => {
            const onChev = e.target.classList && e.target.classList.contains('nbn-chev');
            if (subs.length && (onChev || active)) open[name] = !open[name];      // toggle the dropdown
            else { b.click(); if (subs.length) open[name] = true; }
            saveOpen(); setTimeout(render, 80);
          };
          nav.append(item);
          if (subs.length) {
            const box = el('div', 'nbn-sub' + (open[name] ? ' open' : ''));
            subs.forEach(s => {
              const si = el('div', 'nbn-subitem' + (s.active && active ? ' active' : ''));
              si.append(el('span', 'nbn-sico', s.ico), el('span', 'nbn-sname', s.name));
              si.onclick = () => { s.go(); setTimeout(render, 150); };
              box.append(si);
            });
            nav.append(box);
          }
        });
      };
      render(); setInterval(render, 350);       // cheap: only re-draws when the signature changes

      // chat history: open / delete a saved chat from the sidebar
      document.addEventListener('click', (e) => {
        const t = e.target; if (!t || !t.closest) return;
        const del = t.closest('[data-del]'); const it = t.closest('[data-chat]');
        if (!del && !it) return;
        e.preventDefault(); e.stopPropagation();
        const token = del ? 'del:' + del.getAttribute('data-del') : it.getAttribute('data-chat');
        const box = document.querySelector('#hist-pick textarea, #hist-pick input');
        const go = document.getElementById('hist-go');
        if (!box || !go) return;
        const proto = box.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
        Object.getOwnPropertyDescriptor(proto, 'value').set.call(box, token);
        box.dispatchEvent(new Event('input', { bubbles: true }));
        if (!del) clickTop('Chat');
        setTimeout(() => go.click(), 140);
      }, true);
    } } catch (e) { /* navigation must never break the page */ }

    if (window.innerWidth < 900) {
      const b = document.querySelector('.sidebar-parent button.toggle-button, button[aria-label="Toggle Sidebar"]');
      if (b) setTimeout(() => b.click(), 300);
    }

    // ---------- 🐉 Kali panel: clickable commands + reference height sync ----------
    if (!window.__kaliUI) {
      window.__kaliUI = true;
      // click a command in the Command Reference → drop it into the terminal input
      document.addEventListener('click', (e) => {
        const el = e.target.closest('#kali-ref-view code, #kali-ref-view .kali-cmd');
        if (!el) return;
        const cmd = (el.getAttribute('data-cmd') || el.textContent || '').trim();
        if (!cmd) return;
        const ta = document.querySelector('#kali-in textarea');
        if (!ta) return;
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(ta, cmd);
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        ta.focus();
        try { ta.scrollIntoView({ block: 'center', behavior: 'smooth' }); } catch (e2) {}
        ta.style.transition = 'box-shadow .2s';
        ta.style.boxShadow = '0 0 0 3px rgba(214,85,46,.45)';
        setTimeout(() => { ta.style.boxShadow = ''; }, 450);
      });
      // keep the Command Reference exactly as tall as the terminal, with its own scrollbar
      const syncKaliRef = () => {
        const term = document.querySelector('#kali-term');
        const rv = document.querySelector('#kali-ref-view');
        if (!term || !rv) return;
        const h = term.getBoundingClientRect().height;
        if (h > 0) { rv.style.maxHeight = Math.max(220, h - 92) + 'px'; rv.style.overflowY = 'auto'; }
      };
      const kaliWatch = setInterval(() => {
        const term = document.querySelector('#kali-term');
        if (term) { try { new ResizeObserver(syncKaliRef).observe(term); } catch (e3) {} syncKaliRef(); clearInterval(kaliWatch); }
      }, 400);
      window.addEventListener('resize', syncKaliRef);
      // re-sync when the Kali tab is opened (panel was hidden until then)
      document.addEventListener('click', (e) => {
        const tab = e.target.closest('button[role="tab"]');
        if (tab && /Kali/.test(tab.textContent || '')) setTimeout(syncKaliRef, 200);
      });
      // open the Connect dialog from the header button (instant, class-based)
      document.addEventListener('click', (e) => {
        if (e.target.closest('#kali-connect-toggle')) {
          const m = document.querySelector('#kali-connect-modal');
          if (m) {
            m.classList.add('kopen');
            const u = m.querySelector('#kali-user textarea, #kali-user input');
            if (u) setTimeout(() => u.focus(), 60);
          }
        }
      });
      // close on the ✕ button or when clicking the dimmed backdrop
      document.addEventListener('click', (e) => {
        const m = document.querySelector('#kali-connect-modal');
        if (!m || !m.classList.contains('kopen')) return;
        if (e.target === m || e.target.closest('#kali-modal-close')) m.classList.remove('kopen');
      });
      // Esc also closes the dialog
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          const m = document.querySelector('#kali-connect-modal');
          if (m) m.classList.remove('kopen');
        }
      });
    }

    // ---------- 👁 show / hide the hosted API-key field ----------
    if (!window.__nbKeyEye) {
      window.__nbKeyEye = true;
      const addEye = () => {
        const wrap = document.querySelector('#nb-hosted-key');
        if (!wrap || wrap.querySelector('.nb-eye')) return;
        const inp = wrap.querySelector('input');
        if (!inp) return;
        wrap.style.position = 'relative';
        inp.style.paddingRight = '36px';
        const b = document.createElement('button');
        b.type = 'button'; b.className = 'nb-eye'; b.textContent = '👁';
        b.title = 'Show / hide key';
        b.style.cssText = 'position:absolute;right:10px;top:50%;transform:translateY(-50%);z-index:5;'
          + 'background:transparent;border:none;cursor:pointer;font-size:16px;opacity:.6;padding:2px;line-height:1;';
        b.addEventListener('click', (e) => {
          e.preventDefault();
          const i = wrap.querySelector('input'); if (!i) return;
          const show = i.type === 'password';
          i.type = show ? 'text' : 'password';
          b.style.opacity = show ? '1' : '.6';
        });
        wrap.appendChild(b);
      };
      addEye();
      // the Admin tab renders lazily — re-check after clicks (e.g. opening Admin)
      document.addEventListener('click', () => setTimeout(addEye, 200));
    }

    // ---------- PWA: mobile / iPhone home-screen meta (Gradio already serves the manifest) ----------
    const addMeta = (name, content, attr) => {
      attr = attr || 'name';
      if (document.querySelector(`meta[${attr}="${name}"]`)) return;
      const m = document.createElement('meta'); m.setAttribute(attr, name); m.content = content; document.head.appendChild(m);
    };
    addMeta('apple-mobile-web-app-capable', 'yes');
    addMeta('mobile-web-app-capable', 'yes');
    addMeta('apple-mobile-web-app-status-bar-style', 'black-translucent');
    addMeta('apple-mobile-web-app-title', 'Nanban');
    addMeta('theme-color', '#4f46e5');

    if (document.getElementById('nb-tools')) return;

    // ---------- keyboard shortcuts ----------
    document.addEventListener('keydown', (e) => {
      const mod = e.ctrlKey || e.metaKey;
      if (mod && (e.key === 'k' || e.key === 'K')) {   // focus message box
        const ta = document.querySelector('#composer textarea'); if (ta) { e.preventDefault(); ta.focus(); }
      } else if (mod && (e.key === 'j' || e.key === 'J')) {   // toggle Vizhi
        const o = document.getElementById('nb-vizhi'); if (o) { e.preventDefault(); o.click(); }
      } else if (e.key === 'Escape') {   // stop speaking
        if (window.speechSynthesis) window.speechSynthesis.cancel();
      }
    });

    // ---------- styles ----------
    const st = document.createElement('style');
    st.textContent = `
      @keyframes nbpulse { 0%{box-shadow:0 0 0 0 rgba(79,209,255,.55)} 70%{box-shadow:0 0 0 18px rgba(79,209,255,0)} 100%{box-shadow:0 0 0 0 rgba(79,209,255,0)} }
      @keyframes nbbreath { 0%,100%{transform:scale(1)} 50%{transform:scale(1.07)} }
      @keyframes nbslideup { from{opacity:0;transform:translate(-50%,18px)} to{opacity:1;transform:translate(-50%,0)} }
      #nb-vizhi { transition: background .25s ease, transform .12s ease; }
      #nb-vizhi.nb-pulse { animation: nbpulse 1.6s infinite; }
      #nb-vizhi.nb-breath { animation: nbbreath 2.4s ease-in-out infinite; }
      #nb-jcap { position:fixed; right:84px; bottom:176px; z-index:9998; max-width:270px;
        background:rgba(10,16,32,.94); color:#dbe7ff; font-size:12.5px; line-height:1.5;
        padding:9px 13px; border-radius:13px; box-shadow:0 8px 24px rgba(0,0,0,.34);
        display:none; backdrop-filter:blur(5px); border:1px solid rgba(110,231,255,.18); }
      #nb-jcap .nb-heard { color:#9fe7ff; font-style:italic; margin-top:3px; display:block; }
    `;
    document.head.appendChild(st);

    // ---------- toolbar ----------
    const bar = document.createElement('div');
    bar.id = 'nb-tools';
    bar.style.cssText = 'position:fixed;right:14px;bottom:118px;display:flex;flex-direction:column;align-items:center;gap:8px;z-index:9998;';
    const mk = (txt, title) => {
      const b = document.createElement('button');
      b.textContent = txt; b.title = title;
      b.style.cssText = 'width:42px;height:42px;border-radius:50%;border:1px solid rgba(120,90,60,.25);'
        + 'background:var(--block-background-fill,#fff);font-size:18px;cursor:pointer;'
        + 'box-shadow:0 4px 14px rgba(40,24,8,.14);display:flex;align-items:center;justify-content:center;';
      return b;
    };
    const orb = document.createElement('button');
    orb.id = 'nb-vizhi'; orb.textContent = '👁️'; orb.title = 'Vizhi — hands-free voice assistant';
    orb.style.cssText = 'width:60px;height:60px;border-radius:50%;border:none;cursor:pointer;font-size:26px;'
      + 'display:flex;align-items:center;justify-content:center;color:#fff;'
      + 'background:radial-gradient(circle at 50% 38%, #4fd1ff, #1b6fd6 60%, #0b3a8a);'
      + 'box-shadow:0 6px 22px rgba(11,58,138,.45);';
    const cmdBtn = mk('⌨️', 'Type a command to Vizhi (works without a mic)');
    const micBtn = mk('🎤', 'Speak once → message box');
    const spkBtn = mk('🔊', 'Read answers aloud (toggle)');
    const thmBtn = mk('🌓', 'Light / dark');
    bar.append(orb, cmdBtn, micBtn, spkBtn, thmBtn);
    document.body.appendChild(bar);

    // ---------- Vizhi typed-command box (universal fallback — no mic / any browser) ----------
    // Lets Vizhi work even where the Web Speech API is missing (Firefox, in-app browsers,
    // phone over a plain-http LAN address). Same routing as the voice path.
    const cmdWrap = document.createElement('div');
    cmdWrap.id = 'nb-cmdbox';
    cmdWrap.style.cssText = 'position:fixed;right:70px;bottom:118px;z-index:9999;width:min(82vw,300px);'
      + 'display:none;background:rgba(10,16,32,.96);border:1px solid rgba(110,231,255,.28);'
      + 'border-radius:14px;padding:10px;box-shadow:0 10px 30px rgba(0,0,0,.4);backdrop-filter:blur(6px);';
    cmdWrap.innerHTML =
      '<div style="font-size:12px;color:#9fe7ff;margin-bottom:6px">👁️ Vizhi — type a command</div>'
      + '<input id="nb-cmdin" placeholder="e.g. open India Lab · draw a cat · dark mode"'
      + ' style="width:100%;box-sizing:border-box;padding:9px 10px;border-radius:9px;border:1px solid rgba(110,231,255,.3);'
      + 'background:#0b1324;color:#eaf2ff;font-size:13px;outline:none">'
      + '<div style="font-size:11px;color:#8aa0c8;margin-top:6px;line-height:1.5">'
      + 'Try: <b style="color:#cfe0ff">open images</b>, <b style="color:#cfe0ff">open kali</b>, '
      + '<b style="color:#cfe0ff">new chat</b>, <b style="color:#cfe0ff">light mode</b>, or just ask anything.</div>';
    document.body.appendChild(cmdWrap);

    // ---------- first-run welcome card (one time, modern) ----------
    try {
      if (!localStorage.getItem('nb-seen')) {
        localStorage.setItem('nb-seen', '1');
        const toast = document.createElement('div');
        toast.id = 'nb-welcome';
        toast.style.cssText = 'position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:10000;'
          + 'width:min(92vw,400px);background:linear-gradient(135deg,#141d33,#0d1526);color:#eaf2ff;'
          + 'padding:16px 16px 14px;border-radius:18px;box-shadow:0 18px 44px rgba(0,0,0,.5);'
          + 'border:1px solid rgba(110,231,255,.22);backdrop-filter:blur(8px);animation:nbslideup .4s ease;';
        toast.innerHTML =
          '<div style="display:flex;gap:12px;align-items:flex-start">'
          + '<div style="flex:0 0 auto;width:42px;height:42px;border-radius:13px;display:flex;align-items:center;'
          +   'justify-content:center;font-size:22px;background:radial-gradient(circle at 50% 35%,#6ee7ff,#1b6fd6);'
          +   'box-shadow:0 5px 16px rgba(27,111,214,.5)">👋</div>'
          + '<div style="flex:1"><div style="font-weight:700;font-size:15px;margin-bottom:3px">Vanakkam, nanba!</div>'
          +   '<div style="font-size:12.8px;line-height:1.55;color:#b9c6e4">First time-aa? '
          +   '<b style="color:#eaf2ff">Admin → Getting Started</b> la setup checklist paaru. Bottom-right '
          +   '<b style="color:#eaf2ff">👁️ Vizhi</b> orb press panni voice-la pesalaam.</div></div></div>'
          + '<div style="display:flex;justify-content:flex-end;margin-top:13px">'
          +   '<button id="nb-toast-x" style="border:none;cursor:pointer;font-weight:700;font-size:13px;color:#fff;'
          +   'padding:9px 22px;border-radius:11px;background:linear-gradient(135deg,#6ee7ff,#1b6fd6);'
          +   'box-shadow:0 5px 14px rgba(27,111,214,.45)">Got it 🚀</button></div>';
        document.body.appendChild(toast);
        const close = () => { toast.style.transition='opacity .25s,transform .25s';
          toast.style.opacity='0'; toast.style.transform='translate(-50%,16px)'; setTimeout(()=>toast.remove(),260); };
        toast.querySelector('#nb-toast-x').onclick = close;
        setTimeout(close, 14000);
      }
    } catch(e) {}

    const cap = document.createElement('div'); cap.id = 'nb-jcap'; document.body.appendChild(cap);
    let capTimer = null;
    const hideCap = () => { cap.style.display = 'none'; };
    const showCap = (h, ms) => { cap.innerHTML = h; cap.style.display = 'block'; clearTimeout(capTimer); if (ms) capTimer = setTimeout(hideCap, ms); };
    const esc = (s) => String(s || '').replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

    thmBtn.onclick = () => applyTheme(document.body.classList.contains('dark') ? 'light' : 'dark');

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const synth = window.speechSynthesis || null;

    // ============================ speech OUT ============================
    let speak = false;                       // "read answers aloud" toggle (🔊)
    let voices = [];
    const loadVoices = () => { try { voices = synth ? (synth.getVoices() || []) : []; } catch (e) { voices = []; } };
    if (synth) { loadVoices(); synth.onvoiceschanged = loadVoices; }
    const hasTamil = (t) => /[஀-௿]/.test(t || '');
    const voiceFor = (text) => {
      const best = (list) => list.find(v => /natural|online|neural|google/i.test(v.name)) || list[0];
      if (hasTamil(text)) { const ta = voices.filter(v => /^ta/i.test(v.lang)); if (ta.length) return best(ta); }
      const inn = voices.filter(v => /^en[-_]IN/i.test(v.lang)); if (inn.length) return best(inn);
      const gb = voices.filter(v => /^en[-_]GB/i.test(v.lang)); if (gb.length) return best(gb);
      const en = voices.filter(v => /^en/i.test(v.lang)); return en.length ? best(en) : (voices[0] || null);
    };
    const cleanForSpeech = (t) => (t || '')
      .replace(/```[\s\S]*?```/g, '. code block. ')
      .replace(/`([^`]+)`/g, '$1')
      .replace(/\*\*([^*]+)\*\*/g, '$1').replace(/\*([^*]+)\*/g, '$1')
      .replace(/^#{1,6}\s*/gm, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/https?:\/\/\S+/g, ' link ')
      .replace(/[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}\u{200D}]/gu, ' ')
      .replace(/[>_~|•#]/g, ' ').replace(/\s+/g, ' ').trim();

    let speakSeq = 0;                        // every new utterance chain invalidates the previous one
    const stopSpeaking = () => { speakSeq++; try { if (synth) synth.cancel(); } catch (e) {} };
    const speakText = (text, hooks) => {
      hooks = hooks || {};
      const done = () => { if (hooks.onEnd) hooks.onEnd(); };
      let say = cleanForSpeech(text);
      if (!synth || !say) { done(); return; }
      if (say.length > 900) say = say.slice(0, 900) + '. Mel details screen la irukku.';
      // speak sentence-sized chunks: browsers silently drop long utterances and never fire onend
      const parts = say.match(/[^.!?\n]+[.!?]*\s*/g) || [say];
      const chunks = []; let cur = '';
      parts.forEach(p => { if ((cur + p).length > 190 && cur) { chunks.push(cur); cur = p; } else cur += p; });
      if (cur.trim()) chunks.push(cur);
      stopSpeaking();
      const my = ++speakSeq; let i = 0, started = false, guard = null;
      const next = () => {
        clearTimeout(guard);
        if (my !== speakSeq) return;                         // superseded or stopped
        if (i >= chunks.length) { speakSeq++; done(); return; }
        const u = new SpeechSynthesisUtterance(chunks[i++]);
        const v = voiceFor(u.text);
        if (v) { u.voice = v; u.lang = v.lang; } else u.lang = 'en-IN';
        u.rate = 1.05; u.pitch = 1.0;
        u.onstart = () => { if (!started) { started = true; if (hooks.onStart) hooks.onStart(); } };
        u.onend = next; u.onerror = next;
        // watchdog: if the engine stalls, move on instead of leaving Vizhi stuck in "speaking"
        guard = setTimeout(() => { if (my === speakSeq) { try { synth.cancel(); } catch (e) {} next(); } }, 5000 + u.text.length * 120);
        try { synth.speak(u); } catch (e) { next(); }
      };
      next();
    };

    spkBtn.onclick = () => {
      speak = !speak;
      spkBtn.style.background = speak ? '#c56a44' : '';
      if (!speak) stopSpeaking();
    };

    // ============================ app-control helpers ============================
    const tabBtns = () => { const w = document.querySelector('.tabs > .tab-wrapper');
      return w ? Array.from(w.querySelectorAll('[role="tablist"] button[role="tab"], .overflow-dropdown button')) : []; };
    const clickTab = (name) => { const n = String(name || '').toLowerCase().trim(); if (!n) return false;
      const b = tabBtns().find(x => (x.innerText || '').toLowerCase().includes(n)); if (b) { b.click(); return true; } return false; };
    const clickMode = (label) => { const n = String(label || '').toLowerCase().trim(); if (!n) return false;
      const l = Array.from(document.querySelectorAll('#modes label')).find(x => (x.innerText || '').toLowerCase().includes(n));
      if (l) { l.click(); return true; } return false; };
    const setVal = (box, v) => {
      const proto = box.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, 'value').set.call(box, v);
      box.dispatchEvent(new Event('input', { bubbles: true }));
    };
    const waitFor = (sel, cb, tries) => { const x = document.querySelector(sel);
      if (x && x.offsetParent !== null) { cb(x); return; }
      if ((tries || 0) < 50) setTimeout(() => waitFor(sel, cb, (tries || 0) + 1), 160); };
    const btnByText = (re) => Array.from(document.querySelectorAll('button')).find(b => re.test(b.innerText || ''));
    const submitComposer = (text) => {
      const ta = document.querySelector('#composer textarea'); if (!ta) return;
      setVal(ta, text);
      setTimeout(() => {
        const btn = document.querySelector('#composer button.submit-button') || document.querySelector('#composer button[aria-label*="ubmit"]');
        if (btn) btn.click();
        else ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
      }, 90);
    };

    // ============================ Vizhi ============================
    let vizhiOn = false, vState = 'idle', rec = null, recActive = false, recWanted = false, followUntil = 0;
    let lastAnswer = '', pendingAnswer = false, answerTimer = null;
    // Wake word is OFF by default: speech engines can't reliably hear the word "Vizhi".
    let wakeMode = false;
    try { wakeMode = localStorage.getItem('nb-wake') === '1'; } catch (e) {}
    let micLang = 'ta-IN';                   // ta-IN hears Tamil + mixed English · en-IN = English only
    try { micLang = localStorage.getItem('nb-miclang') || 'ta-IN'; } catch (e) {}
    const WAKE_RE = /(vizhi|vili|vizi|vishi|vichy|whizzy|wizzy|jarvis|nanban|nanba|விழி|விலி|நண்பன்|நண்பா)/i;
    const pick = (a) => a[Math.floor(Math.random() * a.length)];
    const greeting = () => {
      const h = new Date().getHours();
      const g = h < 12 ? 'Kaalai vanakkam' : (h < 16 ? 'Madhiya vanakkam' : (h < 20 ? 'Maalai vanakkam' : 'Vanakkam'));
      return 'Vizhi online. ' + g + ' nanba. ' + pick([
        'Ella systems ready. Sollu, enna pannanum?', 'Naan standby la irukken — sollu.',
        'Un kannu naan, Vizhi. Sollu, pannidren.', 'Ready nanba. Command kudu.']);
    };
    // JARVIS: a quick spoken acknowledgement the instant a request lands (then the answer follows)
    const ACKS = ['Oru nodi nanba…', 'Paakuren…', 'Right away nanba…', 'Seri, paakuren…', 'Konja neram…'];
    const ackSpeak = (text) => { if (!vizhiOn) return; stopRec(); setState('thinking', text); speakText(pick(ACKS)); };
    const GRAD = {
      idle: 'radial-gradient(circle at 50% 38%, #4fd1ff, #1b6fd6 60%, #0b3a8a)',
      listening: 'radial-gradient(circle at 50% 38%, #6ee7ff, #0ea5e9 60%, #0369a1)',
      thinking: 'radial-gradient(circle at 50% 38%, #ffd27a, #f59e0b 60%, #b45309)',
      speaking: 'radial-gradient(circle at 50% 38%, #8ef5b0, #22c55e 60%, #15803d)',
    };
    const listenCap = (heard) => {
      const ltog = `<span id="nb-ltog" style="cursor:pointer;color:#6ee7ff;text-decoration:underline">[mic: ${micLang === 'ta-IN' ? 'Tamil + English' : 'English'}]</span>`;
      const tog = `<span id="nb-wtog" style="cursor:pointer;color:#6ee7ff;text-decoration:underline">[wake word: ${wakeMode ? 'ON' : 'OFF'}]</span>`;
      const hint = wakeMode ? 'Say <b>"Vizhi…"</b> then your command' : 'Just talk — "Kali open pannu", "CM yaar ippo", "ports scan pannu"';
      const h = heard ? `<span class="nb-heard">🗣️ ${esc(heard)}</span>` : '';
      return `🎙️ <b>Listening…</b> ${ltog} ${tog}<br><span style="opacity:.8">${hint}</span>${h}`;
    };
    const bindTog = () => {
      const w = document.getElementById('nb-wtog'); if (w) w.onclick = () => {
        wakeMode = !wakeMode; try { localStorage.setItem('nb-wake', wakeMode ? '1' : '0'); } catch (e) {}
        if (vState === 'listening') { showCap(listenCap()); bindTog(); } };
      const l = document.getElementById('nb-ltog'); if (l) l.onclick = () => {
        micLang = (micLang === 'ta-IN') ? 'en-IN' : 'ta-IN';
        try { localStorage.setItem('nb-miclang', micLang); } catch (e) {}
        if (rec) { try { rec.abort(); } catch (e) {} }          // onend restarts it in the new language
        if (vState === 'listening') { showCap(listenCap()); bindTog(); } };
    };
    const setState = (s, extra) => {
      vState = s;
      orb.style.background = GRAD[s] || GRAD.idle;
      orb.classList.toggle('nb-pulse', s === 'listening' || s === 'speaking');
      orb.classList.toggle('nb-breath', s === 'listening');
      if (s === 'idle') { hideCap(); return; }
      if (s === 'listening') { showCap(listenCap(extra)); bindTog(); }
      else if (s === 'thinking') showCap('💭 <b>Yosikiren…</b>' + (extra ? `<span class="nb-heard">🗣️ ${esc(extra)}</span>` : ''));
      else showCap('🔊 <b>Speaking…</b> <span style="opacity:.75">(orb-ah thattina niruthuven)</span>' + (extra ? `<span class="nb-heard">${esc(extra)}</span>` : ''));
    };
    const startRec = () => { recWanted = true; if (!rec || recActive) return; try { rec.lang = micLang; rec.start(); } catch (e) {} };
    const stopRec = () => { recWanted = false; if (!rec) return; try { rec.abort(); } catch (e) { try { rec.stop(); } catch (e2) {} } };
    const backToListening = () => { if (vizhiOn) { followUntil = Date.now() + 9000; setState('listening'); startRec(); } };
    const turnOff = () => { vizhiOn = false; pendingAnswer = false; clearTimeout(answerTimer); stopRec(); stopSpeaking(); setState('idle'); };

    // Speak as Vizhi. The mic is closed first so Vizhi never hears (and obeys) its own voice.
    const sayVizhi = (text) => {
      if (!vizhiOn) {                       // typed command while the orb is off: confirm on screen
        showCap('✅ ' + esc(text), 3500);
        if (speak) speakText(text);
        return;
      }
      stopRec(); setState('speaking', (text || '').slice(0, 90));
      speakText(text, { onEnd: backToListening });
    };

    // ---- ask the server what the sentence MEANS (works for English, Tanglish and Tamil script) ----
    let intentId = 0, intentCb = null, intentTimer = null;
    window.__vizhiIntent = (raw) => {
      let o = null; try { o = JSON.parse(raw); } catch (e) {}
      if (!o || !intentCb || (o.id !== undefined && Number(o.id) !== intentId)) return;
      const cb = intentCb; intentCb = null; clearTimeout(intentTimer); cb(o);
    };
    const askIntent = (text, cb) => {
      const box = document.querySelector('#viz-in textarea, #viz-in input'); const go = document.getElementById('viz-go');
      if (!box || !go) { cb({ action: 'chat' }); return; }
      intentId++; intentCb = cb;
      setVal(box, intentId + '|' + text); setTimeout(() => go.click(), 70);
      clearTimeout(intentTimer);
      intentTimer = setTimeout(() => { if (intentCb) { const c = intentCb; intentCb = null; c({ action: 'chat' }); } }, 8000);
    };

    const execute = (o, t) => {
      const say = String(o.say || '').trim();
      const target = String(o.target || '').trim();
      switch (o.action) {
        case 'open_section':
          if (clickTab(target)) sayVizhi(say || (target + ' open pannitten.')); else sayVizhi('Andha section kedaikkala.');
          break;
        case 'set_mode':
          clickTab('Chat'); setTimeout(() => clickMode(target), 300);
          sayVizhi(say || (target + ' mode.')); break;
        case 'new_chat':
          clickTab('Chat'); setTimeout(() => { const nc = document.getElementById('new-chat'); if (nc) nc.click(); }, 250);
          sayVizhi(say || 'Pudhu chat ready.'); break;
        case 'theme':
          applyTheme(/light|velich/i.test(target) ? 'light' : 'dark'); sayVizhi(say || 'Theme maathitten.'); break;
        case 'kali_run':
          clickTab('Kali');
          waitFor('#kali-ai-in textarea', (ta) => { setVal(ta, target || t);
            setTimeout(() => { const b = document.getElementById('kali-ai-run'); if (b) b.click(); }, 200); });
          sayVizhi(say || 'Kali-la run pannuren.'); break;
        case 'terminal_run':
          clickTab('Terminal');
          waitFor('#term-in textarea', (ta) => { setVal(ta, target);
            setTimeout(() => { const b = document.querySelector('#term-in button'); if (b) b.click(); }, 200); });
          sayVizhi(say || 'Terminal-la run pannuren.'); break;
        case 'make_image':
          clickTab('Images');
          waitFor('#img-prompt textarea', (ta) => { setVal(ta, target || t);
            setTimeout(() => { const b = document.getElementById('img-gen'); if (b) b.click(); }, 200); });
          sayVizhi(say || 'Image ready pannuren.'); break;
        case 'repeat':
          sayVizhi(lastAnswer || 'Repeat panna onnum illa.'); break;
        case 'stop_speaking':
          stopSpeaking(); backToListening(); if (!vizhiOn) hideCap(); break;
        case 'vizhi_off':
          turnOff(); break;
        default:                             // a question / conversation → the chat answers, then Vizhi reads it
          clickTab('Chat');
          pendingAnswer = true; clearTimeout(answerTimer);
          answerTimer = setTimeout(() => { if (pendingAnswer) { pendingAnswer = false; backToListening(); if (!vizhiOn) hideCap(); } }, 70000);
          ackSpeak(t);                       // JARVIS: respond instantly, the full answer follows
          waitFor('#composer textarea', () => submitComposer(t));
      }
    };

    const STOP_RE = /^(stop|nillu|niruthu|niruthu da|quiet|silence|cancel|podhum|நிறுத்து|நில்லு|போதும்)[\s.!]*$/i;
    const handle = (raw) => {
      let t = String(raw || '').replace(/^\s*(hey|ok|hi)\s+/i, '');
      const m = t.match(WAKE_RE);
      if (m && t.indexOf(m[0]) < 14) t = t.slice(t.indexOf(m[0]) + m[0].length);   // drop a leading wake word
      t = t.replace(/^[\s,.:!-]+/, '').replace(/\s+/g, ' ').trim();
      if (t.length < 2) { backToListening(); return; }
      if (STOP_RE.test(t)) { stopSpeaking(); backToListening(); if (!vizhiOn) hideCap(); return; }
      stopRec();
      if (vizhiOn) setState('thinking', t); else showCap('💭 <b>Yosikiren…</b><span class="nb-heard">' + esc(t) + '</span>');
      askIntent(t, (o) => execute(o, t));
    };

    // every finished chat answer arrives here from the server (clean text, no tool cards)
    window.__nbSpeakAnswer = (text) => {
      text = String(text || '').trim();
      if (text) lastAnswer = text;
      if (vizhiOn) {
        pendingAnswer = false; clearTimeout(answerTimer);
        if (text) sayVizhi(text); else backToListening();
      } else if (speak && text) speakText(text);
      else if (pendingAnswer) { pendingAnswer = false; clearTimeout(answerTimer); hideCap(); }
    };

    // typed-command box (works with or without a microphone)
    const cmdIn = document.getElementById('nb-cmdin');
    const toggleCmd = () => {
      const open = cmdWrap.style.display === 'block';
      cmdWrap.style.display = open ? 'none' : 'block';
      if (!open && cmdIn) cmdIn.focus();
    };
    cmdBtn.onclick = toggleCmd;
    if (cmdIn) {
      cmdIn.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const v = (cmdIn.value || '').trim(); if (!v) return;
          cmdIn.value = ''; cmdWrap.style.display = 'none';
          handle(v);
        } else if (e.key === 'Escape') { cmdWrap.style.display = 'none'; }
      });
    }

    if (SR) {
      rec = new SR();
      rec.lang = micLang; rec.continuous = true; rec.interimResults = true; rec.maxAlternatives = 1;
      let buf = '', bufTimer = null;
      rec.onstart = () => { recActive = true; };
      rec.onaudiostart = () => { recActive = true; };
      rec.onresult = (ev) => {
        if (!vizhiOn || vState !== 'listening') return;
        let interim = '', fin = '';
        for (let i = ev.resultIndex; i < ev.results.length; i++) {
          const r = ev.results[i];
          if (r.isFinal) fin += r[0].transcript + ' '; else interim += r[0].transcript;
        }
        if (fin) buf += fin;
        const shown = (buf + ' ' + interim).trim();
        if (shown) { showCap(listenCap(shown.slice(-80))); bindTog(); }
        clearTimeout(bufTimer);
        if (!buf.trim()) return;
        // wait for a short pause so a sentence spoken in two breaths is handled as ONE command
        bufTimer = setTimeout(() => {
          const text = buf.trim(); buf = '';
          if (!vizhiOn || vState !== 'listening' || !text) return;
          if (wakeMode && !WAKE_RE.test(text) && Date.now() > followUntil) { showCap(listenCap()); bindTog(); return; }
          handle(text);
        }, interim ? 1500 : 950);
      };
      rec.onend = () => {
        recActive = false;
        if (vizhiOn && recWanted) setTimeout(() => { if (vizhiOn && recWanted && !recActive) { try { rec.lang = micLang; rec.start(); } catch (e) {} } }, 250);
      };
      rec.onerror = (e) => {
        recActive = false;
        const err = e && e.error;
        if (err === 'not-allowed' || err === 'service-not-allowed') {
          turnOff(); orb.title = 'Mic blocked — allow it in the browser';
          showCap('🎤 <b>Mic blocked.</b> Address bar-la 🔒 click panni Microphone → Allow, aprama orb-ah thirumba press pannu. (Illa ⌨️ button-la type pannu.)', 9000);
        } else if (err === 'audio-capture') {
          turnOff(); showCap('🎤 <b>Mic kedaikkala.</b> Laptop mic on-la irukka-nu paaru.', 7000);
        } else if (err === 'language-not-supported') {
          micLang = 'en-IN'; try { localStorage.setItem('nb-miclang', micLang); } catch (e2) {}
        }
        // 'no-speech' / 'network' / 'aborted' → onend restarts when wanted
      };
      // self-healing: if we should be listening but the engine died, start it again
      setInterval(() => { if (vizhiOn && recWanted && !recActive) { try { rec.lang = micLang; rec.start(); } catch (e) {} } }, 2500);

      orb.onclick = () => {
        if (vizhiOn && vState === 'speaking') { stopSpeaking(); backToListening(); return; }   // tap = interrupt and listen
        if (vizhiOn) { turnOff(); return; }
        vizhiOn = true; speak = true; spkBtn.style.background = '#c56a44';
        clickMode('Vizhi');                 // spoken answers use Vizhi's short, voice-friendly style
        sayVizhi(greeting());
      };
    } else {
      // No Web Speech API (Firefox, some in-app browsers, phone over plain-http LAN):
      // the orb opens the typed-command box so Vizhi still works.
      orb.title = 'Vizhi — voice not supported here, tap to type a command';
      orb.onclick = toggleCmd;
    }

    // ---------- one-shot mic (speech -> composer) ----------
    if (SR) {
      const rec1 = new SR();
      rec1.lang = micLang; rec1.interimResults = false; rec1.maxAlternatives = 1;
      let listening = false;
      micBtn.onclick = () => { if (listening) { rec1.stop(); return; } try { rec1.lang = micLang; rec1.start(); } catch(e) {} };
      rec1.onstart = () => { listening = true; micBtn.style.background = '#c56a44'; micBtn.textContent = '●'; };
      rec1.onend   = () => { listening = false; micBtn.style.background = ''; micBtn.textContent = '🎤'; };
      rec1.onerror = () => { listening = false; micBtn.style.background = ''; micBtn.textContent = '🎤'; };
      rec1.onresult = (ev) => {
        const text = ev.results[0][0].transcript;
        const ta = document.querySelector('#composer textarea');
        if (ta) { setVal(ta, (ta.value ? ta.value + ' ' : '') + text); ta.focus(); }
      };
    } else { micBtn.title = 'Voice input not supported in this browser'; micBtn.style.opacity = .5; }

    // ---------- Hacker Keyboard (Kali + Terminal command inputs only) ----------
    (function(){
      const SELS = ['#kali-in', '#term-in', '#kali-ai-in'];   // scoped to these command inputs
      const SYMS = ['-','_','/','\\','|','~','.',',','*','$','&','@','#','%','^','>','<',';',':','=','+','!','?','"',"'",'`','{','}','[',']','(',')'];
      // Kali tools + shell/coding tokens
      const TOKS = [['↹','\t'],
        ['sudo','sudo '],['nmap','nmap '],['sqlmap','sqlmap '],['msfconsole','msfconsole'],['hydra','hydra '],
        ['gobuster','gobuster '],['nikto','nikto '],['nuclei','nuclei '],['hashcat','hashcat '],['john','john '],
        ['netexec','netexec '],['nc','nc '],['wireshark','wireshark '],['aircrack-ng','aircrack-ng '],
        ['whoami','whoami'],['id','id'],['ifconfig','ifconfig'],['ping','ping '],['ssh','ssh '],['scp','scp '],
        ['curl','curl '],['wget','wget '],['grep','grep '],['awk','awk '],['sed','sed '],['git','git '],
        ['pip3','pip3 install '],['python3','python3 '],['chmod +x','chmod +x '],
        ['--','--'],['-p-','-p- '],['-sV','-sV '],['-sC','-sC '],['| grep',' | grep '],['./','./'],
        ['>',' > '],['>>',' >> '],['&&',' && '],['||',' || '],['cd','cd '],['ls -la','ls -la '],
        ['cat','cat '],['127.0.0.1','127.0.0.1']];
      let target = null, custom = [];
      try { custom = JSON.parse(localStorage.getItem('nb-hkb-custom') || '[]'); } catch(e) {}
      const saveCustom = () => { try { localStorage.setItem('nb-hkb-custom', JSON.stringify(custom)); } catch(e) {} };

      const isT = (el) => el && el.tagName === 'TEXTAREA' && SELS.some(s => el.closest(s));
      const setRange = (t,a,b,txt) => {
        const v = t.value, nv = v.slice(0,a) + txt + v.slice(b);
        const st = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
        st.call(t, nv); t.dispatchEvent(new Event('input',{bubbles:true}));
        t.selectionStart = t.selectionEnd = a + txt.length; t.focus();
      };
      const ins = (txt) => { if(!target) return; const s=target.selectionStart??target.value.length, e=target.selectionEnd??s; setRange(target,s,e,txt); };
      const move = (d) => { if(!target) return; const p=Math.max(0,(target.selectionStart||0)+d); target.selectionStart=target.selectionEnd=p; target.focus(); };
      const del = () => { if(!target) return; const s=target.selectionStart??0, e=target.selectionEnd??s; if(s===e&&s>0) setRange(target,s-1,s,''); else setRange(target,s,e,''); };
      const addCustom = () => { const t = prompt('Custom command / snippet (e.g. msfvenom -p ...):'); if(t && t.trim()){ custom.push(t.trim()); saveCustom(); buildTokens(); } };

      const bar = document.createElement('div'); bar.id = 'nb-hkb';
      bar.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:10001;background:#0b0f0a;'
        + 'border-top:1px solid #1f3d1f;padding:5px 6px calc(6px + env(safe-area-inset-bottom));display:none;'
        + 'box-shadow:0 -4px 16px rgba(0,0,0,.45)';
      const mkRow = () => { const r=document.createElement('div');
        r.style.cssText='display:flex;gap:5px;overflow-x:auto;scrollbar-width:none;padding:2px 0'; return r; };
      // key uses pointerdown + touchstart with preventDefault → works on iPhone, never blurs the input
      const key = (label,fn,w,hot) => { const k=document.createElement('button'); k.textContent=label;
        k.style.cssText='flex:0 0 auto;min-width:'+(w||34)+'px;height:38px;padding:0 9px;border-radius:7px;'
          +'border:1px solid '+(hot?'#d6552e':'#1f3d1f')+';background:'+(hot?'#2a160d':'#11180f')+';'
          +'color:'+(hot?'#ffb089':'#8ef5b0')+';font-family:ui-monospace,Menlo,monospace;font-size:14px;'
          +'cursor:pointer;-webkit-user-select:none;user-select:none;touch-action:manipulation;';
        const handler = e => { e.preventDefault(); e.stopPropagation(); fn(); };
        k.addEventListener('pointerdown', handler);
        k.addEventListener('touchstart', handler, {passive:false});   // iOS fallback
        return k; };
      const r1 = mkRow(), r2 = mkRow();   // r1 = controls + tokens, r2 = symbols
      bar.append(r1, r2); document.body.appendChild(bar);

      const buildTokens = () => {
        r1.innerHTML = '';
        r1.append(key('✕', ()=>hide(), 40));
        r1.append(key('◀', ()=>move(-1)));
        r1.append(key('▶', ()=>move(1)));
        r1.append(key('⌫', ()=>del()));
        r1.append(key('➕', ()=>addCustom(), 40, true));
        custom.forEach((c,i) => { const k=key(c, ()=>ins(c + (c.endsWith(' ')?'':' ')), Math.min(120, 30+c.length*8), true);
          k.addEventListener('contextmenu', e=>{ e.preventDefault(); if(confirm('Remove snippet?\n'+c)){ custom.splice(i,1); saveCustom(); buildTokens(); } });
          r1.append(k); });
        TOKS.forEach(([l,t]) => r1.append(key(l, ()=>ins(t), l.length>2?50:40)));
      };
      buildTokens();
      SYMS.forEach(s => r2.append(key(s, ()=>ins(s))));

      const reposition = () => { if(window.visualViewport){ const vp=window.visualViewport;
        bar.style.bottom = Math.max(0, window.innerHeight - vp.height - vp.offsetTop) + 'px'; } };
      const show = () => { bar.style.display='block'; reposition(); };
      const hide = () => { bar.style.display='none'; };
      if(window.visualViewport){ window.visualViewport.addEventListener('resize', reposition);
        window.visualViewport.addEventListener('scroll', reposition); }
      document.addEventListener('focusin', e => { if(isT(e.target)){ target=e.target; show(); } });
      document.addEventListener('focusout', () => { setTimeout(()=>{ if(!isT(document.activeElement)) hide(); }, 180); });
    })();

  } catch (e) { /* never break the page */ }
}
"""
