/* SiapLI — motion + interactions (GSAP where available, graceful fallback). */
(function () {
  document.documentElement.classList.add("js");

  var reduced = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasGsap = window.gsap && !window.__gsapShim;

  // Load the ledger module (separate file).
  var s = document.createElement("script");
  s.src = document.currentScript
    ? document.currentScript.src.replace("motion.js", "ledger.js")
    : "/static/js/ledger.js";
  document.body.appendChild(s);

  // ---- Dropzone (check page) ----
  var dz = document.getElementById("dropzone");
  var input = document.getElementById("resume");
  var dzFile = document.getElementById("dzFile");
  if (dz && input) {
    function showFile() {
      if (input.files && input.files.length) {
        dzFile.hidden = false;
        dzFile.textContent = "Selected: " + input.files[0].name;
      }
    }
    input.addEventListener("change", showFile);
    ["dragenter", "dragover"].forEach(function (ev) {
      dz.addEventListener(ev, function (e) { e.preventDefault(); dz.classList.add("drag"); });
    });
    ["dragleave", "drop"].forEach(function (ev) {
      dz.addEventListener(ev, function (e) { e.preventDefault(); dz.classList.remove("drag"); });
    });
    dz.addEventListener("drop", function (e) {
      if (e.dataTransfer && e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files; showFile();
      }
    });
  }

  // ---- If reduced motion or no GSAP: show everything immediately ----
  function showAll() {
    document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("is-in"); });
    document.querySelectorAll(".pii").forEach(function (el) { el.classList.add("redacted"); });
  }
  if (reduced || !hasGsap) { showAll(); return; }

  if (window.ScrollTrigger) window.gsap.registerPlugin(window.ScrollTrigger);

  // ---- Page-load timeline (hero) ----
  var heroCopy = document.querySelectorAll(".hero-copy .reveal");
  if (heroCopy.length) {
    var tl = window.gsap.timeline();
    tl.from(heroCopy, { y: 18, opacity: 0, duration: 0.6, stagger: 0.08, ease: "power3.out" });
    var ledger = document.getElementById("ledger");
    if (ledger) {
      ledger.classList.add("is-in");
      tl.from(ledger, { y: 28, opacity: 0, duration: 0.7, ease: "power3.out" }, "-=0.2");
    }
  }

  // ---- Scroll reveals ----
  document.querySelectorAll(".reveal").forEach(function (el) {
    if (el.closest(".hero-copy") || el.id === "ledger") { el.classList.add("is-in"); return; }
    if (window.ScrollTrigger) {
      window.ScrollTrigger.create({
        trigger: el, start: "top 88%", once: true,
        onEnter: function () {
          window.gsap.fromTo(el, { y: 18, opacity: 0 },
            { y: 0, opacity: 1, duration: 0.7, ease: "power2.out" });
          el.classList.add("is-in");
        }
      });
    } else { el.classList.add("is-in"); }
  });

  // ---- Scroll-scrubbed redaction (privacy specimen) ----
  var specimen = document.getElementById("specimen");
  if (specimen && window.ScrollTrigger) {
    var piis = Array.prototype.slice.call(specimen.querySelectorAll(".pii"));
    window.ScrollTrigger.create({
      trigger: specimen, start: "top 80%", end: "bottom 40%", scrub: true,
      onUpdate: function (self) {
        var n = Math.floor(self.progress * piis.length + 0.0001);
        piis.forEach(function (el, i) {
          el.classList.toggle("redacted", i < n);
        });
      }
    });
  } else if (specimen) {
    specimen.querySelectorAll(".pii").forEach(function (el) { el.classList.add("redacted"); });
  }
})();
