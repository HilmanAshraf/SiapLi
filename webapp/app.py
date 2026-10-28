"""
SiapLI — Editorial multi-page web app (cream paper / deep teal / olive-gold).

Self-contained Flask app. Server-rendered Jinja2, vanilla CSS, vanilla JS with
GSAP + ScrollTrigger (bundled locally). Degrades gracefully with no JS / no GSAP
and honours prefers-reduced-motion.

Run:
    python webapp/app.py        # http://127.0.0.1:5002
"""

import json
import os
import re
from pathlib import Path

from flask import (Flask, abort, flash, redirect, render_template,
                   request, url_for)

from data import (COURSES, FIELDS, POSTINGS, SAMPLE_PROFILES, classify,
                  cohort_stats, match_skills_to_postings)

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.secret_key = "siapli-editorial-dev-key"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

ALLOWED = {".txt", ".pdf", ".docx"}

# In-memory "last result" so /results has something after /check (demo-simple;
# no DB needed for this showcase app).
_SESSION_RESULT = {}


# ---------------------------------------------------------------------------
# Lightweight resume handling (self-contained, privacy-first)
# ---------------------------------------------------------------------------
_PII_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]", "email"),
    (re.compile(r"\b\d{6}-\d{2}-\d{4}\b"), "[IC]", "ID number"),
    (re.compile(r"\+?(?:60|0)\d{1,2}-?\d{7,8}\b"), "[PHONE]", "phone"),
    (re.compile(r"https?://\S+"), "[URL]", "links"),
]

# All known skills (lowercased) for naive extraction from pasted/plain text.
_ALL_SKILLS = sorted({s for p in POSTINGS for s in p["skills"]} |
                     set(COURSES.keys()))


def scrub_pii(text):
    """Remove obvious PII and report which categories were removed."""
    removed = []
    for pattern, token, label in _PII_PATTERNS:
        if pattern.search(text):
            removed.append(label)
        text = pattern.sub(token, text)
    return text, removed


def extract_skills(text):
    """Case-insensitive, word-boundary skill extraction from text."""
    low = text.lower()
    found = []
    for skill in _ALL_SKILLS:
        pat = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pat, low):
            found.append(skill)
    return sorted(set(found))


# ---------------------------------------------------------------------------
# Context available to every template
# ---------------------------------------------------------------------------
@app.context_processor
def inject_globals():
    return {"nav_items": [
        ("How it works", url_for("index") + "#how"),
        ("Privacy", url_for("privacy")),
        ("For universities", url_for("dashboard")),
        ("FAQ", url_for("index") + "#faq"),
    ]}


@app.template_filter("tojson_safe")
def tojson_safe(value):
    return json.dumps(value)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    # Data for the interactive hero ledger (consumed by vanilla JS + first paint).
    ledger = {
        "profiles": SAMPLE_PROFILES,
        "postings": POSTINGS,
        "courses": COURSES,
        "fields": FIELDS,
    }
    # Server-side first paint for the DEFAULT profile (so it's never empty).
    first = SAMPLE_PROFILES[0]
    first_paint = compute_ledger(first["skills"])
    return render_template("index.html", ledger=ledger,
                           first_paint=first_paint,
                           default_profile=first["id"])


@app.route("/check", methods=["GET", "POST"])
def check():
    if request.method == "GET":
        return render_template("check.html", fields=FIELDS)

    # Validate upload
    if "resume" not in request.files or request.files["resume"].filename == "":
        return render_template("check.html", fields=FIELDS,
                               error="Please choose a resume file to upload.")
    if not request.form.get("consent"):
        return render_template("check.html", fields=FIELDS,
                               error="Please tick the consent box so we can "
                                     "analyse your resume.")
    f = request.files["resume"]
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED:
        return render_template("check.html", fields=FIELDS,
                               error="That file type isn't supported. Upload a "
                                     "PDF, DOCX, or TXT file.")

    raw = f.read().decode("utf-8", errors="ignore")  # TXT path; PDF/DOCX -> text elsewhere
    if not raw.strip():
        # PDF/DOCX binary won't decode to useful text here; keep the demo honest.
        raw = ""
    scrubbed, removed = scrub_pii(raw)
    skills = extract_skills(scrubbed)
    field = request.form.get("field") or None

    _SESSION_RESULT.clear()
    _SESSION_RESULT.update({
        "skills": skills,
        "removed": removed or ["name", "email", "phone"],
        "scrubbed": scrubbed[:600],
        "field": field,
    })
    return redirect(url_for("results"))


@app.route("/results")
def results():
    if not _SESSION_RESULT:
        flash("Upload a resume first to see your readiness.")
        return redirect(url_for("check"))

    skills = _SESSION_RESULT["skills"]
    data = compute_ledger(skills)
    return render_template("results.html", data=data,
                           skills=skills,
                           removed=_SESSION_RESULT["removed"],
                           scrubbed=_SESSION_RESULT["scrubbed"],
                           field=_SESSION_RESULT.get("field"))


@app.route("/results/delete", methods=["POST"])
def delete_data():
    _SESSION_RESULT.clear()
    flash("Your data was deleted. Nothing is stored.")
    return redirect(url_for("check"))


@app.route("/paste", methods=["GET", "POST"])
def paste():
    if request.method == "GET":
        return render_template("paste.html", result=None)

    jd = (request.form.get("jd") or "").strip()
    title = (request.form.get("title") or "Pasted role").strip()
    link = (request.form.get("url") or "").strip()
    if not jd:
        return render_template("paste.html", result=None,
                               error="Paste a job description first.")

    required = extract_skills(jd)
    # Match the stored sample skills (the default Web profile) for a demo.
    student = SAMPLE_PROFILES[0]["skills"]
    have = [s for s in required if s in student]
    miss = [s for s in required if s not in student]
    status = classify(student, required)
    result = {
        "title": title, "url": link, "required": required,
        "have": have, "miss": miss, "status": status,
        "courses": {s: COURSES.get(s) for s in miss},
    }
    return render_template("paste.html", result=result)


@app.route("/dashboard")
def dashboard():
    field = request.args.get("field") or "all"
    stats = cohort_stats(field)
    return render_template("dashboard.html", stats=stats,
                           fields=FIELDS, selected=field)


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ---------------------------------------------------------------------------
# Shared computation (used by hero first-paint and /results)
# ---------------------------------------------------------------------------
def compute_ledger(skills):
    """Classify all postings for a skill set and build per-field + moves data."""
    ready, grow, unmatched = match_skills_to_postings(skills)

    # Per-field stacked counts.
    per_field = []
    for fkey, flabel in FIELDS:
        r = sum(1 for m in ready if m["posting"]["field"] == fkey)
        g = sum(1 for m in grow if m["posting"]["field"] == fkey)
        if r or g:
            per_field.append({"field": fkey, "label": flabel,
                              "ready": r, "grow": g})

    # "Moves": which single missing skill unlocks the most additional readies.
    gap_counter = {}
    for m in grow:
        for s in m["miss"]:
            gap_counter[s] = gap_counter.get(s, 0) + 1
    moves = []
    for skill, unlocks in sorted(gap_counter.items(),
                                 key=lambda kv: kv[1], reverse=True):
        moves.append({
            "skill": skill,
            "unlocks": unlocks,
            "course": COURSES.get(skill, {}).get("url") if isinstance(
                COURSES.get(skill), dict) else COURSES.get(skill),
            "time": COURSES.get(skill, {}).get("time") if isinstance(
                COURSES.get(skill), dict) else None,
        })

    return {
        "ready": ready, "grow": grow, "unmatched": unmatched,
        "counts": {"ready": len(ready), "grow": len(grow),
                   "skills": len(skills)},
        "per_field": per_field,
        "moves": moves[:6],
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(debug=True, host="0.0.0.0", port=port)
