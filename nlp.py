"""
SiapLI — NLP module (P2, Day 1 deliverable).

Replaces nlp_stub.py with real implementations:
  - extract_text():  PDF (pdfplumber) + DOCX (python-docx) + TXT
  - extract_skills(): spaCy PhraseMatcher over a curated skills dictionary,
                      with alias support; falls back to substring matching
  - scrub_pii():      regex (email / Malaysian IC / phone) + spaCy NER
                      (PERSON, GPE) for names and places

Design note
-----------
spaCy and the heavy parsers are OPTIONAL at runtime. If a library or model is
not installed, the function degrades gracefully so the whole app still runs.
This keeps teammates unblocked before everyone has run the full install.

Keep the signatures identical to nlp_stub.py so app.py can switch by changing
one import line:  `import nlp as nlp`  instead of `import nlp_stub as nlp`.
"""

from __future__ import annotations

import re

from skills_data import SKILLS, SKILL_ALIASES

# ---------------------------------------------------------------------------
# Lazy spaCy loader (optional dependency)
# ---------------------------------------------------------------------------
_nlp_model = None
_matcher = None


def _load_spacy():
    """Load spaCy + PhraseMatcher once. Returns (nlp, matcher) or (None, None)."""
    global _nlp_model, _matcher
    if _nlp_model is not None:
        return _nlp_model, _matcher
    try:
        import spacy
        from spacy.matcher import PhraseMatcher

        _nlp_model = spacy.load("en_core_web_sm")
        _matcher = PhraseMatcher(_nlp_model.vocab, attr="LOWER")

        # Build patterns from canonical skills + their aliases.
        for skill in SKILLS:
            terms = [skill] + SKILL_ALIASES.get(skill, [])
            patterns = [_nlp_model.make_doc(t) for t in terms]
            _matcher.add(skill, patterns)
        return _nlp_model, _matcher
    except Exception:
        _nlp_model, _matcher = None, None
        return None, None


# ---------------------------------------------------------------------------
# 1. Text extraction
# ---------------------------------------------------------------------------
def extract_text(file_path: str) -> str:
    """Extract raw text from a PDF, DOCX, or TXT resume."""
    lower = file_path.lower()
    if lower.endswith(".pdf"):
        return _extract_pdf(file_path)
    if lower.endswith(".docx"):
        return _extract_docx(file_path)
    return _extract_txt(file_path)


def _extract_pdf(path: str) -> str:
    try:
        import pdfplumber

        parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                parts.append(page.extract_text() or "")
        return "\n".join(parts)
    except Exception:
        return _extract_txt(path)  # best-effort fallback


def _extract_docx(path: str) -> str:
    try:
        import docx

        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return _extract_txt(path)


def _extract_txt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# 2. Skill extraction
# ---------------------------------------------------------------------------
def extract_skills(text: str) -> list:
    """
    Return canonical skills found in the text.
    Uses spaCy PhraseMatcher if available, else substring matching on aliases.
    """
    model, matcher = _load_spacy()
    if model is not None and matcher is not None:
        doc = model(text)
        found = {model.vocab.strings[mid] for mid, _, _ in matcher(doc)}
        return sorted(found)
    return _substring_skills(text)


def _substring_skills(text: str) -> list:
    """Fallback: canonical skill matched if it or any alias appears in text."""
    lower = text.lower()
    found = set()
    for skill in SKILLS:
        terms = [skill] + SKILL_ALIASES.get(skill, [])
        if any(_term_in(t.lower(), lower) for t in terms):
            found.add(skill)
    return sorted(found)


def _term_in(term: str, text: str) -> bool:
    """Word-boundary-ish match to avoid 'r' matching inside 'react'."""
    return re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])",
                     text) is not None


# ---------------------------------------------------------------------------
# 3. PII scrubbing (Responsible AI)
# ---------------------------------------------------------------------------
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_IC_RE = re.compile(r"\b\d{6}-\d{2}-\d{4}\b")              # Malaysian IC
_PHONE_RE = re.compile(r"\b(?:\+?60|0)\d{1,2}-?\d{7,8}\b")  # MY phone
_URL_RE = re.compile(r"https?://\S+")


def scrub_pii(text: str) -> str:
    """
    Remove PII before storage or any external LLM call.
    Regex handles email / IC / phone / URL; spaCy NER removes PERSON & GPE.
    """
    text = _EMAIL_RE.sub("[EMAIL]", text)
    text = _IC_RE.sub("[IC]", text)
    text = _PHONE_RE.sub("[PHONE]", text)
    text = _URL_RE.sub("[URL]", text)

    model, _ = _load_spacy()
    if model is not None:
        doc = model(text)
        # Replace named people and places (right-to-left to keep spans valid).
        for ent in reversed(doc.ents):
            if ent.label_ == "PERSON":
                text = text[:ent.start_char] + "[NAME]" + text[ent.end_char:]
            elif ent.label_ == "GPE":
                text = text[:ent.start_char] + "[PLACE]" + text[ent.end_char:]
    return text
