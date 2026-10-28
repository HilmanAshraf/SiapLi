"""
SiapLI — Field taxonomy (new feature: "Explore My Preferred Field").

Maps a preferred field to:
  - the canonical skills most associated with it (for skill-gap suggestions)
  - keywords used to decide whether a posting belongs to the field

Used by Option 2 (field-first recommendations) in matching.py. This module is
additive — it does not change any existing behaviour.
"""

from __future__ import annotations

# field key -> {"label", "skills", "keywords"}
FIELDS = {
    "cybersecurity": {
        "label": "Cybersecurity",
        "skills": ["Cybersecurity", "Network Security", "Penetration Testing",
                   "Cryptography", "Networking", "Linux", "TCP/IP"],
        "keywords": ["security", "cyber", "penetration", "network security",
                     "cryptography", "vulnerability", "threat"],
    },
    "data_analytics": {
        "label": "Data Analytics",
        "skills": ["Data Analysis", "SQL", "Excel", "Power BI", "Tableau",
                   "Python", "Statistics", "Data Visualization"],
        "keywords": ["data analyst", "data analysis", "analytics", "power bi",
                     "tableau", "dashboard", "report", "statistics"],
    },
    "ai_ml": {
        "label": "AI / Machine Learning",
        "skills": ["Machine Learning", "Deep Learning", "Python",
                   "Natural Language Processing", "Computer Vision",
                   "TensorFlow", "PyTorch", "scikit-learn", "Data Science"],
        "keywords": ["machine learning", "deep learning", "ai engineer",
                     "artificial intelligence", "nlp", "computer vision",
                     "tensorflow", "pytorch", "model", "data science"],
    },
    "software_development": {
        "label": "Software Development",
        "skills": ["Python", "Java", "JavaScript", "React", "Node.js",
                   "Flask", "Django", "SQL", "Git", "REST API", "Docker"],
        "keywords": ["software", "developer", "backend", "frontend",
                     "full stack", "web", "api", "application", "engineer"],
    },
}


def field_choices():
    """Return [(key, label), ...] for building the selection UI."""
    return [(k, v["label"]) for k, v in FIELDS.items()]


def get_field(field_key):
    """Return the field config dict, or None if the key is unknown."""
    return FIELDS.get(field_key)


def posting_field_relevance(posting, field_key):
    """
    Score 0..100 for how well a posting belongs to a field.

    Combines two signals:
      - keyword hits in the posting title/description
      - overlap between the posting's required skills and the field's skills
    """
    field = FIELDS.get(field_key)
    if not field:
        return 0.0

    text = (posting.get("title", "") + " " +
            posting.get("description", "")).lower()

    # 1. Keyword signal
    keywords = field["keywords"]
    kw_hits = sum(1 for kw in keywords if kw in text)
    kw_score = kw_hits / len(keywords) if keywords else 0.0

    # 2. Skill-overlap signal
    field_skills = {s.lower() for s in field["skills"]}
    post_skills = {s.lower() for s in posting.get("skills", [])}
    overlap = len(field_skills & post_skills)
    skill_score = overlap / len(field_skills) if field_skills else 0.0

    # Weight keywords and skills evenly, scale to 0..100.
    return round((0.5 * kw_score + 0.5 * skill_score) * 100, 1)
