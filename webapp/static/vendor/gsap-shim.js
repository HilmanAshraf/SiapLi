/* Minimal no-op GSAP + ScrollTrigger shim.
   Lets the app run fully offline before the real libraries are dropped in.
   The real gsap.min.js / ScrollTrigger.min.js (if present) load AFTER this and
   override window.gsap / window.ScrollTrigger with the full implementations.

   This shim applies END STATES immediately (no animation), which is exactly the
   graceful-degradation behaviour the spec asks for. */
(function () {
  if (window.gsap) return; // real lib already present

  function applyEndState(targets, vars) {
    var els = toEls(targets);
    els.forEach(function (el) {
      if (!el || !el.style) return;
      // Set terminal values immediately.
      if (vars.opacity !== undefined) el.style.opacity = finalVal(vars.opacity, 1);
      if (vars.y !== undefined) el.style.transform = "none";
      if (vars.x !== undefined) el.style.transform = "none";
      if (vars.scaleX !== undefined) el.style.transform = "none";
    });
  }
  function finalVal(v, dflt) {
    if (typeof v === "object" && v !== null) return dflt; // {from:..} fromTo end
    return v;
  }
  function toEls(t) {
    if (!t) return [];
    if (typeof t === "string") return Array.prototype.slice.call(document.querySelectorAll(t));
    if (t.length !== undefined && !t.style) return Array.prototype.slice.call(t);
    return [t];
  }

  var tl = {
    from: function (t, v) { applyEndState(t, v || {}); return tl; },
    to: function (t, v) { applyEndState(t, v || {}); return tl; },
    fromTo: function (t, a, b) { applyEndState(t, b || {}); return tl; },
    add: function () { return tl; }, set: function (t, v) { applyEndState(t, v || {}); return tl; }
  };

  window.gsap = {
    timeline: function () { return tl; },
    from: function (t, v) { applyEndState(t, v || {}); return tl; },
    to: function (t, v) {
      // Support count-up "to" by jumping straight to the end value.
      if (v && v.textContent !== undefined && t && t.textContent !== undefined) {
        t.textContent = v.textContent;
      }
      applyEndState(t, v || {}); return tl;
    },
    fromTo: function (t, a, b) { applyEndState(t, b || {}); return tl; },
    set: function (t, v) { applyEndState(t, v || {}); return tl; },
    registerPlugin: function () {}
  };
  window.ScrollTrigger = {
    create: function () { return {}; },
    refresh: function () {},
    batch: function () {}
  };
  window.__gsapShim = true;
})();
