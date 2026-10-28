"""
SiapLI — Seed sample data (P3, Day 1 deliverable).

Loads a realistic Malaysian internship dataset so the app and the cohort
dashboard look real in the demo:
  - ~20 internship postings (varied roles, real MY locations)
  - ~12 anonymised sample resumes (run through PII scrub, then matched)
  - a skill -> free-course mapping for the skill-gap report

P3 extends this toward ~200 postings / ~30 resumes on Day 2 by appending to
the POSTINGS / SAMPLE_RESUMES lists (same shape).

Run:
    python seed_data.py
"""

import json

import db
import nlp
import matching

# ---------------------------------------------------------------------------
# Internship postings (Malaysian context)
# ---------------------------------------------------------------------------
POSTINGS = [
    ("Software Engineering Intern", "TechNova Sdn Bhd", "Kuala Lumpur",
     "Build and test web features using Python and Flask. Work with SQL "
     "databases and Git. Collaborate in an Agile team. React is a plus.",
     ["Python", "Flask", "SQL", "Git", "React", "Teamwork", "Agile"]),
    ("Data Analyst Intern", "InsightWorks", "Petaling Jaya",
     "Analyse datasets with Python and SQL. Build dashboards in Power BI and "
     "Excel. Present findings clearly. Strong data analysis skills needed.",
     ["Python", "SQL", "Power BI", "Excel", "Data Analysis", "Communication"]),
    ("Frontend Developer Intern", "PixelCraft", "George Town",
     "Develop responsive UIs with HTML, CSS and JavaScript. Use React and "
     "Git. Figma handoff experience valued. Teamwork essential.",
     ["HTML", "CSS", "JavaScript", "React", "Git", "Figma", "Teamwork"]),
    ("Machine Learning Intern", "NeuronLabs MY", "Cyberjaya",
     "Support ML projects in Python. Apply machine learning and deep learning "
     "with TensorFlow. Linux and Git experience preferred.",
     ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "Linux", "Git"]),
    ("Backend Developer Intern", "CloudReach", "Kuala Lumpur",
     "Build REST APIs with Node.js and Express. Work with PostgreSQL and "
     "Docker. Deploy on AWS. Understanding of CI/CD a bonus.",
     ["Node.js", "Express", "REST API", "PostgreSQL", "Docker", "AWS", "CI/CD"]),
    ("Mobile App Developer Intern", "AppVentures", "Shah Alam",
     "Develop cross-platform apps with Flutter and Dart. Integrate Firebase. "
     "Use Git for version control. Attention to detail important.",
     ["Flutter", "Dart", "Firebase", "Git", "Attention to Detail"]),
    ("DevOps Intern", "ScaleOps", "Cyberjaya",
     "Assist with CI/CD pipelines using Jenkins and Docker. Manage Linux "
     "servers and Kubernetes. Scripting in Bash required.",
     ["CI/CD", "Jenkins", "Docker", "Linux", "Kubernetes", "Bash"]),
    ("UI/UX Design Intern", "DesignHive", "Kuala Lumpur",
     "Design user interfaces in Figma and Adobe XD. Conduct usability "
     "research. Collaborate with developers. Strong creativity needed.",
     ["UI/UX Design", "Figma", "Adobe XD", "Creativity", "Collaboration"]),
    ("Cybersecurity Intern", "SecureNet MY", "Putrajaya",
     "Support security assessments and penetration testing. Study network "
     "security and cryptography. Linux familiarity required.",
     ["Cybersecurity", "Penetration Testing", "Network Security", "Cryptography", "Linux"]),
    ("Data Science Intern", "QuantEdge", "Petaling Jaya",
     "Work on data science projects using Python, Pandas and scikit-learn. "
     "Build models and visualise results with Matplotlib. Statistics needed.",
     ["Python", "Data Science", "Pandas", "scikit-learn", "Matplotlib", "Statistics"]),
    ("Full Stack Developer Intern", "BuildIt Studios", "Johor Bahru",
     "Work across React frontend and Django backend. Use PostgreSQL and Git. "
     "Deploy with Docker. Problem solving mindset valued.",
     ["React", "Django", "PostgreSQL", "Git", "Docker", "Problem Solving"]),
    ("Digital Marketing Intern", "GrowthLab", "Kuala Lumpur",
     "Run digital marketing campaigns and SEO. Create content and analyse "
     "performance. Strong communication and creativity needed.",
     ["Digital Marketing", "SEO", "Content Writing", "Communication", "Creativity"]),
    ("Cloud Engineer Intern", "SkyStack", "Cyberjaya",
     "Deploy services on AWS and Azure. Use Terraform and Docker. Linux and "
     "networking fundamentals required.",
     ["AWS", "Azure", "Terraform", "Docker", "Linux", "Networking"]),
    ("QA / Test Engineer Intern", "QualityFirst", "Penang",
     "Write unit tests and automated tests with Selenium. Use Postman for API "
     "testing. Attention to detail and problem solving required.",
     ["Unit Testing", "Selenium", "Postman", "Attention to Detail", "Problem Solving"]),
    ("Business Analyst Intern", "StrategyWorks", "Kuala Lumpur",
     "Gather requirements and document processes. Analyse data in Excel. Use "
     "Jira for tracking. Communication and critical thinking needed.",
     ["Business Analysis", "Excel", "Jira", "Communication", "Critical Thinking"]),
    ("AI Engineer Intern", "VisionAI", "Cyberjaya",
     "Build NLP and computer vision prototypes in Python with PyTorch. Use "
     "Git. Deep learning knowledge preferred.",
     ["Python", "Natural Language Processing", "Computer Vision", "PyTorch", "Git", "Deep Learning"]),
    ("Database Administrator Intern", "DataVault", "Shah Alam",
     "Maintain MySQL and PostgreSQL databases. Write SQL queries and optimise "
     "performance. Linux experience valued.",
     ["MySQL", "PostgreSQL", "SQL", "Linux", "Attention to Detail"]),
    ("Game Developer Intern", "PlayForge", "Kuala Lumpur",
     "Develop game features in C# and Unity. Use Git. Creativity and teamwork "
     "essential.",
     ["C#", "Git", "Creativity", "Teamwork", "Problem Solving"]),
    ("Graphic Design Intern", "CreativeDen", "George Town",
     "Produce graphics and videos using design tools. Edit video content. "
     "Strong creativity and attention to detail required.",
     ["Graphic Design", "Video Editing", "Creativity", "Attention to Detail"]),
    ("IT Support Intern", "HelpDesk Solutions", "Kuala Lumpur",
     "Provide technical support, manage Windows and Linux systems, and handle "
     "networking issues. Communication and problem solving needed.",
     ["Linux", "Networking", "Communication", "Problem Solving", "Time Management"]),
]

# ---------------------------------------------------------------------------
# Anonymised sample resumes (free text). These are synthetic — no real PII.
# They are still run through scrub_pii() to prove the pipeline works.
# ---------------------------------------------------------------------------
SAMPLE_RESUMES = [
    ("R-001", "Software Engineering Intern",
     "Final year CS student. Built web apps with Python, Flask and SQL. "
     "Comfortable with Git and teamwork. Some React experience."),
    ("R-002", "Data Analyst Intern",
     "Statistics undergraduate. Strong in Excel and SQL. Learning Python for "
     "data analysis. Good communication skills."),
    ("R-003", "Frontend Developer Intern",
     "Built several websites with HTML, CSS and JavaScript. Learning React. "
     "Used Git and worked in a team project."),
    ("R-004", "Machine Learning Intern",
     "Python developer interested in machine learning. Used scikit-learn and "
     "Pandas. Familiar with Linux and Git."),
    ("R-005", "Backend Developer Intern",
     "Built APIs with Node.js and Express. Worked with MongoDB. Learning "
     "Docker and AWS. Problem solving focused."),
    ("R-006", "Mobile App Developer Intern",
     "Developed a Flutter app for a university project using Dart and "
     "Firebase. Used Git. Detail oriented."),
    ("R-007", "Data Science Intern",
     "Data enthusiast skilled in Python, Pandas and Matplotlib. Basic "
     "statistics. Some machine learning exposure."),
    ("R-008", "UI/UX Design Intern",
     "Design student using Figma daily. Interest in UI/UX design. Creative "
     "and collaborative. Learning Adobe XD."),
    ("R-009", "Full Stack Developer Intern",
     "Comfortable with React and Django. Used PostgreSQL and Git. Deployed a "
     "project with Docker. Strong problem solving."),
    ("R-010", "Cybersecurity Intern",
     "Interested in cybersecurity and networking. Practised on Linux. Basic "
     "cryptography knowledge. Eager to learn penetration testing."),
    ("R-011", "DevOps Intern",
     "Familiar with Linux and Bash. Used Docker for a project. Learning CI/CD "
     "and Jenkins. Team player."),
    ("R-012", "Digital Marketing Intern",
     "Marketing student running social campaigns. Knows SEO basics and "
     "content writing. Strong communication and creativity."),
]

# ---------------------------------------------------------------------------
# Skill -> free course mapping (for the skill-gap report)
# ---------------------------------------------------------------------------
COURSE_MAP = {
    "Python": "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
    "JavaScript": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
    "SQL": "https://www.khanacademy.org/computing/computer-programming/sql",
    "React": "https://react.dev/learn",
    "Flask": "https://flask.palletsprojects.com/en/latest/tutorial/",
    "Django": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
    "Node.js": "https://nodejs.org/en/learn",
    "Docker": "https://docker-curriculum.com/",
    "AWS": "https://aws.amazon.com/getting-started/",
    "Machine Learning": "https://www.coursera.org/learn/machine-learning",
    "Deep Learning": "https://www.coursera.org/specializations/deep-learning",
    "Data Analysis": "https://www.freecodecamp.org/learn/data-analysis-with-python/",
    "Data Science": "https://www.kaggle.com/learn",
    "Power BI": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi",
    "Figma": "https://help.figma.com/hc/en-us/categories/360002051613",
    "Git": "https://learngitbranching.js.org/",
    "Communication": "https://www.coursera.org/learn/wharton-communication-skills",
    "CI/CD": "https://www.redhat.com/en/topics/devops/what-is-ci-cd",
    "TensorFlow": "https://www.tensorflow.org/learn",
    "Linux": "https://linuxjourney.com/",
}


def run():
    db.init_db()

    # --- Postings ---
    if db.get_all_postings():
        print("Postings already exist — skipping posting seed.")
    else:
        for title, company, loc, desc, skills in POSTINGS:
            db.add_posting(title=title, company=company, location=loc,
                           description=desc, skills=skills)
        print(f"Seeded {len(POSTINGS)} postings.")

    # --- Skills + course mapping ---
    conn = db.get_connection()
    for skill, url in COURSE_MAP.items():
        conn.execute(
            "INSERT OR IGNORE INTO skills (name, course_url) VALUES (?, ?)",
            (skill, url),
        )
    conn.commit()
    conn.close()
    print(f"Seeded {len(COURSE_MAP)} skill->course mappings.")

    # --- Sample resumes: scrub, extract skills, store, and match ---
    conn = db.get_connection()
    already = conn.execute("SELECT COUNT(*) AS c FROM resumes").fetchone()["c"]
    conn.close()
    if already:
        print(f"{already} resumes already exist — skipping resume seed.")
        return

    postings = []
    for p in db.get_all_postings():
        p["skills"] = json.loads(p.get("skills_json") or "[]")
        postings.append(p)

    for label, role, text in SAMPLE_RESUMES:
        scrubbed = nlp.scrub_pii(text)
        skills = nlp.extract_skills(scrubbed)
        rid = db.add_resume(scrubbed_text=scrubbed, label=label,
                            skills=skills, target_role=role, consent=1)
        ranked = matching.rank_postings(scrubbed, skills, postings, top_n=5)
        for item in ranked:
            db.save_match(rid, item["posting"]["id"], item["score"], item["gap"])
    print(f"Seeded {len(SAMPLE_RESUMES)} sample resumes with matches.")


if __name__ == "__main__":
    run()
