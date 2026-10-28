"""
SiapLI — Database layer (SQLite).

Day 1 / P1 deliverable: schema + helper functions the whole team builds on.

Tables
------
postings      : internship postings (title, company, description, required skills)
resumes       : uploaded resumes (SCRUBBED text only — never store raw PII)
match_results : one row per (resume, posting) match with a score
skills        : curated skills dictionary (name + optional alias)

Notes for teammates
--------------------
- P2 (NLP): write to `resumes.scrubbed_text` and `resumes.skills_json`.
- P3 (Data): seed `postings` and `skills` via seed_data.py.
- P1 (Backend): compute + store rows in `match_results`.
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "siapli.db"


def get_connection():
    """Return a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Create all tables if they do not exist. Safe to call repeatedly."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS postings (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT NOT NULL,
            company       TEXT,
            location      TEXT,
            description   TEXT NOT NULL,
            skills_json   TEXT DEFAULT '[]',   -- JSON array of required skills
            apply_url     TEXT,                -- real application link (never invented)
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resumes (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            label          TEXT,                -- anonymised label, e.g. "R-012"
            scrubbed_text  TEXT NOT NULL,       -- PII REMOVED before storing
            skills_json    TEXT DEFAULT '[]',   -- JSON array of extracted skills
            target_role    TEXT,
            consent        INTEGER DEFAULT 0,   -- 1 if user consented
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS match_results (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id    INTEGER NOT NULL,
            posting_id   INTEGER NOT NULL,
            score        REAL NOT NULL,         -- 0..100 match percentage
            gap_json     TEXT DEFAULT '[]',     -- JSON array of missing skills
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id)  REFERENCES resumes(id)  ON DELETE CASCADE,
            FOREIGN KEY (posting_id) REFERENCES postings(id) ON DELETE CASCADE
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS skills (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL UNIQUE,       -- canonical skill, e.g. "JavaScript"
            alias   TEXT,                       -- optional alias, e.g. "JS"
            course_url  TEXT                    -- free course for the skill-gap report
        );
        """
    )

    conn.commit()

    # --- Migration: ensure postings has an `apply_url` column ---
    # Older databases may have the legacy `source_url` column; rename-by-copy so
    # no existing data is lost. New databases already have `apply_url`.
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(postings)")]
    if "apply_url" not in cols:
        conn.execute("ALTER TABLE postings ADD COLUMN apply_url TEXT")
        if "source_url" in cols:
            conn.execute("UPDATE postings SET apply_url = source_url "
                         "WHERE apply_url IS NULL")
        conn.commit()

    conn.close()


# ---------------------------------------------------------------------------
# Convenience helpers (used by app.py and teammates)
# ---------------------------------------------------------------------------

def add_posting(title, description, company=None, location=None,
                skills=None, apply_url=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO postings (title, company, location, description,
                                 skills_json, apply_url)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (title, company, location, description,
         json.dumps(skills or []), apply_url),
    )
    conn.commit()
    posting_id = cur.lastrowid
    conn.close()
    return posting_id


def add_resume(scrubbed_text, label=None, skills=None,
               target_role=None, consent=0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO resumes (label, scrubbed_text, skills_json,
                                target_role, consent)
           VALUES (?, ?, ?, ?, ?)""",
        (label, scrubbed_text, json.dumps(skills or []),
         target_role, int(consent)),
    )
    conn.commit()
    resume_id = cur.lastrowid
    conn.close()
    return resume_id


def get_resume(resume_id):
    """Return a single resume as a dict (with skills parsed), or None."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM resumes WHERE id = ?",
                       (resume_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    r = dict(row)
    r["skills"] = json.loads(r.get("skills_json") or "[]")
    return r


def save_match(resume_id, posting_id, score, gap=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO match_results (resume_id, posting_id, score, gap_json)
           VALUES (?, ?, ?, ?)""",
        (resume_id, posting_id, score, json.dumps(gap or [])),
    )
    conn.commit()
    conn.close()


def get_all_postings():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM postings").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def import_postings_csv(csv_path):
    """
    Import internship postings from a CSV file.

    Expected columns (header row, case-insensitive):
        title, company, location, description, skills, apply_url
      - `skills` is a semicolon- or comma-separated list.
      - `apply_url` is the REAL application link (leave blank if unknown;
        we never invent URLs).

    Returns the number of rows imported.
    """
    import csv

    count = 0
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        # Normalise headers to lowercase for forgiving matching.
        for raw in reader:
            row = {(k or "").strip().lower(): (v or "").strip()
                   for k, v in raw.items()}
            title = row.get("title")
            if not title:
                continue
            skills_raw = row.get("skills", "")
            sep = ";" if ";" in skills_raw else ","
            skills = [s.strip() for s in skills_raw.split(sep) if s.strip()]
            add_posting(
                title=title,
                description=row.get("description", ""),
                company=row.get("company") or None,
                location=row.get("location") or None,
                skills=skills,
                apply_url=row.get("apply_url") or None,
            )
            count += 1
    return count


def get_top_matches(resume_id, limit=3):
    conn = get_connection()
    rows = conn.execute(
        """SELECT m.score, m.gap_json, p.title, p.company, p.location
           FROM match_results m
           JOIN postings p ON p.id = m.posting_id
           WHERE m.resume_id = ?
           ORDER BY m.score DESC
           LIMIT ?""",
        (resume_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_course_map():
    """Return {skill_name: course_url} for the skill-gap report links."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT name, course_url FROM skills WHERE course_url IS NOT NULL"
    ).fetchall()
    conn.close()
    return {r["name"]: r["course_url"] for r in rows}


def cohort_skill_gaps(top_n=10):
    """Aggregate missing skills across all match_results for the dashboard."""
    conn = get_connection()
    rows = conn.execute("SELECT gap_json FROM match_results").fetchall()
    conn.close()

    counts = {}
    for r in rows:
        for skill in json.loads(r["gap_json"]):
            counts[skill] = counts.get(skill, 0) + 1

    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return ranked[:top_n]


if __name__ == "__main__":
    init_db()
    print(f"Initialised database at {DB_PATH}")
