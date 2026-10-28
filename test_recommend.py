"""
Test the new two-option recommendation feature end-to-end (no browser).
Verifies Option 1 (skills) and Option 2 (field) plus that existing routes
still work.
"""

import io

import app as flask_app
import db
import seed_data


def main():
    db.init_db()
    seed_data.run()
    client = flask_app.app.test_client()

    # Upload a resume -> should now redirect to /choose
    resume = ("Final year student skilled in Python, Flask, SQL and Git. "
              "Enjoys teamwork and data analysis. Built a React project.")
    data = {
        "consent": "on",
        "target_role": "Software Engineering Intern",
        "resume": (io.BytesIO(resume.encode()), "resume.txt"),
    }
    r = client.post("/upload", data=data,
                    content_type="multipart/form-data",
                    follow_redirects=False)
    assert r.status_code == 302, "upload should redirect"
    assert "/choose/" in r.headers["Location"], \
        f"should go to choose, got {r.headers['Location']}"
    resume_id = int(r.headers["Location"].rstrip("/").split("/")[-1])
    print(f"Upload -> choose page OK (resume {resume_id}).")

    # Choose page renders both options
    r = client.get(f"/choose/{resume_id}")
    assert r.status_code == 200
    assert b"Match My Skills" in r.data and b"Preferred Field" in r.data
    print("Choose page shows both options OK.")

    # --- Option 1: Match My Skills ---
    r = client.get(f"/recommend/{resume_id}?mode=skills")
    assert r.status_code == 200, "option 1 failed"
    assert b"match your skills" in r.data.lower()
    assert b"Skills you have" in r.data
    assert b"% match" in r.data
    print("Option 1 (skills) OK — match %, matched + missing skills shown.")

    # --- Option 2: Explore a field ---
    for field in ["cybersecurity", "data_analytics", "ai_ml",
                  "software_development"]:
        r = client.get(f"/recommend/{resume_id}?mode=field&field={field}")
        assert r.status_code == 200, f"option 2 failed for {field}"
        assert b"field fit" in r.data, f"no field score for {field}"
        print(f"Option 2 (field={field}) OK — field-ranked results shown.")

    # Invalid field is handled gracefully
    r = client.get(f"/recommend/{resume_id}?mode=field&field=nope",
                   follow_redirects=False)
    assert r.status_code == 302, "invalid field should redirect"
    print("Invalid field handled OK (redirects back).")

    # --- Existing routes still work (nothing removed) ---
    assert client.get("/").status_code == 200
    assert client.get("/upload").status_code == 200
    assert client.get(f"/results/{resume_id}").status_code == 200
    assert client.get("/dashboard").status_code == 200
    print("Existing routes (/, /upload, /results, /dashboard) still OK.")

    print("\nALL RECOMMENDATION TESTS PASSED ✅")


if __name__ == "__main__":
    main()
