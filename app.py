"""
SiapLI — Flask application (P1, Day 1 deliverable).

Routes
------
GET  /            landing page
GET  /upload      resume upload form (+ consent checkbox)
POST /upload      process resume -> scrub PII -> extract skills -> match -> results
GET  /results/<resume_id>   show top-3 matches + skill-gap report
GET  /dashboard   cohort skill-gap dashboard

This runs END-TO-END today using stubs (nlp_stub.py) and a fallback matcher,
so P2/P3/P4 can plug in their real work without touching routing.

Run:
    python db.py          # create tables (once)
    python seed_data.py   # load sample postings (once)
    python app.py         # start dev server on http://127.0.0.1:5000
"""

import os
import tempfile

from flask import (Flask, flash, redirect, render_template,
                   request, url_for)

import db
import matching
import nlp_stub as nlp  # P2 will swap this for the real module

app = Flask(__name__)
app.secret_key = "siapli-dev-key-change-me"  # dev only
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload cap


@app.template_filter("fromjson")
def _fromjson(value):
    """Parse a JSON string in templates (used for stored skill-gap lists)."""
    import json
    try:
        return json.loads(value or "[]")
    except (TypeError, ValueError):
        return []

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    # --- POST: handle the uploaded resume ---
    if "resume" not in request.files or request.files["resume"].filename == "":
        flash("Please choose a resume file.")
        return redirect(url_for("upload"))

    if not request.form.get("consent"):
        flash("You must consent to analysis before uploading.")
        return redirect(url_for("upload"))

    file = request.files["resume"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        flash("Unsupported file type. Use PDF, DOCX, or TXT.")
        return redirect(url_for("upload"))

    target_role = request.form.get("target_role", "").strip()

    # Save to a temp file, extract, then discard the raw file (no raw PII kept).
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        raw_text = nlp.extract_text(tmp_path)
    finally:
        os.remove(tmp_path)  # never persist the raw upload

    if not raw_text.strip():
        flash("Could not read any text from that file.")
        return redirect(url_for("upload"))

    # Responsible-AI: scrub PII BEFORE storing or any external call.
    scrubbed = nlp.scrub_pii(raw_text)
    resume_skills = nlp.extract_skills(scrubbed)

    resume_id = db.add_resume(
        scrubbed_text=scrubbed,
        skills=resume_skills,
        target_role=target_role or None,
        consent=1,
    )

    # Match against all postings and persist the top results.
    postings = []
    for p in db.get_all_postings():
        import json
        p["skills"] = json.loads(p.get("skills_json") or "[]")
        postings.append(p)

    ranked = matching.rank_postings(scrubbed, resume_skills, postings, top_n=5)
    for item in ranked:
        db.save_match(resume_id, item["posting"]["id"],
                      item["score"], item["gap"])

    return redirect(url_for("results", resume_id=resume_id))


@app.route("/results/<int:resume_id>")
def results(resume_id):
    matches = db.get_top_matches(resume_id, limit=3)
    return render_template("results.html", matches=matches,
                           resume_id=resume_id)


@app.route("/dashboard")
def dashboard():
    gaps = db.cohort_skill_gaps(top_n=10)
    labels = [g[0] for g in gaps]
    values = [g[1] for g in gaps]
    return render_template("dashboard.html", labels=labels, values=values)


if __name__ == "__main__":
    db.init_db()  # ensure tables exist on startup
    app.run(debug=True, port=5000)
