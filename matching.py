"""
SiapLI — Matching engine (P1).

Uses sentence-transformers embeddings + cosine similarity to score a resume
against each internship posting. The model loads lazily so the app starts fast
and so teammates who don't have the model installed can still run the rest.

If sentence-transformers is unavailable, we fall back to a simple keyword
overlap score so the end-to-end flow still works during the hackathon.
"""

from __future__ import annotations

_model = None


def _load_model():
    """Load the embedding model once (lazy)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def match_score(resume_text: str, job_text: str) -> float:
    """Return a 0..100 match percentage between a resume and a job posting."""
    try:
        from sentence_transformers import util

        model = _load_model()
        emb = model.encode([resume_text, job_text], convert_to_tensor=True)
        sim = util.cos_sim(emb[0], emb[1]).item()  # -1..1
        return round(max(0.0, sim) * 100, 1)
    except Exception:
        # Fallback: keyword overlap so the demo never hard-fails.
        return _keyword_overlap_score(resume_text, job_text)


def _keyword_overlap_score(resume_text: str, job_text: str) -> float:
    r = set(resume_text.lower().split())
    j = set(job_text.lower().split())
    if not j:
        return 0.0
    return round(len(r & j) / len(j) * 100, 1)


def skill_gap(resume_skills, job_skills) -> list:
    """Skills required by the job but missing from the resume."""
    return sorted(set(job_skills) - set(resume_skills))


def rank_postings(resume_text, resume_skills, postings, top_n=3):
    """
    Score a resume against every posting and return the top N.

    Each posting is a dict with at least `description` and `skills` (list).
    Returns a list of dicts: {posting, score, gap}.
    """
    scored = []
    for p in postings:
        score = match_score(resume_text, p["description"])
        gap = skill_gap(resume_skills, p.get("skills", []))
        scored.append({"posting": p, "score": score, "gap": gap})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
