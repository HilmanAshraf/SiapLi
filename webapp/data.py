"""
SiapLI editorial app — sample data + classification logic.

Classification rule (MUST match the JS in ledger.js exactly):
  ready  : student has ALL required skills
  grow   : missing <= 2 required skills AND has >= half of them
  else   : unmatched
"""

# --- Fields -----------------------------------------------------------------
FIELDS = [
    ("web", "Web Development"),
    ("data", "Data & Analytics"),
    ("network", "Networking & Security"),
]

# --- Courses: skill -> {url, time} (free, real-ish homepages) ---------------
COURSES = {
    "HTML": {"url": "https://developer.mozilla.org/en-US/docs/Learn/HTML", "time": "1 week"},
    "CSS": {"url": "https://web.dev/learn/css/", "time": "1 week"},
    "JavaScript": {"url": "https://www.freecodecamp.org/learn/", "time": "3 weeks"},
    "React": {"url": "https://react.dev/learn", "time": "2 weeks"},
    "Git": {"url": "https://learngitbranching.js.org/", "time": "3 days"},
    "Python": {"url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "time": "3 weeks"},
    "SQL": {"url": "https://www.khanacademy.org/computing/computer-programming/sql", "time": "1 week"},
    "Excel": {"url": "https://support.microsoft.com/excel", "time": "1 week"},
    "Power BI": {"url": "https://learn.microsoft.com/training/powerplatform/power-bi", "time": "2 weeks"},
    "Data Analysis": {"url": "https://www.freecodecamp.org/learn/data-analysis-with-python/", "time": "3 weeks"},
    "Pandas": {"url": "https://pandas.pydata.org/docs/getting_started/", "time": "1 week"},
    "Statistics": {"url": "https://www.khanacademy.org/math/statistics-probability", "time": "4 weeks"},
    "Linux": {"url": "https://linuxjourney.com/", "time": "2 weeks"},
    "Networking": {"url": "https://www.professormesser.com/network-plus/", "time": "3 weeks"},
    "TCP/IP": {"url": "https://www.cloudflare.com/learning/ddos/glossary/tcp-ip/", "time": "4 days"},
    "Network Security": {"url": "https://www.cybrary.it/", "time": "3 weeks"},
    "Cryptography": {"url": "https://www.coursera.org/learn/crypto", "time": "4 weeks"},
    "Bash": {"url": "https://www.learnshell.org/", "time": "1 week"},
    "Communication": {"url": "https://www.coursera.org/learn/wharton-communication-skills", "time": "ongoing"},
    "Teamwork": {"url": "https://www.coursera.org/learn/teamwork-skills-effective-communication", "time": "ongoing"},
}

# --- Internship postings ----------------------------------------------------
# field, title, company, required skills
POSTINGS = [
    {"id": 1, "field": "web", "title": "Frontend Developer Intern",
     "company": "PixelCraft", "skills": ["HTML", "CSS", "JavaScript", "Git"]},
    {"id": 2, "field": "web", "title": "Web Developer Intern",
     "company": "SiteForge", "skills": ["HTML", "CSS", "JavaScript", "React", "Git"]},
    {"id": 3, "field": "web", "title": "Junior Web Assistant Intern",
     "company": "StartRight", "skills": ["HTML", "CSS", "Git"]},
    {"id": 4, "field": "web", "title": "Full Stack Intern",
     "company": "BuildIt", "skills": ["HTML", "CSS", "JavaScript", "React", "SQL", "Git"]},
    {"id": 5, "field": "data", "title": "Data Analyst Intern",
     "company": "InsightWorks", "skills": ["Python", "SQL", "Excel", "Data Analysis"]},
    {"id": 6, "field": "data", "title": "Business Intelligence Intern",
     "company": "ClearMetrics", "skills": ["Power BI", "SQL", "Excel", "Communication"]},
    {"id": 7, "field": "data", "title": "Data Science Intern",
     "company": "QuantEdge", "skills": ["Python", "Pandas", "Statistics", "Data Analysis"]},
    {"id": 8, "field": "data", "title": "Data Entry & Reporting Intern",
     "company": "InsightWorks", "skills": ["Excel", "SQL", "Communication"]},
    {"id": 9, "field": "network", "title": "Network Support Intern",
     "company": "NetLink", "skills": ["Networking", "TCP/IP", "Linux"]},
    {"id": 10, "field": "network", "title": "IT Support Intern",
     "company": "HelpDesk", "skills": ["Linux", "Networking", "Communication"]},
    {"id": 11, "field": "network", "title": "Cybersecurity Intern",
     "company": "SecureNet", "skills": ["Network Security", "Cryptography", "Linux", "Networking"]},
    {"id": 12, "field": "network", "title": "Systems Admin Intern",
     "company": "CoreOps", "skills": ["Linux", "Bash", "Networking"]},
]

# --- Sample student profiles for the hero ledger ----------------------------
SAMPLE_PROFILES = [
    {"id": "web", "label": "Web",
     "skills": ["HTML", "CSS", "Git", "Communication"]},
    {"id": "data", "label": "Data",
     "skills": ["Python", "SQL", "Excel", "Communication"]},
    {"id": "network", "label": "Network",
     "skills": ["Linux", "Networking", "Communication"]},
]


# --- Classification (mirror in ledger.js) -----------------------------------
def classify(student_skills, required):
    have = [s for s in required if s in set(student_skills)]
    miss = [s for s in required if s not in set(student_skills)]
    if not miss:
        return "ready"
    if len(miss) <= 2 and len(have) >= len(required) / 2:
        return "grow"
    return "unmatched"


def match_skills_to_postings(student_skills):
    ready, grow, unmatched = [], [], []
    sset = set(student_skills)
    for p in POSTINGS:
        required = p["skills"]
        have = [s for s in required if s in sset]
        miss = [s for s in required if s not in sset]
        status = classify(student_skills, required)
        score = round(len(have) / len(required) * 100) if required else 0
        item = {"posting": p, "have": have, "miss": miss, "score": score}
        if status == "ready":
            ready.append(item)
        elif status == "grow":
            grow.append(item)
        else:
            unmatched.append(item)
    ready.sort(key=lambda m: m["score"], reverse=True)
    grow.sort(key=lambda m: m["score"], reverse=True)
    return ready, grow, unmatched


# --- Cohort dashboard (anonymous, synthetic) --------------------------------
# Synthetic cohort: counts of students and skill coverage per field.
_COHORT = {
    "web": {"students": 48, "ready": 31, "growing": 14,
            "gaps": [("JavaScript", 22, 14), ("React", 30, 9), ("Git", 12, 36)]},
    "data": {"students": 37, "ready": 20, "growing": 13,
             "gaps": [("SQL", 25, 18), ("Python", 28, 15), ("Statistics", 31, 8)]},
    "network": {"students": 21, "ready": 9, "growing": 8,
                "gaps": [("Linux", 16, 10), ("Network Security", 19, 4),
                         ("TCP/IP", 14, 9)]},
}


def cohort_stats(field="all"):
    """Return big numbers + skill-gap bars + table. Hide groups under 5."""
    keys = [field] if field in _COHORT else list(_COHORT.keys())
    students = ready = growing = 0
    gaps = {}
    table = []
    for k in keys:
        c = _COHORT[k]
        if c["students"] < 5:
            continue
        students += c["students"]
        ready += c["ready"]
        growing += c["growing"]
        label = dict(FIELDS)[k]
        for skill, needed, have in c["gaps"]:
            agg = gaps.setdefault(skill, [0, 0])
            agg[0] += needed
            agg[1] += have
        table.append({
            "field": label, "students": c["students"],
            "ready": c["ready"], "growing": c["growing"],
            "status": ("healthy" if c["ready"] / c["students"] >= 0.55
                       else "watch" if c["ready"] / c["students"] >= 0.35
                       else "at risk"),
        })
    gap_bars = [{"skill": s, "needed": v[0], "have": v[1]}
                for s, v in sorted(gaps.items(), key=lambda kv: kv[1][0],
                                   reverse=True)]
    pct_ready = round(ready / students * 100) if students else 0
    return {
        "students": students, "ready": ready, "growing": growing,
        "pct_ready": pct_ready, "gaps": gap_bars, "table": table,
    }
