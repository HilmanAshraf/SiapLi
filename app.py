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
import fields
import matching
import nlp  # real NLP module (P2); falls back gracefully if spaCy not installed

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

    # Extract skills from the original text (skills are not PII).
    resume_skills = nlp.extract_skills(raw_text)
    # Responsible-AI: scrub PII BEFORE storing or any external call.
    scrubbed = nlp.scrub_pii(raw_text)

    resume_id = db.add_resume(
        scrubbed_text=scrubbed,
        skills=resume_skills,
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

    # New: let the student pick a recommendation option.
    return redirect(url_for("choose", resume_id=resume_id))


@app.route("/results/<int:resume_id>")
def results(resume_id):
    matches = db.get_top_matches(resume_id, limit=3)
    courses = db.get_course_map()  # {skill_name: course_url}
    return render_template("results.html", matches=matches,
                           resume_id=resume_id, courses=courses)


# ---------------------------------------------------------------------------
# New feature: two recommendation options after a resume is analysed
# ---------------------------------------------------------------------------

def _load_postings_with_skills():
    """Load all postings with their skills parsed from JSON."""
    import json
    out = []
    for p in db.get_all_postings():
        p["skills"] = json.loads(p.get("skills_json") or "[]")
        out.append(p)
    return out


@app.route("/choose/<int:resume_id>")
def choose(resume_id):
    """Present the two recommendation options for an analysed resume."""
    resume = db.get_resume(resume_id)
    if resume is None:
        flash("That resume was not found. Please upload again.")
        return redirect(url_for("upload"))
    return render_template("choose.html", resume=resume,
                           fields=fields.field_choices())


@app.route("/recommend/<int:resume_id>")
def recommend(resume_id):
    """
    Produce recommendations in one of two modes:
      ?mode=skills                 -> Option 1 (Match My Skills)
      ?mode=field&field=<key>      -> Option 2 (Explore My Preferred Field)
    """
    resume = db.get_resume(resume_id)
    if resume is None:
        flash("That resume was not found. Please upload again.")
        return redirect(url_for("upload"))

    mode = request.args.get("mode", "skills")
    postings = _load_postings_with_skills()
    courses = db.get_course_map()

    if mode == "field":
        field_key = request.args.get("field", "")
        field = fields.get_field(field_key)
        if field is None:
            flash("Please choose a valid field.")
            return redirect(url_for("choose", resume_id=resume_id))
        recs = matching.rank_by_field(resume["skills"], postings,
                                      field_key, top_n=5)
        return render_template(
            "recommend.html", mode="field", resume=resume,
            recs=recs, courses=courses,
            field_label=field["label"], field_skills=field["skills"])

    # Default: Option 1 — Match My Skills.
    recs = matching.rank_by_skills(resume["scrubbed_text"], resume["skills"],
                                   postings, top_n=5)
    return render_template("recommend.html", mode="skills", resume=resume,
                           recs=recs, courses=courses)


# ---------------------------------------------------------------------------
# New feature: Target-role recommendations
#   Option 1 — Exact Target Role Match
#   Option 2 — Alternative Related Roles
# ---------------------------------------------------------------------------

@app.route("/target/<int:resume_id>")
def target(resume_id):
    """Let the student pick a target role from the real internship listings."""
    resume = db.get_resume(resume_id)
    if resume is None:
        flash("That resume was not found. Please upload again.")
        return redirect(url_for("upload"))

    roles = [{"id": p["id"], "title": p["title"], "company": p["company"]}
             for p in db.get_all_postings()]
    return render_template("target.html", resume=resume, roles=roles)


@app.route("/target-match/<int:resume_id>")
def target_match(resume_id):
    """Show Option 1 (exact target) and Option 2 (alternatives) for a role."""
    resume = db.get_resume(resume_id)
    if resume is None:
        flash("That resume was not found. Please upload again.")
        return redirect(url_for("upload"))

    role_id = request.args.get("role", type=int)
    if role_id is None:
        flash("Please choose a target role.")
        return redirect(url_for("target", resume_id=resume_id))

    postings = _load_postings_with_skills()
    courses = db.get_course_map()

    best = matching.exact_target_match(resume["skills"], postings, role_id)
    if best is None:
        flash("That role is no longer available. Please choose another.")
        return redirect(url_for("target", resume_id=resume_id))

    alternatives = matching.alternative_roles(resume["skills"], postings,
                                              role_id, top_n=4)

    return render_template("target_match.html", resume=resume, courses=courses,
                           target=best, alternatives=alternatives)


@app.route("/dashboard")
def dashboard():
    gaps = db.cohort_skill_gaps(top_n=10)
    labels = [g[0] for g in gaps]
    values = [g[1] for g in gaps]
    return render_template("dashboard.html", labels=labels, values=values)


if __name__ == "__main__":
    db.init_db()  # ensure tables exist on startup
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug, host="0.0.0.0", port=port)
