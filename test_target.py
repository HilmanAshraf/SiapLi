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
    # Use a real security-governance role as the target (like the Cybersecurity
    # example): the student has networking basics but lacks the security
    # specifics, so related network roles become achievable alternatives.
    target = next(p for p in postings
                  if p["title"] == "Network Security Governance Intern")
    resume_skills = ["Networking", "TCP/IP", "Troubleshooting",
                     "Communication", "Linux"]

    # --- Option 1: exact target match ---
    best = matching.exact_target_match(resume_skills, postings, target["id"])
    assert best is not None, "target match should exist"
    assert best["posting"]["title"] == "Network Security Governance Intern"
    assert best["gap"], "there should be at least one gap skill"
    print(f"Option 1 OK — {best['posting']['title']} "
          f"({best['score']}%), matched={best['matched']}, gap={best['gap']}")

    # --- Option 2: alternatives ---
    alts = matching.alternative_roles(resume_skills, postings, target["id"],
                                      top_n=4)
    assert alts, "expected at least one alternative"
    titles = [a["posting"]["title"] for a in alts]
    print(f"Option 2 OK — alternatives: {titles}")

    # Data-grounded checks: each alternative must be MORE achievable than the
    # target — it demands fewer of the student's missing skills, and shares at
    # least one real skill with the target role.
    target_gap = set(best["gap"])
    for a in alts:
        req = set(a["posting"]["skills"])
        shared_gaps = req & target_gap
        assert len(shared_gaps) < len(target_gap), \
            f"{a['posting']['title']} does not lower the skill barrier"
        assert len(a["gap"]) < len(best["gap"]) \
            or a["skill_coverage"] > best["skill_coverage"], \
            f"{a['posting']['title']} is not more achievable than the target"
        assert a["shared_with_target"], "alternative must share a skill"
        assert a["why"], "alternative should explain why it's a good fit"
    print("Alternatives are data-grounded and more achievable than the target.")

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
    r = client.get(f"/target-match/{rid}?role={target['id']}")
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
