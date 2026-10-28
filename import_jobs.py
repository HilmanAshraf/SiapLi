"""
SiapLI — import real internships from a CSV into the database.

Usage:
    python import_jobs.py real_internships_template.csv
    python import_jobs.py myjobs.csv --replace   # clear prior imports first

CSV columns (header row, case-insensitive):
    title, company, location, description, skills, apply_url
  - `skills` separated by ';' (or ',')
  - `apply_url` = the REAL application link; leave blank if unknown.

Behaviour:
  - Skips rows whose title starts with "EXAMPLE" (the template's sample rows).
  - Skips duplicates: a row is a duplicate if a posting with the same
    (title, company) already exists — so re-running is safe.
  - --replace deletes all existing postings (and their match_results) first.
  - Prints a clear summary and flags rows with no apply_url.
"""

import csv
import json
import sys

import db


def load_rows(csv_path):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            row = {(k or "").strip().lower(): (v or "").strip()
                   for k, v in raw.items()}
            if not row.get("title"):
                continue
            if row["title"].upper().startswith("EXAMPLE"):
                continue  # template sample rows
            rows.append(row)
    return rows


def existing_keys():
    keys = set()
    for p in db.get_all_postings():
        keys.add((p["title"].strip().lower(),
                  (p.get("company") or "").strip().lower()))
    return keys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    csv_path = sys.argv[1]
    replace = "--replace" in sys.argv[2:]

    db.init_db()

    if replace:
        conn = db.get_connection()
        conn.execute("DELETE FROM match_results")
        conn.execute("DELETE FROM postings")
        conn.commit()
        conn.close()
        print("Cleared existing postings (--replace).")

    rows = load_rows(csv_path)
    if not rows:
        print("No usable rows found (did you delete the EXAMPLE rows and keep "
              "the header?).")
        return

    seen = existing_keys()
    imported = skipped = no_url = 0
    for row in rows:
        key = (row["title"].strip().lower(),
               (row.get("company") or "").strip().lower())
        if key in seen:
            skipped += 1
            continue

        skills_raw = row.get("skills", "")
        sep = ";" if ";" in skills_raw else ","
        skills = [s.strip() for s in skills_raw.split(sep) if s.strip()]
        apply_url = row.get("apply_url") or None
        if not apply_url:
            no_url += 1

        db.add_posting(
            title=row["title"],
            description=row.get("description", ""),
            company=row.get("company") or None,
            location=row.get("location") or None,
            skills=skills,
            apply_url=apply_url,
        )
        seen.add(key)
        imported += 1

    print("\n" + "=" * 48)
    print(f"Imported : {imported}")
    print(f"Skipped  : {skipped} (already in database)")
    if no_url:
        print(f"Note     : {no_url} row(s) had no apply_url — their Apply Now "
              f"button will show disabled (honest, not broken).")
    total = len(db.get_all_postings())
    print(f"Database now has {total} postings.")
    print("=" * 48)


if __name__ == "__main__":
    main()
