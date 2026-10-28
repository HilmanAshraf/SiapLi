"""
Test the Target-role feature:
  Option 1 — Exact Target Role Match (single posting + gaps + courses)
  Option 2 — Alternative Related Roles (data-grounded alternatives)

Uses the Cybersecurity example from the spec and checks the logic directly
against the real internship database, then exercises the web routes.
"""

import io
import json

import app as flask_app
import db
import matching
import seed_data


def _postings():
    return [dict(p, skills=json.loads(p["skills_json"] or "[]"))
            for p in db.get_all_postings()]


def main():
    db.init_db()
    seed_data.run()

    postings = _postings()
    cyber = next(p for p in postings if p["title"] == "Cybersecurity Intern")
    # A student with some networking/linux skills but no security specifics.
    resume_skills = ["Linux", "Networking", "Communication", "Problem Solving",
                     "Python", "Git"]

    # --- Option 1: exact target match ---
    best = matching.exact_target_match(resume_skills, postings, cyber["id"])
    assert best is not None, "target match should exist"
    assert best["posting"]["title"] == "Cybersecurity Intern"
    assert "Linux" in best["matched"], "Linux should be a matched skill"
    assert "Cybersecurity" in best["gap"], "Cybersecurity should be a gap"
    print(f"Option 1 OK — {best['posting']['title']} "
          f"({best['score']}%), matched={best['matched']}, gap={best['gap']}")

    # --- Option 2: alternatives ---
    alts = matching.alternative_roles(resume_skills, postings, cyber["id"],
                                      top_n=4)
    assert alts, "expected at least one alternative"
    titles = [a["posting"]["title"] for a in alts]
    print(f"Option 2 OK — alternatives: {titles}")

    # Data-grounded checks: no alternative may require a target gap skill.
    target_gap = set(best["gap"])
    for a in alts:
        req = set(a["posting"]["skills"])
        assert not (req & target_gap), \
            f"{a['posting']['title']} wrongly requires a target gap skill"
        assert a["shared_with_target"], "alternative must share a skill"
    # IT Support Intern is the spec's example alternative — confirm it appears.
    assert "IT Support Intern" in titles, \
        f"expected IT Support Intern among alternatives, got {titles}"
    print("Alternatives are data-grounded (no target-gap skills required).")

    # --- Web routes ---
    client = flask_app.app.test_client()
    data = {
        "consent": "on",
        "resume": (io.BytesIO(
            "Skilled in Linux, Networking, Python, Git. Good communication "
            "and problem solving.".encode()), "r.txt"),
    }
    r = client.post("/upload", data=data,
                    content_type="multipart/form-data")
    rid = int(r.headers["Location"].rstrip("/").split("/")[-1])

    assert client.get(f"/target/{rid}").status_code == 200
    r = client.get(f"/target-match/{rid}?role={cyber['id']}")
    assert r.status_code == 200
    assert b"Option 1" in r.data and b"Option 2" in r.data
    assert b"Free course" in r.data
    print("Web routes OK — /target and /target-match render both options.")

    # No role selected -> redirect back
    assert client.get(f"/target-match/{rid}").status_code == 302
    print("Missing role handled OK (redirects back).")

    # Existing features untouched
    assert client.get("/").status_code == 200
    assert client.get(f"/choose/{rid}").status_code == 200
    assert client.get(f"/recommend/{rid}?mode=skills").status_code == 200
    assert client.get(f"/results/{rid}").status_code == 200
    assert client.get("/dashboard").status_code == 200
    print("Existing routes still OK.")

    print("\nALL TARGET-ROLE TESTS PASSED ✅")


if __name__ == "__main__":
    main()
