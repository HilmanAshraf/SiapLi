"""
SiapLI — Validation study (Day 3 deliverable for the Validation slide).

Measures two things the judges asked for, using ONLY the seeded data:

  1. Top-3 agreement
     Each seeded resume (R-001 ..) was written with an intended best-fit role.
     We treat that intended role as the ground-truth label (a proxy for lecturer
     judgement) and measure how often SiapLI's top-3 skill matches include it.

  2. Before/after improvement
     We take a weak resume, record its match score for a target role, then add
     the missing skills (simulating the student acting on our feedback) and
     re-score. We report the average lift.

This is an HONEST proxy, clearly labelled. For the real pitch, replace the
ground truth with lecturer/industrial-training-unit rankings.

Run:
    python validation.py            # prints the numbers
    python validation.py --write    # also writes pitch/VALIDATION_RESULTS.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import db
import matching
from seed_data import SAMPLE_RESUMES


def _postings():
    return [dict(p, skills=json.loads(p["skills_json"] or "[]"))
            for p in db.get_all_postings()]


def _resumes_with_labels():
    """Return [(skills, scrubbed_text, intended_role_title), ...]."""
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT label, scrubbed_text, skills_json, target_role FROM resumes "
        "WHERE target_role IS NOT NULL").fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append((json.loads(r["skills_json"] or "[]"),
                    r["scrubbed_text"], r["target_role"]))
    return out


def top3_agreement(postings):
    """% of resumes whose top-3 skill matches include their intended role."""
    labelled = _resumes_with_labels()
    if not labelled:
        return 0.0, 0, 0, []

    hits = 0
    rows = []
    for skills, text, intended in labelled:
        ranked = matching.rank_by_skills(text, skills, postings, top_n=3)
        top3 = [r["posting"]["title"] for r in ranked]
        hit = intended in top3
        hits += 1 if hit else 0
        rows.append((intended, top3, hit))

    pct = round(hits / len(labelled) * 100, 1)
    return pct, hits, len(labelled), rows


def before_after_lift(postings):
    """
    Average match-score lift when a student learns their missing skills.
    Uses each resume's intended role as the target.
    """
    labelled = _resumes_with_labels()
    lifts = []
    for skills, text, intended in labelled:
        target = next((p for p in postings if p["title"] == intended), None)
        if target is None:
            continue
        required = target["skills"]
        before = matching.evaluate_posting(skills, target)["skill_coverage"]
        # Simulate the student acting on feedback: acquire the missing skills.
        improved = sorted(set(skills) | set(required))
        after = matching.evaluate_posting(improved, target)["skill_coverage"]
        lifts.append(after - before)

    if not lifts:
        return 0.0, 0.0, 0.0
    avg = round(sum(lifts) / len(lifts), 1)
    return avg, round(min(lifts), 1), round(max(lifts), 1)


def run(write=False):
    db.init_db()
    postings = _postings()

    pct, hits, total, rows = top3_agreement(postings)
    avg_lift, min_lift, max_lift = before_after_lift(postings)

    print("=" * 60)
    print("SiapLI — Validation results")
    print("=" * 60)
    print(f"Top-3 agreement: {pct}%  ({hits}/{total} resumes)")
    print(f"Avg match-score lift after learning gaps: +{avg_lift} points "
          f"(range +{min_lift} to +{max_lift})")
    print("-" * 60)
    print("Per-resume detail (intended role -> top-3):")
    for intended, top3, hit in rows:
        mark = "HIT " if hit else "miss"
        print(f"  [{mark}] {intended}")
        print(f"         top3: {top3}")

    if write:
        _write_report(pct, hits, total, avg_lift, min_lift, max_lift, rows)
        print("\nWrote pitch/VALIDATION_RESULTS.md")

    return pct, avg_lift


def _write_report(pct, hits, total, avg_lift, min_lift, max_lift, rows):
    lines = []
    lines.append("# SiapLI — Validation Results (for the Validation slide)\n")
    lines.append("> Honest proxy: each seeded resume was written with an "
                 "intended best-fit role. We use that as ground truth (a stand-in "
                 "for lecturer judgement) and measure whether SiapLI's top-3 "
                 "skill matches include it. Replace with real lecturer rankings "
                 "for the final pitch.\n")
    lines.append("## Headline numbers\n")
    lines.append(f"- **Top-3 agreement: {pct}%** ({hits}/{total} resumes). The "
                 "intended role appeared in SiapLI's top-3 matches.")
    lines.append(f"- **Average match-score lift: +{avg_lift} points** after a "
                 "student learns their missing skills (range "
                 f"+{min_lift} to +{max_lift}). This is the measurable value of "
                 "acting on the skill-gap report and AI feedback.\n")
    lines.append("## Per-resume detail\n")
    lines.append("| Intended role | In top-3? | SiapLI top-3 |")
    lines.append("|---|---|---|")
    for intended, top3, hit in rows:
        lines.append(f"| {intended} | {'✅' if hit else '❌'} | "
                     f"{', '.join(top3)} |")
    lines.append("\n## Honest limitations\n")
    lines.append("- Ground truth is a proxy (intended role), not independent "
                 "lecturer judgement — the real study should use the industrial "
                 "training unit's rankings.")
    lines.append(f"- Sample size is small (n={total}). Results indicate "
                 "direction, not statistical significance.")
    lines.append("- The skills dictionary is not exhaustive, so a niche skill "
                 "could be missed in extraction.")
    Path("pitch").mkdir(exist_ok=True)
    Path("pitch/VALIDATION_RESULTS.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    run(write="--write" in sys.argv)
