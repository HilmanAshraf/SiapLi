"""
Rewrite every posting's apply_url to a BROAD LinkedIn job search that reliably
returns results, instead of an over-specific query that lands on "no jobs found".

Strategy: derive a short, general keyword from the role title (field-level, not
company-specific), e.g. "Network Engineer Intern Telekom Malaysia" -> "network
engineer intern". Keep location=Malaysia. The company stays as the display
label on the card; the search itself is broad enough to always show real jobs.

Run:
    python fix_apply_urls.py           # update DB + rewrite real_internships.csv
"""

import csv
import re
import urllib.parse
from pathlib import Path

import db

CSV_PATH = Path(__file__).parent / "real_internships.csv"

# Words to strip so the query stays broad (companies, filler, punctuation).
_STRIP = {
    "with", "and", "the", "for", "a", "an", "of", "in", "at",
    "genai", "gfit", "programme", "program", "intake", "2026", "2027",
    "sdn", "bhd", "asia", "pacific", "malaysia", "berhad", "group",
}


def broad_keywords(title):
    """Turn a role title into a short, general search phrase."""
    # Keep letters/numbers/spaces, drop the rest.
    words = re.findall(r"[a-zA-Z0-9#+.]+", title.lower())
    kept = [w for w in words if w not in _STRIP]
    # Cap to the first 3 meaningful words + ensure "intern" is present.
    core = kept[:3]
    if "intern" not in " ".join(core) and "internship" not in " ".join(core):
        core.append("intern")
    phrase = " ".join(core)
    return phrase.strip()


def build_url(title):
    kw = broad_keywords(title)
    q = urllib.parse.urlencode({"keywords": kw, "location": "Malaysia"})
    return "https://www.linkedin.com/jobs/search/?" + q


def main():
    db.init_db()

    # 1. Update the database (only LinkedIn-search postings).
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT id, title, apply_url FROM postings "
        "WHERE apply_url LIKE '%linkedin.com/jobs/search%'").fetchall()
    updated = 0
    for r in rows:
        new_url = build_url(r["title"])
        conn.execute("UPDATE postings SET apply_url = ? WHERE id = ?",
                     (new_url, r["id"]))
        updated += 1
    conn.commit()
    conn.close()
    print(f"Updated {updated} posting apply_urls in the database.")

    # 2. Rewrite the CSV so re-imports stay consistent.
    if CSV_PATH.exists():
        with open(CSV_PATH, newline="", encoding="utf-8") as fh:
            reader = list(csv.DictReader(fh))
            fields = reader[0].keys() if reader else []
        for row in reader:
            if "apply_url" in row and "linkedin.com/jobs/search" in (row["apply_url"] or ""):
                row["apply_url"] = build_url(row["title"])
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(fields))
            writer.writeheader()
            writer.writerows(reader)
        print(f"Rewrote {len(reader)} rows in {CSV_PATH.name}.")


if __name__ == "__main__":
    main()
