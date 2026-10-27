"""
SiapLI — Seed sample data (handed to P3 on Day 1).

Loads a few internship postings and skills so the app works end-to-end today.
P3 replaces/extends this with ~200 real Malaysian postings and ~400 skills.

Run:
    python seed_data.py
"""

import db

SAMPLE_POSTINGS = [
    {
        "title": "Software Engineering Intern",
        "company": "TechNova Sdn Bhd",
        "location": "Kuala Lumpur",
        "description": ("Build and test web features using Python and Flask. "
                        "Work with SQL databases, Git version control, and "
                        "collaborate in a team. React knowledge is a plus."),
        "skills": ["python", "flask", "sql", "git", "react", "teamwork"],
    },
    {
        "title": "Data Analyst Intern",
        "company": "InsightWorks",
        "location": "Petaling Jaya",
        "description": ("Analyse datasets using Python and SQL. Build reports "
                        "in Excel and present findings. Experience with data "
                        "analysis and clear communication required."),
        "skills": ["python", "sql", "excel", "data analysis", "communication"],
    },
    {
        "title": "Frontend Developer Intern",
        "company": "PixelCraft",
        "location": "Penang",
        "description": ("Develop responsive interfaces with HTML, CSS, and "
                        "JavaScript. Use React and Git. Strong teamwork and "
                        "communication skills needed."),
        "skills": ["html", "css", "javascript", "react", "git", "teamwork"],
    },
    {
        "title": "Machine Learning Intern",
        "company": "DeepMind MY",
        "location": "Cyberjaya",
        "description": ("Support ML projects using Python. Apply machine "
                        "learning and data analysis techniques. Linux and Git "
                        "experience preferred."),
        "skills": ["python", "machine learning", "data analysis", "linux", "git"],
    },
]

SAMPLE_SKILLS = [
    ("Python", "py", "https://www.freecodecamp.org/learn"),
    ("JavaScript", "js", "https://www.freecodecamp.org/learn"),
    ("SQL", None, "https://www.khanacademy.org/computing/computer-programming/sql"),
    ("React", None, "https://react.dev/learn"),
    ("Flask", None, "https://flask.palletsprojects.com/"),
    ("Data Analysis", None, "https://www.freecodecamp.org/learn/data-analysis-with-python/"),
    ("Machine Learning", "ml", "https://www.coursera.org/learn/machine-learning"),
    ("Communication", None, "https://www.coursera.org/learn/wharton-communication-skills"),
]


def run():
    db.init_db()

    # Only seed if empty, so re-running doesn't duplicate.
    if db.get_all_postings():
        print("Postings already exist — skipping posting seed.")
    else:
        for p in SAMPLE_POSTINGS:
            db.add_posting(**p)
        print(f"Seeded {len(SAMPLE_POSTINGS)} postings.")

    conn = db.get_connection()
    for name, alias, url in SAMPLE_SKILLS:
        conn.execute(
            "INSERT OR IGNORE INTO skills (name, alias, course_url) VALUES (?, ?, ?)",
            (name, alias, url),
        )
    conn.commit()
    conn.close()
    print(f"Seeded {len(SAMPLE_SKILLS)} skills.")


if __name__ == "__main__":
    run()
