/* SiapLI — interactive hero ledger (vanilla JS).
   Recomputes Ready/Grow/Skills + per-field bars + "moves" instantly in the
   browser. Classification rule MUST mirror data.py exactly. */
(function () {
  var root = document.getElementById("ledger");
  if (!root) return;

  var DATA, POSTINGS, COURSES, FIELDS, PROFILES;
  try {
    DATA = JSON.parse(root.getAttribute("data-ledger"));
    POSTINGS = DATA.postings; COURSES = DATA.courses;
    FIELDS = DATA.fields; PROFILES = DATA.profiles;
  } catch (e) { return; }

  var current = root.getAttribute("data-default") || PROFILES[0].id;
  var baseSkills = profileSkills(current);
  var learned = [];   // skills the user marked as learned

  function profileSkills(id) {
    var p = PROFILES.find(function (x) { return x.id === id; });
    return p ? p.skills.slice() : [];
  }
  function currentSkills() {
    var set = {};
    baseSkills.concat(learned).forEach(function (s) { set[s] = true; });
    return Object.keys(set);
  }

  // --- Classification (mirror of data.py) ---
  function classify(skills, required) {
    var have = required.filter(function (s) { return skills.indexOf(s) !== -1; });
    var miss = required.filter(function (s) { return skills.indexOf(s) === -1; });
    if (miss.length === 0) return "ready";
    if (miss.length <= 2 && have.length >= required.length / 2) return "grow";
    return "unmatched";
  }

  function compute() {
    var skills = currentSkills();
    var ready = [], grow = [];
    POSTINGS.forEach(function (p) {
      var status = classify(skills, p.skills);
      var have = p.skills.filter(function (s) { return skills.indexOf(s) !== -1; });
      var miss = p.skills.filter(function (s) { return skills.indexOf(s) === -1; });
      var item = { posting: p, have: have, miss: miss };
      if (status === "ready") ready.push(item);
      else if (status === "grow") grow.push(item);
    });

    // per-field
    var perField = FIELDS.map(function (f) {
      var key = f[0], label = f[1];
      var r = ready.filter(function (m) { return m.posting.field === key; }).length;
      var g = grow.filter(function (m) { return m.posting.field === key; }).length;
      return { field: key, label: label, ready: r, grow: g };
    }).filter(function (x) { return x.ready || x.grow; });

    // moves: missing skill -> how many grow postings it unlocks
    var counter = {};
    grow.forEach(function (m) {
      m.miss.forEach(function (s) { counter[s] = (counter[s] || 0) + 1; });
    });
    var moves = Object.keys(counter).map(function (s) {
      var c = COURSES[s] || {};
      return { skill: s, unlocks: counter[s], course: c.url, time: c.time };
    }).sort(function (a, b) { return b.unlocks - a.unlocks; }).slice(0, 6);

    return {
      counts: { ready: ready.length, grow: grow.length, skills: skills.length },
      perField: perField, moves: moves
    };
  }

  // --- Rendering ---
  function animateCount(el, to) {
    var from = parseInt(el.textContent, 10) || 0;
    if (window.gsap && !window.__gsapShim && !prefersReduced()) {
      var obj = { v: from };
      window.gsap.to(obj, {
        v: to, duration: 0.6, ease: "power2.out",
        onUpdate: function () { el.textContent = Math.round(obj.v); }
      });
    } else {
      el.textContent = to;
    }
  }
  function prefersReduced() {
    return window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function render(state) {
    root.querySelector('[data-count="ready"]') &&
      animateCount(root.querySelector('[data-count="ready"]'), state.counts.ready);
    root.querySelector('[data-count="grow"]') &&
      animateCount(root.querySelector('[data-count="grow"]'), state.counts.grow);
    root.querySelector('[data-count="skills"]') &&
      animateCount(root.querySelector('[data-count="skills"]'), state.counts.skills);

    // Field bars
    var bars = document.getElementById("fieldBars");
    bars.innerHTML = state.perField.map(function (fb) {
      var total = fb.ready + fb.grow || 1;
      return '<div class="fb-row"><span class="fb-label">' + esc(fb.label) +
        '</span><div class="fb-track">' +
        '<span class="fb-ready" style="width:' + (fb.ready / total * 100) + '%"></span>' +
        '<span class="fb-grow" style="width:' + (fb.grow / total * 100) + '%"></span>' +
        '</div></div>';
    }).join("");

    // Moves
    var list = document.getElementById("movesList");
    if (!state.moves.length) {
      list.innerHTML = '<p class="muted">You\'re ready for everything in these fields. Nice.</p>';
    } else {
      list.innerHTML = state.moves.map(function (m) {
        return '<div class="move"><div class="move-main">' +
          '<div class="move-skill">' + esc(m.skill) + '</div>' +
          '<div class="move-meta">Unlocks ' + m.unlocks + ' more' +
          (m.time ? ' · ' + esc(m.time) : '') + '</div></div>' +
          '<button class="btn btn-gold btn-sm" data-learn="' + esc(m.skill) + '">Mark as learned</button>' +
          '</div>';
      }).join("");
      if (window.gsap && !window.__gsapShim && !prefersReduced()) {
        window.gsap.from(list.querySelectorAll(".move"),
          { x: 14, opacity: 0, duration: 0.4, stagger: 0.05, ease: "power2.out" });
      }
    }
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // --- Events ---
  root.addEventListener("click", function (e) {
    var learn = e.target.closest("[data-learn]");
    if (learn) {
      var s = learn.getAttribute("data-learn");
      if (learned.indexOf(s) === -1) learned.push(s);
      render(compute());
      return;
    }
    var tab = e.target.closest("[data-profile]");
    if (tab) {
      current = tab.getAttribute("data-profile");
      baseSkills = profileSkills(current);
      learned = [];
      root.querySelectorAll("[data-profile]").forEach(function (b) {
        b.setAttribute("aria-selected", b === tab ? "true" : "false");
      });
      render(compute());
    }
  });

  var reset = document.getElementById("ledgerReset");
  if (reset) reset.addEventListener("click", function () {
    learned = []; render(compute());
  });

  // First JS paint (server already rendered a valid state; this syncs the JS model)
  render(compute());
})();
