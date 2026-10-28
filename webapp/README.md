# SiapLI — Editorial web app

A self-contained, multi-page Flask app: cream paper / deep teal ink / olive-gold.
Server-rendered Jinja2, vanilla CSS, vanilla JS + GSAP/ScrollTrigger. Works fully
offline and degrades gracefully with no JS, no GSAP, or reduced motion.

This is a separate app from the main SiapLI prototype in the repo root — it does
not touch or depend on it.

## Run

```bash
# from the repo root, using the existing venv
./venv/bin/python webapp/app.py      # http://127.0.0.1:5002
```

Only Flask is required (already installed).

## Pages
- `/`           Landing with the interactive "readiness ledger"
- `/check`      Upload resume (drag-and-drop, consent)
- `/results`    Ready-now / Grow-into-it groups + privacy sidebar
- `/paste`      Paste a job description and match it
- `/dashboard`  Anonymous cohort view for universities
- `/privacy`    Prose privacy notice

## Bundling the real assets (optional — app works without them)
The app ships with graceful fallbacks so it runs offline today:

- **Fonts:** drop `Newsreader.woff2` and `HankenGrotesk.woff2` into
  `static/fonts/` (see that folder's README). Falls back to Georgia + system sans.
- **GSAP:** replace `static/vendor/gsap.min.js` and `ScrollTrigger.min.js` with
  the real GSAP 3 builds for full animation. A no-op shim (`gsap-shim.js`) keeps
  everything working meanwhile — scroll reveals and the ledger still function,
  just without tweened motion.

## Graceful degradation
- No JS: every page renders fully; the hero ledger shows server-rendered data.
- No GSAP: shim applies end states immediately; reveals/redaction still resolve.
- `prefers-reduced-motion`: all motion skipped, end states applied at once.
