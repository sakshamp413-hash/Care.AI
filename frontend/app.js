/* Beta Bol — voice UI.
 *
 * Backend hooks (all on window and on window.BetaBol):
 *   startListening()                 ask for the mic, drive the orb from real mic volume, live captions
 *   stopListening()                  release the mic, orb back to idle
 *   playAIAudio(blob)                play an MP3/WAV blob (e.g. ElevenLabs) with the orb synced to it; resolves when done
 *   setOrbState(state)               'idle' | 'listening' | 'speaking'
 *   addMessage(role, text, opts)     role 'user' | 'ai'; opts { warning: boolean }
 *   BetaBol.onUserSpeech = async (text, lang) => {}   override this to send speech to your backend
 *
 * Until onUserSpeech is overridden, a local demo responder answers (and flags scam words).
 */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // ---------------------------------------------------------------- background contours
  (function drawContours() {
    const svg = $("contours");
    const w = window.innerWidth, h = window.innerHeight;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    let html = "";
    for (let r = 60; r < Math.hypot(w, h) * 1.1; r += 46) {
      html += `<circle cx="${-w * 0.08}" cy="${h * 1.06}" r="${r}"/>`;
    }
    svg.innerHTML = html;
  })();

  // ---------------------------------------------------------------- screens
  const state = { lang: "hi", paused: false, demoToken: 0 };

  function show(id) {
    document.querySelectorAll(".screen").forEach((s) => s.classList.toggle("active", s.id === id));
    document.body.classList.toggle("in-chat", id === "chat");
    window.scrollTo(0, 0);
    if (id === "chat") orbResize();
  }

  $("ctaBtn").addEventListener("click", () => {
    show("chat");
    runDemo();
  });
  $("backBtn").addEventListener("click", () => {
    endSession(false);
    show("hero");
  });

  $("langBtn").addEventListener("click", () => {
    state.lang = state.lang === "hi" ? "en" : "hi";
    document.querySelectorAll("#langBtn [data-lang]").forEach((s) => s.classList.toggle("on", s.dataset.lang === state.lang));
    if (recognition) recognition.lang = state.lang === "hi" ? "hi-IN" : "en-IN";
    console.log("[BetaBol] language:", state.lang);
  });

  // ---------------------------------------------------------------- messages + captions
  const SHIELD = '<svg class="i"><use href="#i-shield"/></svg>';

  function scrollChat() {
    const box = $("messages");
    requestAnimationFrame(() => box.scrollTo({ top: box.scrollHeight, behavior: reduceMotion.matches ? "auto" : "smooth" }));
  }

  function addMessage(role, text, opts = {}) {
    const box = $("messages");
    const el = document.createElement("div");
    const isUser = role === "user";
    el.className = `bubble ${isUser ? "user" : "ai"}${opts.warning ? " warning" : ""}`;
    const who = document.createElement("span");
    who.className = "who";
    if (opts.warning) who.innerHTML = `${SHIELD} Scam alert`;
    else who.textContent = isUser ? "Aap" : "Beta Bol";
    el.appendChild(who);
    el.appendChild(document.createTextNode(text));
    box.appendChild(el);
    scrollChat();
    if (opts.warning && navigator.vibrate) navigator.vibrate([300, 120, 300]);
    console.log("[BetaBol] addMessage", role, opts.warning ? "(warning)" : "", text);
    return el;
  }

  function addSystem(text) {
    const el = document.createElement("div");
    el.className = "sys";
    el.innerHTML = '<svg class="i"><use href="#i-check"/></svg>';
    el.appendChild(document.createTextNode(text));
    $("messages").appendChild(el);
    scrollChat();
  }

  function setCaption(text, dim = false) {
    $("caption").textContent = text;
    $("caption").classList.toggle("dim", dim);
  }

  async function typeCaption(text, token, msPerChar = 38) {
    if (reduceMotion.matches) { setCaption(text); return; }
    for (let i = 1; i <= text.length; i++) {
      if (token !== state.demoToken) return;
      while (state.paused) await sleep(120);
      setCaption(text.slice(0, i));
      await sleep(msPerChar);
    }
  }

  // ---------------------------------------------------------------- audio graph
  let audioCtx = null, micStream = null, micAnalyser = null, micSource = null;
  let playAnalyser = null, currentAudio = null, recognition = null;
  const buf = new Uint8Array(1024);

  function ctx() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === "suspended" && !state.paused) audioCtx.resume();
    return audioCtx;
  }

  function rms(analyser) {
    analyser.getByteTimeDomainData(buf);
    let sum = 0;
    for (let i = 0; i < analyser.fftSize; i++) { const v = (buf[i] - 128) / 128; sum += v * v; }
    return Math.sqrt(sum / analyser.fftSize);
  }

  // ---------------------------------------------------------------- hooks
  async function startListening() {
    console.log("[BetaBol] startListening()");
    if (micStream) { setOrbState("listening"); return true; }
    try {
      micStream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
    } catch (err) {
      console.warn("[BetaBol] mic permission denied", err);
      setCaption("Mic ki ijaazat nahi mili. Browser mein mic allow kijiye.", true);
      return false;
    }
    const ac = ctx();
    micSource = ac.createMediaStreamSource(micStream);
    micAnalyser = ac.createAnalyser();
    micAnalyser.fftSize = 1024;
    micSource.connect(micAnalyser);
    setOrbState("listening");
    setCaption("Sun raha hoon… boliye", true);
    startRecognition();
    return true;
  }

  function stopListening() {
    console.log("[BetaBol] stopListening()");
    if (recognition) { recognition.onend = null; try { recognition.abort(); } catch {} recognition = null; }
    if (micStream) micStream.getTracks().forEach((t) => t.stop());
    if (micSource) micSource.disconnect();
    micStream = micSource = micAnalyser = null;
    if (orb.state === "listening") setOrbState("idle");
  }

  async function playAIAudio(blob) {
    console.log("[BetaBol] playAIAudio()", blob && blob.size, "bytes");
    stopAudio();
    const ac = ctx();
    if (!playAnalyser) {
      playAnalyser = ac.createAnalyser();
      playAnalyser.fftSize = 1024;
      playAnalyser.connect(ac.destination);
    }
    const url = URL.createObjectURL(blob);
    const el = new Audio(url);
    currentAudio = el;
    ac.createMediaElementSource(el).connect(playAnalyser);
    setOrbState("speaking");
    await el.play();
    return new Promise((resolve) => {
      el.onended = el.onerror = () => {
        URL.revokeObjectURL(url);
        if (currentAudio === el) currentAudio = null;
        setOrbState(micStream ? "listening" : "idle");
        resolve();
      };
    });
  }

  function stopAudio() {
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }
    if ("speechSynthesis" in window) speechSynthesis.cancel();
  }

  function setOrbState(s) {
    if (!["idle", "listening", "speaking"].includes(s)) return;
    orb.state = s;
    $("orbBtn").setAttribute("aria-label",
      s === "listening" ? "Sun raha hoon. Rokne ke liye dabaiye" : s === "speaking" ? "Beta Bol bol raha hai" : "Bolne ke liye orb dabaiye");
    if (reduceMotion.matches) drawOrb(performance.now());
  }

  // ---------------------------------------------------------------- speech recognition (live captions)
  function startRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    recognition = new SR();
    recognition.lang = state.lang === "hi" ? "hi-IN" : "en-IN";
    recognition.interimResults = true;
    recognition.continuous = true;
    recognition.onresult = (e) => {
      if (orb.state === "speaking") return; // don't transcribe our own voice
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) {
          const text = r[0].transcript.trim();
          if (text) handleUserSpeech(text);
        } else interim += r[0].transcript;
      }
      if (interim) setCaption(interim);
    };
    recognition.onerror = (e) => console.warn("[BetaBol] recognition", e.error);
    recognition.onend = () => { if (micStream && !state.paused) try { recognition.start(); } catch {} };
    try { recognition.start(); } catch {}
  }

  async function handleUserSpeech(text) {
    addMessage("user", text);
    setCaption(text);
    try {
      await api.onUserSpeech(text, state.lang);
    } catch (err) {
      console.error("[BetaBol] onUserSpeech failed", err);
      addMessage("ai", "Maaf kijiye, thodi dikkat aa gayi. Phir se boliye.");
    }
  }

  // Demo responder used until the backend overrides BetaBol.onUserSpeech.
  const SCAM_WORDS = /\b(otp|kyc|lottery|lucky draw|prize|anydesk|teamviewer|cbi|police|arrest|pin|cashback|refund)\b|ओटीपी|लॉटरी|केवाईसी|पिन|इनाम/i;
  async function demoResponder(text) {
    const scam = SCAM_WORDS.test(text);
    const reply = scam
      ? "Rukiye! Ye scam ho sakta hai. Bank ya police kabhi OTP, PIN ya paise nahi maangte. Call kaat dijiye — maine aapke bete ko bata diya hai."
      : "Theek hai. Apne phone ki screen ka photo bhejiye, main ek-ek kadam bataunga.";
    await speakLocal(reply);
    addMessage("ai", reply, { warning: scam });
    if (scam) addSystem("Rahul ko WhatsApp alert bheja gaya");
  }

  // Browser voice + simulated orb amplitude (stand-in for ElevenLabs audio).
  function speakLocal(text) {
    return new Promise((resolve) => {
      setOrbState("speaking");
      setCaption(text);
      const done = () => { setOrbState(micStream ? "listening" : "idle"); resolve(); };
      if (!("speechSynthesis" in window)) return setTimeout(done, 1800);
      const u = new SpeechSynthesisUtterance(text);
      u.lang = state.lang === "hi" ? "hi-IN" : "en-IN";
      u.rate = 0.95;
      u.onend = u.onerror = done;
      speechSynthesis.speak(u);
    });
  }

  // ---------------------------------------------------------------- demo conversation
  const DEMO = [
    { role: "ai", text: "Namaste! Aaj kis cheez mein madad karun?" },
    { role: "user", text: "Bank wale ka call aaya hai, OTP maang rahe hain." },
    { role: "ai", warning: true, text: "Rukiye! Bank kabhi OTP nahi maangta. Ye scam ho sakta hai. Call kaat dijiye — maine aapke bete ko bata diya hai." },
  ];

  async function runDemo() {
    const token = ++state.demoToken;
    $("messages").innerHTML = "";
    setOrbState("idle");
    setCaption("");
    await sleep(500);
    for (const m of DEMO) {
      if (token !== state.demoToken) return;
      setOrbState(m.role === "ai" ? "speaking" : "listening");
      orb.simulate = true;
      await typeCaption(m.text, token);
      if (token !== state.demoToken) return;
      await sleep(250);
      addMessage(m.role, m.text, { warning: m.warning });
      orb.simulate = false;
      setOrbState("idle");
      await sleep(m.warning ? 400 : 700);
    }
    if (token !== state.demoToken) return;
    addSystem("Rahul ko WhatsApp alert bheja gaya");
    await sleep(900);
    if (token === state.demoToken) setCaption("Ab aap boliye — orb dabaiye", true);
  }

  // ---------------------------------------------------------------- controls
  $("orbBtn").addEventListener("click", async () => {
    state.demoToken++; // tapping the orb takes over from the demo
    orb.simulate = false;
    if (micStream) { stopListening(); setCaption("Orb dabaiye aur boliye", true); }
    else await startListening();
  });

  $("pauseBtn").addEventListener("click", () => {
    state.paused = !state.paused;
    const btn = $("pauseBtn");
    btn.classList.toggle("paused", state.paused);
    btn.innerHTML = `<svg class="i"><use href="#i-${state.paused ? "play" : "pause"}"/></svg>`;
    btn.setAttribute("aria-label", state.paused ? "Phir shuru kijiye" : "Rokiye");
    if (audioCtx) state.paused ? audioCtx.suspend() : audioCtx.resume();
    if (currentAudio) state.paused ? currentAudio.pause() : currentAudio.play();
    if ("speechSynthesis" in window) state.paused ? speechSynthesis.pause() : speechSynthesis.resume();
    if (recognition) state.paused ? recognition.stop() : (() => { try { recognition.start(); } catch {} })();
    console.log("[BetaBol] paused:", state.paused);
  });

  function endSession(withCaption = true) {
    state.demoToken++;
    orb.simulate = false;
    stopAudio();
    stopListening();
    if (state.paused) $("pauseBtn").click();
    setOrbState("idle");
    if (withCaption) setCaption("Baat khatam hui. Orb dabakar phir se boliye.", true);
  }
  $("endBtn").addEventListener("click", () => endSession(true));

  // ---------------------------------------------------------------- ORB (canvas)
  const canvas = $("orb");
  const g = canvas.getContext("2d");
  const SIZE = 264, R = 110;
  const orb = { state: "idle", level: 0, simulate: false, phase: 0, last: 0 };

  function orbResize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = SIZE * dpr;
    canvas.height = SIZE * dpr;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    drawOrb(performance.now());
  }

  function targetLevel(t) {
    if (state.paused) return 0;
    if (orb.state === "listening" && micAnalyser) return Math.min(1, rms(micAnalyser) * 5);
    if (orb.state === "speaking" && playAnalyser && currentAudio) return Math.min(1, rms(playAnalyser) * 4);
    if (orb.simulate || orb.state === "speaking") {
      const s = orb.state === "speaking" ? 1 : 0.6;
      return s * (0.25 + 0.45 * Math.abs(Math.sin(t * 7.3) * Math.sin(t * 2.9 + 1)));
    }
    return 0;
  }

  function blobPath(cx, cy, r, t, wob, seed) {
    g.beginPath();
    const N = 72;
    for (let i = 0; i <= N; i++) {
      const a = (i / N) * Math.PI * 2;
      const d = r * (1 + wob * (0.55 * Math.sin(3 * a + t * 1.3 + seed) +
                                0.3 * Math.sin(5 * a - t * 1.7 + seed * 2) +
                                0.15 * Math.sin(2 * a + t * 0.8 + seed * 3)));
      const x = cx + Math.cos(a) * d, y = cy + Math.sin(a) * d;
      i ? g.lineTo(x, y) : g.moveTo(x, y);
    }
    g.closePath();
  }

  function glow(x, y, r, color, alpha) {
    const grad = g.createRadialGradient(x, y, 0, x, y, r);
    grad.addColorStop(0, color.replace("A", alpha));
    grad.addColorStop(1, color.replace("A", 0));
    g.fillStyle = grad;
    g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
  }

  function drawOrb(now) {
    const t = now / 1000;
    const dt = Math.min(0.05, orb.last ? t - orb.last : 0.016);
    orb.last = t;
    const lvTarget = targetLevel(t);
    orb.level += (lvTarget - orb.level) * (lvTarget > orb.level ? 0.35 : 0.08);
    const lv = orb.level;

    const speed = orb.state === "speaking" ? 1.9 : orb.state === "listening" ? 0.9 : 0.35;
    if (!state.paused) orb.phase += dt * speed * (1 + lv * 1.5);
    const p = orb.phase;
    const breathe = orb.state === "idle" ? Math.sin(t * 1.2) * 0.025 : 0;
    const r = R * (1 + breathe + lv * 0.06);
    const wob = (orb.state === "idle" ? 0.035 : 0.05) + lv * 0.16;
    const cx = SIZE / 2, cy = SIZE / 2;

    g.clearRect(0, 0, SIZE, SIZE);

    // outer halo
    glow(cx, cy, r * 1.18, "rgba(0,200,255,A)", 0.22 + lv * 0.25);

    // listening ripples
    if (orb.state === "listening" && !reduceMotion.matches) {
      for (let k = 0; k < 3; k++) {
        const q = (t * 0.55 + k / 3) % 1;
        g.strokeStyle = `rgba(0,200,255,${(1 - q) * (0.25 + lv * 0.6)})`;
        g.lineWidth = 2;
        g.beginPath(); g.arc(cx, cy, r * (1 + q * 0.18), 0, Math.PI * 2); g.stroke();
      }
    }

    // fluid body
    g.save();
    blobPath(cx, cy, r, p, wob, 0);
    g.clip();
    const base = g.createRadialGradient(cx, cy, 0, cx, cy, r);
    base.addColorStop(0, "#0B2A4A");
    base.addColorStop(1, "#02060C");
    g.fillStyle = base;
    g.fillRect(0, 0, SIZE, SIZE);

    g.globalCompositeOperation = "lighter";
    if ("filter" in g) g.filter = "blur(12px)";
    const swirl = orb.state === "speaking" ? 1.4 : 1;
    const orbit = r * 0.38;
    glow(cx + Math.cos(p * 0.9 * swirl) * orbit, cy + Math.sin(p * 1.1 * swirl) * orbit, r * 0.85, "rgba(0,200,255,A)", 0.85);
    glow(cx + Math.cos(p * 0.7 * swirl + 2.2) * orbit, cy + Math.sin(p * 0.8 * swirl + 2.2) * orbit, r * 0.9, "rgba(26,92,255,A)", 0.95);
    glow(cx + Math.cos(-p * 1.2 * swirl + 4.1) * orbit * 1.1, cy + Math.sin(-p * 1.0 * swirl + 4.1) * orbit * 1.1, r * 0.55, "rgba(255,92,154,A)", 0.7 + lv * 0.2);
    glow(cx, cy, r * 0.35, "rgba(160,235,255,A)", 0.15 + lv * 0.35);
    if ("filter" in g) g.filter = "none";
    g.globalCompositeOperation = "source-over";

    // smoky dark edge
    const edge = g.createRadialGradient(cx, cy, r * 0.55, cx, cy, r * 1.05);
    edge.addColorStop(0, "rgba(2,6,12,0)");
    edge.addColorStop(0.75, "rgba(2,6,12,.45)");
    edge.addColorStop(1, "rgba(2,6,12,.95)");
    g.fillStyle = edge;
    g.fillRect(0, 0, SIZE, SIZE);

    // glassy highlight
    glow(cx - r * 0.35, cy - r * 0.42, r * 0.45, "rgba(255,255,255,A)", 0.18);
    g.restore();

    // rim
    blobPath(cx, cy, r, p, wob, 0);
    g.strokeStyle = `rgba(120,200,255,${0.18 + lv * 0.3})`;
    g.lineWidth = 1.2;
    g.stroke();
  }

  function loop(now) {
    drawOrb(now);
    if (!reduceMotion.matches) requestAnimationFrame(loop);
  }
  reduceMotion.addEventListener && reduceMotion.addEventListener("change", () => !reduceMotion.matches && requestAnimationFrame(loop));
  orbResize();
  requestAnimationFrame(loop);

  // ---------------------------------------------------------------- public API
  const api = {
    startListening, stopListening, playAIAudio, setOrbState, addMessage,
    onUserSpeech: demoResponder,
  };
  window.BetaBol = api;
  Object.assign(window, { startListening, stopListening, playAIAudio, setOrbState, addMessage });
  console.log("[BetaBol] hooks ready: startListening, stopListening, playAIAudio, setOrbState, addMessage, BetaBol.onUserSpeech");
})();
