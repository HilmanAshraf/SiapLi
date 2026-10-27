"""
SiapLI — NLP stubs (owned by P2 on Day 1/2).

P1 provides these stubs so the Flask app runs end-to-end TODAY.
P2 replaces the internals with:
  - real text extraction (pdfplumber / python-docx)
  - spaCy PhraseMatcher skill extraction against the curated skills dict
  - full PII scrubbing (spaCy NER + regex)

Keep the function SIGNATURES stable so app.py doesn't need to change.
"""

from __future__ import annotations

import re

# A tiny starter skills list so extraction returns something today.
# P2: replace with the ~400-term curated dictionary loaded from the DB.
_STARTER_SKILLS = [
    "python", "java", "javascript", "sql", "html", "css", "react",
    "flask", "django", "git", "docker", "excel", "communication",
    "teamwork", "machine learning", "data analysis", "c++", "linux",
]


def extract_text(file_path: str) -> str:
    """
    Extract raw text from an uploaded resume.
    STUB: reads plain text. P2 adds PDF/DOCX support.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def extract_skills(text: str) -> list:
    """
    Return skills found in the text.
    STUB: case-insensitive substring match on a starter list.
    P2: replace with spaCy PhraseMatcher + alias handling.
    """
    lower = text.lower()
    found = [s for s in _STARTER_SKILLS if s in lower]
    return sorted(set(found))


def scrub_pii(text: str) -> str:
    """
    Remove obvious PII before any external LLM call or DB storage.
    Covers email, Malaysian IC, and phone. P2: add spaCy NER for names/places.
    """
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[EMAIL]", text)
    text = re.sub(r"\b\d{6}-\d{2}-\d{4}\b", "[IC]", text)
    text = re.sub(r"\b(?:\+?60|0)\d{1,2}-?\d{7,8}\b", "[PHONE]", text)
    return text
