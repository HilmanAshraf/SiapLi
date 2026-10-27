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
            source_url    TEXT,
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
    conn.close()


# ---------------------------------------------------------------------------
# Convenience helpers (used by app.py and teammates)
# ---------------------------------------------------------------------------

def add_posting(title, description, company=None, location=None,
                skills=None, source_url=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO postings (title, company, location, description,
                                 skills_json, source_url)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (title, company, location, description,
         json.dumps(skills or []), source_url),
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
