"""
SiapLI — AI resume feedback (privacy-safe, rule-based).

Generates concrete, role-aware suggestions to improve a resume for a chosen
target role. This fulfils the pitch promise of "AI feedback to improve the
resume for a chosen role".

Design choices (responsible AI):
  - Works on SCRUBBED resume text only — never sees raw PII.
  - No external LLM call, so no student data leaves the app and there is no API
    cost or network dependency. The logic is transparent and explainable, which
    is exactly the "explainable, not black-box" angle in the pitch.
  - If an external LLM is ever added later, generate_feedback()'s signature can
    stay the same; only the internals change.

Returns a list of feedback items, each:
    {"type": "strength"|"gap"|"tip", "title": str, "detail": str,
     "skill": str|None, "course_url": str|None}
"""

from __future__ import annotations

import re

# Common resume quality signals we can check in scrubbed text.
_ACTION_VERBS = [
    "built", "designed", "developed", "led", "created", "implemented",
    "analysed", "analyzed", "improved", "automated", "launched", "managed",
    "optimised", "optimized", "delivered", "deployed", "tested",
]


def generate_feedback(scrubbed_text, resume_skills, target_posting,
                      course_map=None):
    """
    Produce resume-improvement feedback for a specific target role.

    Args:
        scrubbed_text:   the PII-scrubbed resume text
        resume_skills:   list of skills detected in the resume
        target_posting:  dict with "title" and "skills" (required skills)
        course_map:      optional {skill: course_url} for gap suggestions

    Returns a list of feedback dicts (see module docstring).
    """
    course_map = course_map or {}
    resume_set = set(resume_skills)
    required = target_posting.get("skills", [])
    title = target_posting.get("title", "this role")

    matched = [s for s in required if s in resume_set]
    gaps = [s for s in required if s not in resume_set]

    items = []

    # 1. Strengths — reinforce what already aligns.
    if matched:
        items.append({
            "type": "strength",
            "title": "You already match key requirements",
            "detail": ("Your resume shows " + _join(matched) + ", which "
                       + ("is" if len(matched) == 1 else "are")
                       + " directly relevant to " + title + ". Make "
                       "sure " + ("it is" if len(matched) == 1 else "these are")
                       + " near the top and backed by a concrete example."),
            "skill": None, "course_url": None,
        })

    # 2. Gaps — turn each missing skill into an actionable step.
    for skill in gaps:
        items.append({
            "type": "gap",
            "title": "Add or build: " + skill,
            "detail": (title + " expects " + skill + ". Learn the basics, then "
                       "add a small project or coursework line that uses it so "
                       "it appears in both your skills and experience."),
            "skill": skill,
            "course_url": course_map.get(skill),
        })

    # 3. Writing-quality tips derived from the actual text.
    items.extend(_quality_tips(scrubbed_text))

    # 4. Readiness-oriented closing tip.
    coverage = round(len(matched) / len(required) * 100, 1) if required else 0.0
    if coverage >= 70:
        close = ("You're a strong fit (" + str(coverage) + "% of required "
                 "skills). Focus on quantifying impact and you're ready to apply.")
    elif coverage >= 40:
        close = ("You're a moderate fit (" + str(coverage) + "%). Close one or "
                 "two gaps above and you'll be competitive for " + title + ".")
    else:
        close = ("You're an early fit (" + str(coverage) + "%). Use the courses "
                 "above to build the core skills, or check the alternative "
                 "roles that match your current skills better.")
    items.append({
        "type": "tip", "title": "Overall readiness", "detail": close,
        "skill": None, "course_url": None,
    })

    return items


def _quality_tips(text):
    """Light, transparent checks on the scrubbed resume text."""
    tips = []
    lower = text.lower()

    # Quantified impact (numbers/percentages) is a classic resume win.
    if not re.search(r"\d", text):
        tips.append({
            "type": "tip",
            "title": "Quantify your impact",
            "detail": ("Your resume has no numbers. Add measurable results "
                       "(e.g. 'improved load time by 30%', 'handled 200+ "
                       "records') to make achievements concrete."),
            "skill": None, "course_url": None,
        })

    # Strong action verbs.
    if not any(v in lower for v in _ACTION_VERBS):
        tips.append({
            "type": "tip",
            "title": "Start bullet points with action verbs",
            "detail": ("Lead each experience line with a strong verb such as "
                       "Built, Designed, Led, or Automated to show ownership."),
            "skill": None, "course_url": None,
        })

    # Length / detail heuristic.
    word_count = len(text.split())
    if word_count < 80:
        tips.append({
            "type": "tip",
            "title": "Add more detail",
            "detail": ("Your resume is quite short. Expand on projects, "
                       "coursework, and responsibilities so reviewers can see "
                       "your skills in context."),
            "skill": None, "course_url": None,
        })

    return tips


def _join(items):
    """Human-friendly join: 'A', 'A and B', 'A, B and C'."""
    items = list(items)
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return items[0] + " and " + items[1]
    return ", ".join(items[:-1]) + " and " + items[-1]
