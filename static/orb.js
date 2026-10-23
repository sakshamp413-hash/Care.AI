/* Beta Bol voice orb — a read-only observer. It never changes app behaviour.
 * States (class on #bb-orb): is-alert > is-speaking > is-thinking > is-idle.
 *  - speaking: media play/pause/ended events + polling speechSynthesis.speaking (browser voice)
 *  - thinking: a /api/guide request is pending (transparent fetch wrapper, same promise returned)
 *  - alert:    the #scam screen has class "show" (MutationObserver)
 * No getUserMedia, no createMediaElementSource: audio is never rerouted.
 * Everything is wrapped in try/catch; on any failure the orb just stays idle.
 */
(function () {
  "use strict";
  try {
    var host = document.getElementById("bb-orb");
    if (!host) return;

    var LABELS = { idle: "तैयार हूँ", thinking: "देख रहे हैं…", speaking: "बोल रहे हैं", alert: "रुकिए! खतरा" };
    var STATES = ["is-idle", "is-thinking", "is-speaking", "is-alert"];
    var playing = [];
    var flags = { synth: false, pending: 0, alert: false };
    var current = "";

    host.setAttribute("aria-hidden", "true");
    host.innerHTML =
      '<div class="bb-orb"><span class="bb-l1"></span><span class="bb-l2"></span><span class="bb-l3"></span>' +
      '<span class="bb-edge"></span><span class="bb-shine"></span></div><div class="bb-label"></div>';
    var label = host.querySelector(".bb-label");

    function render() {
      try {
        var s = flags.alert ? "alert" : (playing.length || flags.synth) ? "speaking" : flags.pending > 0 ? "thinking" : "idle";
        if (s === current) return;
        current = s;
        for (var i = 0; i < STATES.length; i++) host.classList.remove(STATES[i]);
        host.classList.add("is-" + s);
        if (label) label.textContent = LABELS[s];
      } catch (e) { /* stay as is */ }
    }

    // ---- speaking: audio elements ----
    function onMedia(e) {
      try {
        var el = e && e.target;
        if (!el || typeof HTMLMediaElement === "undefined" || !(el instanceof HTMLMediaElement)) return;
        var idx = playing.indexOf(el);
        if (e.type === "playing" || e.type === "play") { if (idx === -1) playing.push(el); }
        else if (idx !== -1) playing.splice(idx, 1);
        render();
      } catch (err) { /* ignore */ }
    }
    var MEDIA_EVENTS = ["play", "playing", "pause", "ended", "emptied", "error", "abort"];
    try {
      for (var i = 0; i < MEDIA_EVENTS.length; i++) document.addEventListener(MEDIA_EVENTS[i], onMedia, true);
    } catch (e) { /* ignore */ }

    // `new Audio()` elements are not in the DOM, so their events never reach document.
    // Observe them by attaching listeners when play() is called; the original play()
    // runs untouched and its exact return value is passed back.
    try {
      if (typeof HTMLMediaElement !== "undefined" && HTMLMediaElement.prototype.play) {
        var origPlay = HTMLMediaElement.prototype.play;
        HTMLMediaElement.prototype.play = function () {
          var result = origPlay.apply(this, arguments);
          try {
            if (!this.__bbOrbWatched) {
              this.__bbOrbWatched = true;
              for (var j = 0; j < MEDIA_EVENTS.length; j++) this.addEventListener(MEDIA_EVENTS[j], onMedia);
            }
          } catch (e) { /* ignore */ }
          return result;
        };
      }
    } catch (e) { /* ignore */ }

    // ---- speaking: browser Hindi voice fallback ----
    try {
      setInterval(function () {
        try {
          var ss = window.speechSynthesis;
          flags.synth = !!(ss && ss.speaking && !ss.paused);
          render();
        } catch (e) { /* ignore */ }
      }, 300);
    } catch (e) { /* ignore */ }

    // ---- thinking: pending /api/guide request ----
    try {
      var origFetch = window.fetch;
      if (typeof origFetch === "function") {
        window.fetch = function (input) {
          var p = origFetch.apply(this, arguments);
          try {
            var url = (typeof Request !== "undefined" && input instanceof Request) ? input.url : String(input);
            if (url.indexOf("api/guide") !== -1) {
              flags.pending++;
              render();
              var done = function () {
                try { flags.pending = Math.max(0, flags.pending - 1); render(); } catch (e) { /* ignore */ }
              };
              p.then(done, done);
            }
          } catch (e) { /* ignore */ }
          return p;
        };
      }
    } catch (e) { /* ignore */ }

    // ---- alert: Scam Kavach screen visible ----
    try {
      var scam = document.getElementById("scam");
      if (scam && typeof MutationObserver !== "undefined") {
        var check = function () {
          try { flags.alert = scam.classList.contains("show"); render(); } catch (e) { /* ignore */ }
        };
        new MutationObserver(check).observe(scam, { attributes: true, attributeFilter: ["class"] });
        check();
      }
    } catch (e) { /* ignore */ }

    render();
  } catch (e) { /* orb stays idle; app unaffected */ }
})();
