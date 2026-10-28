"""
Test the Apply Now feature: apply_url column, CSV import, and that the
target-match page shows a real Apply button when a URL exists and the
"Application link unavailable" message when it doesn't.
"""

import io
import json
import tempfile
from pathlib import Path

import app as flask_app
import db
import seed_data


def main():
    db.init_db()
    seed_data.run()

    # 1. Schema has apply_url
    cols = [r["name"] for r in db.get_connection().execute(
        "PRAGMA table_info(postings)")]
    assert "apply_url" in cols, "postings.apply_url column missing"
    print("Schema OK — postings has apply_url.")

    # 2. CSV import supports apply_url
    csv_text = (
        "title,company,location,description,skills,apply_url\n"
        "Test Apply Intern,RealCo,KL,Build things with Python and Git,"
        "Python;Git,https://realco.example.com/careers/apply/test-apply\n"
        "No Link Intern,NoCo,KL,Work with SQL,SQL,\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                     newline="", encoding="utf-8") as fh:
        fh.write(csv_text)
        csv_path = fh.name
    n = db.import_postings_csv(csv_path)
    Path(csv_path).unlink()
    assert n == 2, f"expected 2 rows imported, got {n}"

    postings = {p["title"]: p for p in db.get_all_postings()}
    assert postings["Test Apply Intern"]["apply_url"].endswith("test-apply")
    assert not postings["No Link Intern"]["apply_url"]
    print("CSV import OK — apply_url imported; blank stays blank.")

    # 3. Web: target-match shows a real Apply button for a posting WITH a url
    client = flask_app.app.test_client()
    data = {"consent": "on",
            "resume": (io.BytesIO(b"Skilled in Python and Git."), "r.txt")}
    r = client.post("/upload", data=data, content_type="multipart/form-data")
    rid = int(r.headers["Location"].rstrip("/").split("/")[-1])

    role_id = postings["Test Apply Intern"]["id"]
    r = client.get(f"/target-match/{rid}?role={role_id}")
    assert r.status_code == 200
    assert b"Apply Now" in r.data, "Apply Now button missing for role with url"
    assert b"test-apply" in r.data, "correct apply_url not rendered"
    print("Apply button OK — renders the real URL and opens in a new tab.")

    # 4. A posting WITHOUT a url shows the unavailable message
    role_id2 = postings["No Link Intern"]["id"]
    r = client.get(f"/target-match/{rid}?role={role_id2}")
    assert b"Application link unavailable" in r.data, \
        "missing 'Application link unavailable' message"
    print("No-URL case OK — shows 'Application link unavailable'.")

    print("\nALL APPLY TESTS PASSED ✅")


if __name__ == "__main__":
    main()
