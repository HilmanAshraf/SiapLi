"""
Quick end-to-end smoke test for Day 1 (no browser needed).
Verifies: DB init -> seed -> upload a resume -> matches -> dashboard.
"""

import io

import app as flask_app
import db
import seed_data


def main():
    db.init_db()
    seed_data.run()

    client = flask_app.app.test_client()

    # 1. Home page
    r = client.get("/")
    assert r.status_code == 200, "home failed"
    assert b"internship" in r.data.lower()

    # 2. Upload page
    r = client.get("/upload")
    assert r.status_code == 200, "upload page failed"

    # 3. Upload a sample resume (TXT) with consent
    resume = ("Jane Doe\njane.doe@example.com\n0123456789\n"
              "Skilled in Python, Flask, SQL and git. Enjoys teamwork and "
              "data analysis. Built a React project.")
    data = {
        "consent": "on",
        "target_role": "Software Engineering Intern",
        "resume": (io.BytesIO(resume.encode()), "resume.txt"),
    }
    r = client.post("/upload", data=data,
                    content_type="multipart/form-data",
                    follow_redirects=True)
    assert r.status_code == 200, "upload POST failed"
    assert b"%" in r.data, "no match score shown"
    assert b"Free course" in r.data, "no course links on results"
    print("Results page OK — match scores + course links rendered.")

    # 3b. Skill extraction picked up real skills from the resume
    conn = db.get_connection()
    import json as _json
    row = conn.execute("SELECT skills_json FROM resumes "
                       "ORDER BY id DESC LIMIT 1").fetchone()
    skills = _json.loads(row["skills_json"])
    conn.close()
    assert "Python" in skills and "Flask" in skills, f"skills off: {skills}"
    print(f"Skill extraction OK — found {skills}")

    # 4. Confirm PII was scrubbed in storage
    conn = db.get_connection()
    row = conn.execute("SELECT scrubbed_text FROM resumes "
                       "ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    stored = row["scrubbed_text"]
    assert "jane.doe@example.com" not in stored, "EMAIL not scrubbed!"
    assert "0123456789" not in stored, "PHONE not scrubbed!"
    print("PII scrubbing OK — email and phone removed before storage.")

    # 5. Dashboard renders
    r = client.get("/dashboard")
    assert r.status_code == 200, "dashboard failed"
    print("Dashboard OK.")

    print("\nALL SMOKE TESTS PASSED ✅")


if __name__ == "__main__":
    main()
