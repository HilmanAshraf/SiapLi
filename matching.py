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


def matched_skills(resume_skills, job_skills) -> list:
    """Skills required by the job that the resume already has."""
    return sorted(set(job_skills) & set(resume_skills))


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


# ---------------------------------------------------------------------------
# New feature: two recommendation options
# ---------------------------------------------------------------------------

def rank_by_skills(resume_text, resume_skills, postings, top_n=5):
    """
    OPTION 1 — "Match My Skills".
    Prioritise postings where the student's EXISTING skills cover the most of
    what the role requires. Semantic text similarity breaks ties.

    Returns list of dicts:
        {posting, score, matched, gap, skill_coverage}
    """
    results = []
    for p in postings:
        required = p.get("skills", [])
        matched = matched_skills(resume_skills, required)
        gap = skill_gap(resume_skills, required)

        coverage = (len(matched) / len(required) * 100) if required else 0.0
        semantic = match_score(resume_text, p["description"])

        # Skills-first: coverage dominates, semantic similarity is a tie-breaker.
        score = round(0.8 * coverage + 0.2 * semantic, 1)

        results.append({
            "posting": p,
            "score": score,
            "matched": matched,
            "gap": gap,
            "skill_coverage": round(coverage, 1),
        })

    results.sort(key=lambda x: (x["score"], x["skill_coverage"]), reverse=True)
    return results[:top_n]


def rank_by_field(resume_skills, postings, field_key, top_n=5):
    """
    OPTION 2 — "Explore My Preferred Field".
    Prioritise postings that belong to the chosen field, EVEN IF the student is
    missing some or all required skills. Field relevance dominates the ranking;
    we still surface matched vs missing skills so the student sees the gap.

    Returns list of dicts:
        {posting, score, field_relevance, matched, gap, skill_coverage}
    """
    import fields  # local import to avoid a hard dependency cycle

    results = []
    for p in postings:
        relevance = fields.posting_field_relevance(p, field_key)
        if relevance <= 0:
            continue  # not in this field

        required = p.get("skills", [])
        matched = matched_skills(resume_skills, required)
        gap = skill_gap(resume_skills, required)
        coverage = (len(matched) / len(required) * 100) if required else 0.0

        # Field-first: relevance dominates; skill coverage is a gentle booster
        # so a student isn't blocked by missing skills.
        score = round(0.8 * relevance + 0.2 * coverage, 1)

        results.append({
            "posting": p,
            "score": score,
            "field_relevance": relevance,
            "matched": matched,
            "gap": gap,
            "skill_coverage": round(coverage, 1),
        })

    results.sort(key=lambda x: (x["field_relevance"], x["score"]), reverse=True)
    return results[:top_n]


# ---------------------------------------------------------------------------
# New feature: Target-role recommendations
#   Option 1 — Exact Target Role Match (single best posting for the role)
#   Option 2 — Alternative Related Roles (data-grounded alternatives)
# All logic below uses ONLY the skills stored on each posting. It never invents
# vacancies, courses, or requirements.
# ---------------------------------------------------------------------------

def evaluate_posting(resume_skills, posting):
    """
    Compute the skill picture for one posting against the student's skills.
    Returns {posting, matched, gap, skill_coverage, score}.
    `score` here is the % of the role's required skills the student already has.
    """
    required = posting.get("skills", [])
    matched = matched_skills(resume_skills, required)
    gap = skill_gap(resume_skills, required)
    coverage = (len(matched) / len(required) * 100) if required else 0.0
    return {
        "posting": posting,
        "matched": matched,
        "gap": gap,
        "skill_coverage": round(coverage, 1),
        "score": round(coverage, 1),
    }


def exact_target_match(resume_skills, postings, target_id):
    """
    OPTION 1 — Exact Target Role Match.
    Return the single posting whose id == target_id, with matched/missing
    skills, or None if that posting no longer exists.
    """
    for p in postings:
        if p.get("id") == target_id:
            return evaluate_posting(resume_skills, p)
    return None


def alternative_roles(resume_skills, postings, target_id, top_n=4,
                      min_relatedness=1):
    """
    OPTION 2 — Alternative Related Roles.

    An alternative is a DIFFERENT posting that:
      1. is RELATED to the target role — it shares at least `min_relatedness`
         required skills with the target role (verified from the listings), and
      2. does NOT make the student's target-role skill GAPS mandatory — none of
         the skills the student is missing for the target are required here, and
      3. FITS the student better — the student covers a higher share of this
         role's required skills than they do of the target role.

    Returns a list of dicts, best fit first:
        {posting, matched, gap, skill_coverage, shared_with_target,
         relatedness, avoids_target_gaps}
    """
    target = next((p for p in postings if p.get("id") == target_id), None)
    if target is None:
        return []

    target_required = set(target.get("skills", []))
    target_gap = set(skill_gap(resume_skills, target.get("skills", [])))

    alternatives = []
    for p in postings:
        if p.get("id") == target_id:
            continue  # skip the target itself

        required = set(p.get("skills", []))
        shared = sorted(required & target_required)      # relatedness evidence
        if len(shared) < min_relatedness:
            continue  # not related enough to the target role

        # Must NOT require the exact skills blocking the student in the target.
        if required & target_gap:
            continue

        info = evaluate_posting(resume_skills, p)
        target_coverage = (len(target_required - target_gap)
                           / len(target_required) * 100) if target_required else 0.0
        if info["skill_coverage"] <= target_coverage:
            continue  # not a better fit than the target itself

        info["shared_with_target"] = shared
        info["relatedness"] = len(shared)
        info["avoids_target_gaps"] = sorted(target_gap)
        alternatives.append(info)

    # Best fit first; then most related to the target.
    alternatives.sort(key=lambda x: (x["skill_coverage"], x["relatedness"]),
                      reverse=True)
    return alternatives[:top_n]
