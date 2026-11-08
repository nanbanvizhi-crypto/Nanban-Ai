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
    try { saved = localStorage.getItem('nb-theme') || 'light'; } catch(e) {}
    applyTheme(saved);

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
    const showCap = (h) => { cap.innerHTML = h; cap.style.display = 'block'; };
    const hideCap = () => { cap.style.display = 'none'; };

    thmBtn.onclick = () => applyTheme(document.body.classList.contains('dark') ? 'light' : 'dark');

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;

    // ---------- speech synthesis (shared, natural voice) ----------
    let speak = false;
    const spoken = new Set();
    let bestVoice = null;
    const pickVoice = () => {
      if (!window.speechSynthesis) return;
      const vs = window.speechSynthesis.getVoices() || [];
      bestVoice =
        vs.find(v => /en-IN/i.test(v.lang) && /google|female|neural|natural/i.test(v.name)) ||
        vs.find(v => /en-IN/i.test(v.lang)) ||
        vs.find(v => /en-GB/i.test(v.lang) && /google|female|neural/i.test(v.name)) ||
        vs.find(v => /en-GB/i.test(v.lang)) ||
        vs.find(v => /en-US/i.test(v.lang) && /google|female|neural/i.test(v.name)) ||
        vs.find(v => /^en/i.test(v.lang)) || vs[0] || null;
    };
    if (window.speechSynthesis) { pickVoice(); window.speechSynthesis.onvoiceschanged = pickVoice; }

    const cleanForSpeech = (t) => (t || '')
      .replace(/```[\s\S]*?```/g, '. code block. ')
      .replace(/`([^`]+)`/g, '$1')
      .replace(/\*\*([^*]+)\*\*/g, '$1').replace(/\*([^*]+)\*/g, '$1')
      .replace(/^#{1,6}\s*/gm, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/https?:\/\/\S+/g, ' link ')
      .replace(/[>_~|•]/g, ' ').replace(/\s+/g, ' ').trim();

    const speakText = (text, hooks) => {
      hooks = hooks || {};
      if (!window.speechSynthesis) { if (hooks.onEnd) hooks.onEnd(); return; }
      let say = cleanForSpeech(text);
      let truncated = false;
      if (say.length > 850) { say = say.slice(0, 850); truncated = true; }
      if (truncated) say += '. Mel details screen la irukku.';
      const u = new SpeechSynthesisUtterance(say);
      u.lang = (bestVoice && bestVoice.lang) || 'en-IN';
      if (bestVoice) u.voice = bestVoice;
      u.rate = 1.03; u.pitch = 1.0;
      if (hooks.onStart) u.onstart = hooks.onStart;
      if (hooks.onEnd)   u.onend = hooks.onEnd;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(u);
    };

    spkBtn.onclick = () => {
      speak = !speak;
      spkBtn.style.background = speak ? '#c56a44' : '';
      if (!speak && window.speechSynthesis) window.speechSynthesis.cancel();
    };

    // ========================= Vizhi =========================
    let vizhiOn = false, vState = 'idle', rec = null, recActive = false, followUntil = 0;
    let wakeMode = true;
    try { wakeMode = localStorage.getItem('nb-wake') !== '0'; } catch(e) {}
    const pick = (a) => a[Math.floor(Math.random() * a.length)];
    const greeting = () => {
      const h = new Date().getHours();
      const g = h < 12 ? 'Kaalai vanakkam' : (h < 16 ? 'Nalla madhiyam' : (h < 20 ? 'Maalai vanakkam' : 'Vanakkam'));
      return g + ', nanba. ' + pick([
        'Sollu, enna help venum?', 'Vizhi ready. Sollu.', 'Naan ketten, sollu.',
        'Enna pannalaam indha neram?', 'Un kannu naan, Vizhi — sollu, pannidren.']);
    };
    const THINKING = ['💭 <b>Yosikiren…</b>', '💭 <b>Konja second, paakuren…</b>', '💭 <b>Thinking…</b>', '💭 <b>Processing pannuren…</b>'];
    const DONE_TAB = (n) => pick([n + ' open pannitten, nanba.', n + ' ready. Paaru.', n + ' ponnaacho!', 'Indhaa, ' + n + ' open.']);
    const GRAD = {
      idle:'radial-gradient(circle at 50% 38%, #4fd1ff, #1b6fd6 60%, #0b3a8a)',
      listening:'radial-gradient(circle at 50% 38%, #6ee7ff, #0ea5e9 60%, #0369a1)',
      thinking:'radial-gradient(circle at 50% 38%, #ffd27a, #f59e0b 60%, #b45309)',
      speaking:'radial-gradient(circle at 50% 38%, #8ef5b0, #22c55e 60%, #15803d)',
    };
    const listenCap = (heard) => {
      const tog = `<span id="nb-wtog" style="cursor:pointer;color:#6ee7ff;text-decoration:underline">[wake-word: ${wakeMode ? 'ON' : 'OFF'}]</span>`;
      const hint = wakeMode ? 'Say <b>"Vizhi…"</b> then your command'
                            : 'Say anything — "open Kali", "draw a cat"';
      const h = heard ? `<span class="nb-heard">heard: ${heard}</span>` : '';
      return `🎙️ <b>Listening…</b> ${tog}<br><span style="opacity:.8">${hint}</span>${h}`;
    };
    const bindTog = () => { const w = document.getElementById('nb-wtog'); if (w) w.onclick = () => {
      wakeMode = !wakeMode; try { localStorage.setItem('nb-wake', wakeMode ? '1' : '0'); } catch(e) {}
      if (vState === 'listening') { showCap(listenCap()); bindTog(); } }; };
    const setState = (s, heard) => {
      vState = s;
      orb.style.background = GRAD[s] || GRAD.idle;
      orb.classList.toggle('nb-pulse', s === 'listening' || s === 'speaking');
      orb.classList.toggle('nb-breath', s === 'listening');
      if (s === 'idle') { hideCap(); return; }
      showCap(s === 'listening' ? listenCap(heard) : (s === 'thinking' ? pick(THINKING) : '🔊 <b>Speaking…</b>'));
      if (s === 'listening') bindTog();
    };
    const sayVizhi = (text) => speakText(text, {
      onStart: () => { if (vizhiOn) { setState('speaking'); try { rec.stop(); } catch(e) {} } },
      onEnd:   () => { if (vizhiOn) { followUntil = Date.now() + 9000; setState('listening'); try { rec.start(); } catch(e) {} } },
    });

    // ---- app-control helpers ----
    const clickTab = (name) => {
      const t = Array.from(document.querySelectorAll('[role="tab"], button')).find(el =>
        (el.innerText || '').toLowerCase().includes(name.toLowerCase())
        && (el.getAttribute('role') === 'tab' || (el.className || '').includes('tab')));
      if (t) { t.click(); return true; } return false;
    };
    const clickMode = (label) => {
      const l = Array.from(document.querySelectorAll('#modes label')).find(el =>
        (el.innerText || '').toLowerCase().includes(label.toLowerCase()));
      if (l) { l.click(); return true; } return false;
    };
    const setVal = (ta, v) => {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      setter.call(ta, v); ta.dispatchEvent(new Event('input', { bubbles: true }));
    };
    const btnByText = (re) => Array.from(document.querySelectorAll('button')).find(b => re.test(b.innerText || ''));
    const submitComposer = (text) => {
      const ta = document.querySelector('#composer textarea');
      if (!ta) return;
      setVal(ta, text);
      setTimeout(() => {
        let btn = document.querySelector('#composer button.submit-button') || document.querySelector('#composer button[aria-label*="ubmit"]');
        if (!btn) {
          const c = Array.from(document.querySelectorAll('#composer button')).filter(b => b.querySelector('svg') && !/upload|image/i.test(b.getAttribute('aria-label') || ''));
          btn = c[c.length - 1];
        }
        if (btn) btn.click();
        else ta.dispatchEvent(new KeyboardEvent('keydown', { key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true }));
      }, 70);
    };
    const TABS = [
      {k:['india lab','india','lab'], n:'India Lab'},
      {k:['image','images','padam','photo','picture'], n:'Images'},
      {k:['terminal','command line'], n:'Terminal'},
      {k:['security'], n:'Security'},
      {k:['kali','linux','hacking tool'], n:'Kali'},
      {k:['learn','study','practice','sandbox'], n:'Learn'},
      {k:['admin','settings','setting','automation'], n:'Admin'},
      {k:['chat','conversation'], n:'Chat'},
    ];
    const MODES = [
      {k:['coding','code','program'], n:'Coding'}, {k:['writing','write'], n:'Writing'},
      {k:['research'], n:'Research'}, {k:['study'], n:'Study'}, {k:['business'], n:'Business'},
      {k:['security tutor','security mode','tutor'], n:'Security Tutor'}, {k:['computer'], n:'Computer'},
      {k:['assistant','personal','default','normal'], n:'Personal Assistant'},
    ];
    const NAVVERB = /\b(open|go to|goto|show|switch|take me|move to|kaattu|kaami|kaamu|po|poo|thirum)\b/i;

    const routeCommand = (t) => {
      const low = t.toLowerCase().trim();
      if (/^(stop|quiet|silence|mute|nillu|niruthu|cancel|summa iru)\b/.test(low)) {
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        if (vizhiOn) setState('listening'); return true;
      }
      if (/\b(vizhi off|jarvis off|stop listening|sleep|off pannu|podhum)\b/.test(low)) {
        vizhiOn = false; setState('idle'); try { rec.stop(); } catch(e) {}
        if (window.speechSynthesis) window.speechSynthesis.cancel(); return true;
      }
      if (/\b(repeat|again|marubadi|thirumba sollu|say again|read again)\b/.test(low)) {
        const bots = document.querySelectorAll('#chat .bot');
        if (bots.length) sayVizhi((bots[bots.length-1].innerText || '').trim()); return true;
      }
      if (/\b(dark mode|night mode|dark pannu|dark theme|iruttu)\b/.test(low)) { applyTheme('dark'); sayVizhi('Dark mode on'); return true; }
      if (/\b(light mode|day mode|light pannu|light theme|velicham)\b/.test(low)) { applyTheme('light'); sayVizhi('Light mode on'); return true; }
      if (/\b(new chat|pudhu chat|pudusa|fresh chat|clear chat)\b/.test(low)) {
        const nc = document.getElementById('new-chat'); if (nc) { nc.click(); sayVizhi('New chat ready'); return true; }
      }
      const mi = low.match(/(?:draw|image of|picture of|generate image of|create image of|create a image of|padam\s*podu|photo of)\s+(.+)/i);
      if (mi && mi[1]) {
        const subj = mi[1].trim(); clickTab('Images');
        setTimeout(() => { const ta = document.querySelector('#img-prompt textarea'); if (ta) { setVal(ta, subj); const b = btnByText(/create image/i); if (b) b.click(); } }, 650);
        sayVizhi('Image ready pannuren: ' + subj); return true;
      }
      if (/\b(install arsenal|install tools|install everything|full arsenal|ella tools install)\b/.test(low)) {
        clickTab('Kali'); setTimeout(() => { const b = btnByText(/install full arsenal/i); if (b) b.click(); }, 650);
        sayVizhi('Installing the Kali arsenal'); return true;
      }
      const mk2 = low.match(/\b(scan|run|nmap|check ports|port scan)\b\s*(.*)/i);
      if (mk2) {
        clickTab('Kali'); const cmd = t;
        setTimeout(() => { const ta = document.querySelector('#kali-ai-in textarea'); if (ta) { setVal(ta, cmd); const b = btnByText(/run with ai/i); if (b) b.click(); } }, 650);
        sayVizhi('Kali-la pannuren'); return true;
      }
      if (/\b(mode|tutor)\b/.test(low)) {
        for (const m of MODES) if (m.k.some(k => low.includes(k))) { if (clickMode(m.n)) { sayVizhi(m.n + ' mode'); return true; } }
      }
      if (NAVVERB.test(low)) {
        for (const tb of TABS) if (tb.k.some(k => low.includes(k))) { if (clickTab(tb.n)) { sayVizhi(DONE_TAB(tb.n)); return true; } }
      }
      return false;
    };

    const handle = (t) => {
      t = t.replace(/\b(hey\s+|ok\s+)?(vizhi|jarvis|nanban|friend)\b[,\.\s]*/ig, ' ').replace(/\s+/g, ' ').trim();
      if (t.length < 2) { if (vizhiOn) setState('listening'); return; }
      if (routeCommand(t)) return;
      setState('thinking');
      submitComposer(t);
    };

    // typed-command fallback wiring (works with or without speech support)
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
          const v = (cmdIn.value || '').trim();
          if (!v) return;
          cmdIn.value = ''; cmdWrap.style.display = 'none';
          handle(v);
        } else if (e.key === 'Escape') { cmdWrap.style.display = 'none'; }
      });
    }

    if (SR) {
      rec = new SR();
      rec.lang = 'en-IN'; rec.continuous = true; rec.interimResults = true; rec.maxAlternatives = 1;
      rec.onstart = () => { recActive = true; };
      rec.onaudiostart = () => { recActive = true; };
      rec.onresult = (ev) => {
        if (!vizhiOn || vState === 'speaking' || vState === 'thinking') return;
        let interim = '', finalTxt = '';
        for (let i = ev.resultIndex; i < ev.results.length; i++) {
          const r = ev.results[i];
          if (r.isFinal) finalTxt += r[0].transcript; else interim += r[0].transcript;
        }
        if (interim && vState === 'listening') showCap(listenCap(interim.trim().slice(0, 60)));
        const raw = (finalTxt || '').trim();
        if (!raw) return;
        const hasWake = /\b(vizhi|jarvis|nanban|friend)\b/i.test(raw) || /^(hey|ok)\s/i.test(raw);
        const inFollow = Date.now() < followUntil;
        if (wakeMode && !hasWake && !inFollow) { if (vState === 'listening') showCap(listenCap()); return; }
        handle(raw);
      };
      rec.onend = () => { recActive = false; if (vizhiOn && vState !== 'speaking') { try { rec.start(); } catch(e) {} } };
      rec.onerror = (e) => {
        recActive = false;
        if (e && e.error === 'not-allowed') { vizhiOn = false; setState('idle'); orb.title = 'Mic blocked — allow it in the browser'; }
        // 'no-speech' / 'network' / 'aborted' → let onend restart
      };

      // self-healing watchdog: if we should be listening but recognition died, restart it
      setInterval(() => {
        if (vizhiOn && (vState === 'listening') && !recActive) { try { rec.start(); } catch(e) {} }
      }, 3000);

      orb.onclick = () => {
        vizhiOn = !vizhiOn;
        if (vizhiOn) {
          speak = true; spkBtn.style.background = '#c56a44';
          clickMode('Vizhi');   // give spoken answers Vizhi's warm personality
          setState('listening');
          try { rec.start(); } catch(e) {}
          speakText(greeting());
        } else {
          setState('idle'); try { rec.stop(); } catch(e) {}
          if (window.speechSynthesis) window.speechSynthesis.cancel();
        }
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
      rec1.lang = 'en-IN'; rec1.interimResults = false; rec1.maxAlternatives = 1;
      let listening = false;
      micBtn.onclick = () => { if (listening) { rec1.stop(); return; } try { rec1.start(); } catch(e) {} };
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

    // ---------- read answers aloud; drive Vizhi states + follow-up ----------
    let timer = null;
    const sayLatest = () => {
      if (!speak || !window.speechSynthesis) { if (vizhiOn) setState('listening'); return; }
      const bots = document.querySelectorAll('#chat .bot');
      if (!bots.length) { if (vizhiOn) setState('listening'); return; }
      const text = (bots[bots.length - 1].innerText || '').trim();
      if (!text || spoken.has(text)) { if (vizhiOn && vState === 'thinking') setState('listening'); return; }
      spoken.add(text);
      speakText(text, {
        onStart: () => { if (vizhiOn) { setState('speaking'); try { rec.stop(); } catch(e) {} } },
        onEnd:   () => { if (vizhiOn) { followUntil = Date.now() + 9000; setState('listening'); try { rec.start(); } catch(e) {} } },
      });
    };
    const chat = document.querySelector('#chat');
    if (chat) {
      const obs = new MutationObserver(() => { clearTimeout(timer); timer = setTimeout(sayLatest, 1100); });
      obs.observe(chat, { childList: true, subtree: true, characterData: true });
    }
  } catch (e) { /* never break the page */ }
}
"""
