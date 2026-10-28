"""
Test the AI resume feedback feature (rule-based, privacy-safe).
"""

import io
import json

import app as flask_app
import db
import feedback as fb
import seed_data


def _postings():
    return [dict(p, skills=json.loads(p["skills_json"] or "[]"))
            for p in db.get_all_postings()]


def main():
    db.init_db()
    seed_data.run()
    postings = _postings()

    # Front End Engineer role requires React (a real posting), so a resume
    # without React has a React gap.
    swe = next(p for p in postings if p["title"] == "Front End Engineer Intern")

    # Resume with HTML/CSS/Git but missing React, no numbers, weak verbs.
    text = "Student interested in HTML and CSS. Knows Git."
    skills = ["HTML", "CSS", "Git"]
    items = fb.generate_feedback(text, skills, swe, course_map={
        "React": "https://react.dev/learn"})

    types = {i["type"] for i in items}
    assert "strength" in types, "should praise matched skills"
    assert "gap" in types, "should flag missing skills"
    assert "tip" in types, "should give writing tips"

    # A gap item should carry a course link when available.
    react_gap = next((i for i in items
                      if i["type"] == "gap" and i["skill"] == "React"), None)
    assert react_gap is not None, "React gap should appear"
    assert react_gap["course_url"], "React gap should include a course link"

    # Quantify-impact tip fires because the text has no digits.
    assert any("Quantify" in i["title"] for i in items), \
        "should suggest quantifying impact"
    print(f"Feedback engine OK — {len(items)} items, types={sorted(types)}")

    # --- Web route ---
    client = flask_app.app.test_client()
    data = {"consent": "on",
            "resume": (io.BytesIO(text.encode()), "r.txt")}
    r = client.post("/upload", data=data, content_type="multipart/form-data")
    rid = int(r.headers["Location"].rstrip("/").split("/")[-1])

    r = client.get(f"/feedback/{rid}?role={swe['id']}")
    assert r.status_code == 200, "feedback route failed"
    assert b"resume feedback" in r.data.lower()
    assert b"Privacy-safe" in r.data
    print("Feedback route OK — renders tailored suggestions.")

    # Missing role -> redirect
    assert client.get(f"/feedback/{rid}").status_code == 302
    print("Missing role handled OK.")

    # Existing routes unaffected
    assert client.get(f"/target-match/{rid}?role={swe['id']}").status_code == 200
    assert client.get("/dashboard").status_code == 200
    print("Existing routes still OK.")

    print("\nALL FEEDBACK TESTS PASSED ✅")


if __name__ == "__main__":
    main()
