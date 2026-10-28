"""
Lightweight sample profiles + field labels for the interactive hero ledger.

The ledger is a live, in-browser demo widget — it uses these small sample
profiles and the real postings/courses (passed in from app.py) so it can
recompute instantly without hitting the backend. The actual resume analysis on
/check and /results uses the real engine (nlp.py / matching.py / db.py).
"""

LEDGER_FIELDS = [
    ("web", "Web Development"),
    ("data", "Data & Analytics"),
    ("network", "Networking & Security"),
]

SAMPLE_PROFILES = [
    {"id": "web", "label": "Web",
     "skills": ["HTML", "CSS", "Git", "Communication"]},
    {"id": "data", "label": "Data",
     "skills": ["Python", "SQL", "Excel", "Communication"]},
    {"id": "network", "label": "Network",
     "skills": ["Linux", "Networking", "Communication"]},
]
