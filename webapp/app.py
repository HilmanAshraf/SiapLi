"""
SiapLI — Editorial multi-page web app (cream paper / deep teal / olive-gold).

Editorial FRONTEND powered by the REAL SiapLI engine from the repo root:
  - nlp.py       : spaCy skill extraction + PII scrubbing
  - matching.py  : embedding match score, target-role + alternatives logic
  - feedback.py  : AI resume feedback
  - db.py        : real SQLite database (49 jobs, 88 courses, ...)
  - seed_data.py : seeds the database on first run

Run:
    python webapp/app.py        # http://127.0.0.1:5002
"""

import json
import os
import sys
import tempfile
from pathlib import Path

from flask import (Flask, flash, redirect, render_template,
                   request, url_for)

# --- Make the repo-root engine importable ---------------------------------
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import db                       # noqa: E402  (real database layer)
import nlp                      # noqa: E402  (real spaCy NLP)
import matching                 # noqa: E402  (real matching engine)
import feedback as feedback_engine  # noqa: E402  (AI resume feedback)
import seed_data                # noqa: E402  (real dataset)

# The hero ledger still uses lightweight sample profiles for the live widget.
from ledger_data import LEDGER_FIELDS, SAMPLE_PROFILES

app = Flask(__name__)
app.secret_key = "siapli-editorial-dev-key"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

ALLOWED = {".txt", ".pdf", ".docx"}

# In-memory "last result" so /results works after /check (demo-simple).
_SESSION = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _postings():
    out = []
    for p in db.get_all_postings():
        p["skills"] = json.loads(p.get("skills_json") or "[]")
        out.append(p)
    return out


def _ensure_seeded():
    db.init_db()
    if not db.get_all_postings():
        seed_data.run()


# ---------------------------------------------------------------------------
# Template context
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


@app.template_filter("fromjson")
def fromjson(value):
    try:
        return json.loads(value or "[]")
    except (TypeError, ValueError):
        return []


# ---------------------------------------------------------------------------
# Home — editorial landing + interactive hero ledger (unchanged UI)
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    ledger = {
        "profiles": SAMPLE_PROFILES,
        "postings": _ledger_postings(),
        "courses": _ledger_courses(),
        "fields": LEDGER_FIELDS,
    }
    first = SAMPLE_PROFILES[0]
    first_paint = _ledger_first_paint(first["skills"], ledger)
    return render_template("index.html", ledger=ledger,
                           first_paint=first_paint,
                           default_profile=first["id"])


# ---------------------------------------------------------------------------
# Check — upload resume with the REAL nlp pipeline
# ---------------------------------------------------------------------------
@app.route("/check", methods=["GET", "POST"])
def check():
    _ensure_seeded()
    if request.method == "GET":
        roles = [{"id": p["id"], "title": p["title"]} for p in _postings()]
        return render_template("check.html", roles=roles)

    if "resume" not in request.files or request.files["resume"].filename == "":
        return _check_error("Please choose a resume file to upload.")
    if not request.form.get("consent"):
        return _check_error("Please tick the consent box so we can analyse "
                            "your resume.")
    f = request.files["resume"]
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED:
        return _check_error("That file type isn't supported. Upload a PDF, "
                            "DOCX, or TXT file.")

    # Save to temp, extract with the REAL nlp module, then discard the raw file.
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        f.save(tmp.name)
        tmp_path = tmp.name
    try:
        raw = nlp.extract_text(tmp_path)
    finally:
        os.remove(tmp_path)

    if not raw.strip():
        return _check_error("We couldn't read any text from that file.")

    skills = nlp.extract_skills(raw)          # skills are not PII
    scrubbed = nlp.scrub_pii(raw)             # responsible-AI: strip PII

    # Persist (scrubbed only) to the real DB so /results can use the engine.
    resume_id = db.add_resume(scrubbed_text=scrubbed, skills=skills, consent=1)
    role_id = request.form.get("role", type=int)

    _SESSION.clear()
    _SESSION.update({"resume_id": resume_id, "role_id": role_id,
                     "scrubbed": scrubbed[:800]})
    return redirect(url_for("results"))


def _check_error(msg):
    roles = [{"id": p["id"], "title": p["title"]} for p in _postings()]
    return render_template("check.html", roles=roles, error=msg)


# ---------------------------------------------------------------------------
# Results — the ORIGINAL style: target match (Option 1) + alternatives
# (Option 2) + AI feedback, rendered in the editorial look.
# ---------------------------------------------------------------------------
@app.route("/results")
def results():
    if not _SESSION.get("resume_id"):
        flash("Upload a resume first to see your readiness.")
        return redirect(url_for("check"))

    resume = db.get_resume(_SESSION["resume_id"])
    if resume is None:
        flash("Your data was cleared. Please upload again.")
        return redirect(url_for("check"))

    postings = _postings()
    courses = db.get_course_map()
    skills = resume["skills"]

    # Option 1 — overall best matches by the student's existing skills.
    ranked = matching.rank_by_skills(resume["scrubbed_text"], skills,
                                     postings, top_n=6)

    # If a target role was chosen, compute exact match + alternatives + feedback.
    role_id = _SESSION.get("role_id")
    target = alternatives = tips = target_posting = None
    if role_id:
        target = matching.exact_target_match(skills, postings, role_id)
        alternatives = matching.alternative_roles(skills, postings, role_id,
                                                  top_n=4)
        target_posting = next((p for p in postings if p["id"] == role_id), None)
        if target_posting:
            tips = feedback_engine.generate_feedback(
                resume["scrubbed_text"], skills, target_posting, courses)

    return render_template(
        "results.html", skills=skills, ranked=ranked, courses=courses,
        target=target, alternatives=alternatives, tips=tips,
        target_posting=target_posting, scrubbed=_SESSION.get("scrubbed", ""))


@app.route("/results/delete", methods=["POST"])
def delete_data():
    rid = _SESSION.get("resume_id")
    if rid:
        conn = db.get_connection()
        conn.execute("DELETE FROM resumes WHERE id = ?", (rid,))
        conn.execute("DELETE FROM match_results WHERE resume_id = ?", (rid,))
        conn.commit()
        conn.close()
    _SESSION.clear()
    flash("Your data was deleted. Nothing is stored.")
    return redirect(url_for("check"))


# ---------------------------------------------------------------------------
# Paste a job — match a pasted JD with the REAL engine
# ---------------------------------------------------------------------------
@app.route("/paste", methods=["GET", "POST"])
def paste():
    _ensure_seeded()
    if request.method == "GET":
        return render_template("paste.html", result=None)

    jd = (request.form.get("jd") or "").strip()
    title = (request.form.get("title") or "Pasted role").strip()
    link = (request.form.get("url") or "").strip()
    if not jd:
        return render_template("paste.html", result=None,
                               error="Paste a job description first.")

    required = nlp.extract_skills(jd)
    courses = db.get_course_map()
    # Match against the most recently analysed resume if present, else the
    # first sample profile so the page is still useful on its own.
    if _SESSION.get("resume_id"):
        student = db.get_resume(_SESSION["resume_id"])["skills"]
    else:
        student = SAMPLE_PROFILES[0]["skills"]

    matched = matching.matched_skills(student, required)
    gap = matching.skill_gap(student, required)
    coverage = round(len(matched) / len(required) * 100, 1) if required else 0.0
    result = {
        "title": title, "url": link, "required": required,
        "have": matched, "miss": gap, "coverage": coverage,
        "courses": {s: courses.get(s) for s in gap},
    }
    return render_template("paste.html", result=result)


# ---------------------------------------------------------------------------
# Dashboard — anonymous cohort view from the REAL match_results
# ---------------------------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    _ensure_seeded()
    gaps = db.cohort_skill_gaps(top_n=10)

    conn = db.get_connection()
    n_resumes = conn.execute("SELECT COUNT(*) c FROM resumes").fetchone()["c"]
    n_postings = conn.execute("SELECT COUNT(*) c FROM postings").fetchone()["c"]
    # "ready" proxy: resumes with at least one >= 80% match.
    ready = conn.execute(
        "SELECT COUNT(DISTINCT resume_id) c FROM match_results "
        "WHERE score >= 80").fetchone()["c"]
    conn.close()

    max_gap = max((g[1] for g in gaps), default=1) or 1
    gap_bars = [{"skill": s, "needed": c, "pct": round(c / max_gap * 100)}
                for s, c in gaps]
    pct_ready = round(ready / n_resumes * 100) if n_resumes else 0

    stats = {"students": n_resumes, "postings": n_postings,
             "pct_ready": pct_ready, "gaps": gap_bars}
    return render_template("dashboard.html", stats=stats)


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ---------------------------------------------------------------------------
# Hero ledger data (lightweight; mirrors real postings for the live widget)
# ---------------------------------------------------------------------------
def _ledger_postings():
    """Compact postings (id/field/title/company/skills) for the JS ledger."""
    out = []
    for p in _postings():
        out.append({"id": p["id"], "field": _guess_field(p),
                    "title": p["title"], "company": p.get("company"),
                    "skills": p["skills"]})
    return out


def _ledger_courses():
    cm = db.get_course_map()
    return {k: {"url": v} for k, v in cm.items()}


def _guess_field(posting):
    t = (posting["title"] + " " + posting.get("description", "")).lower()
    if any(w in t for w in ["data", "analyt", "bi", "statistic"]):
        return "data"
    if any(w in t for w in ["network", "security", "cyber", "support", "system"]):
        return "network"
    return "web"


def _ledger_first_paint(skills, ledger):
    """Server-side first paint for the ledger (mirrors ledger.js classify)."""
    postings = ledger["postings"]
    ready, grow = [], []
    sset = set(skills)
    for p in postings:
        req = p["skills"]
        have = [s for s in req if s in sset]
        miss = [s for s in req if s not in sset]
        if not miss:
            ready.append(p)
        elif len(miss) <= 2 and len(have) >= len(req) / 2:
            grow.append({"posting": p, "miss": miss})

    per_field = []
    for key, label in ledger["fields"]:
        r = sum(1 for p in ready if p["field"] == key)
        g = sum(1 for m in grow if m["posting"]["field"] == key)
        if r or g:
            per_field.append({"field": key, "label": label, "ready": r, "grow": g})

    counter = {}
    for m in grow:
        for s in m["miss"]:
            counter[s] = counter.get(s, 0) + 1
    courses = ledger["courses"]
    moves = [{"skill": s, "unlocks": c, "course": courses.get(s, {}).get("url"),
              "time": None}
             for s, c in sorted(counter.items(), key=lambda kv: kv[1],
                                reverse=True)][:6]

    return {"counts": {"ready": len(ready), "grow": len(grow),
                       "skills": len(skills)},
            "per_field": per_field, "moves": moves}


if __name__ == "__main__":
    _ensure_seeded()
    port = int(os.environ.get("PORT", 5002))
    app.run(debug=True, host="0.0.0.0", port=port)
