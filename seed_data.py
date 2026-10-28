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
    ("Network Support Intern", "NetLink Systems", "Shah Alam",
     "Support networking infrastructure and TCP/IP configurations. Work on "
     "Linux servers. Strong problem solving and communication needed.",
     ["Networking", "TCP/IP", "Linux", "Problem Solving", "Communication"]),
    ("Android Developer Intern", "Mobilytics", "Kuala Lumpur",
     "Build native Android apps with Kotlin and Jetpack Compose. Integrate "
     "Firebase and REST APIs. Use Git. Attention to detail valued.",
     ["Android", "Kotlin", "Jetpack Compose", "Firebase", "REST API", "Git"]),
    ("iOS Developer Intern", "Appletree Studio", "Petaling Jaya",
     "Develop iOS apps with Swift. Work with REST APIs and Git. Collaborate "
     "in a small team. Attention to detail important.",
     ["iOS", "Swift", "REST API", "Git", "Teamwork", "Attention to Detail"]),
    ("Cloud Security Intern", "FortressCloud", "Cyberjaya",
     "Support cloud security on AWS. Study network security and cryptography. "
     "Linux and scripting in Bash required.",
     ["AWS", "Network Security", "Cryptography", "Linux", "Bash", "Cybersecurity"]),
    ("Data Engineer Intern", "PipelineWorks", "Kuala Lumpur",
     "Build data pipelines with Python and SQL. Work with Apache Spark and "
     "big data on Linux. Use Git for version control.",
     ["Python", "SQL", "Apache Spark", "Big Data", "Linux", "Git"]),
    ("Business Intelligence Intern", "ClearMetrics", "Penang",
     "Build dashboards in Tableau and Power BI. Write SQL queries and analyse "
     "data in Excel. Strong communication required.",
     ["Tableau", "Power BI", "SQL", "Excel", "Data Analysis", "Communication"]),
    ("Web Developer Intern", "SiteForge", "Johor Bahru",
     "Build websites with HTML, CSS, JavaScript and Bootstrap. Use Git. Some "
     "PHP and Laravel experience valued. Teamwork essential.",
     ["HTML", "CSS", "JavaScript", "Bootstrap", "Git", "PHP", "Teamwork"]),
    ("NLP Research Intern", "Lingua AI", "Cyberjaya",
     "Research natural language processing with Python and PyTorch. Apply "
     "deep learning. Use Git. Statistics knowledge helpful.",
     ["Python", "Natural Language Processing", "PyTorch", "Deep Learning", "Git", "Statistics"]),
    ("Computer Vision Intern", "VisionWorks", "Kuala Lumpur",
     "Develop computer vision models in Python with TensorFlow. Apply machine "
     "learning. Linux and Git experience preferred.",
     ["Python", "Computer Vision", "TensorFlow", "Machine Learning", "Linux", "Git"]),
    ("Site Reliability Intern", "Uptime Labs", "Cyberjaya",
     "Support reliability with Kubernetes and Docker. Manage Linux systems "
     "and CI/CD. Scripting in Bash. Problem solving required.",
     ["Kubernetes", "Docker", "Linux", "CI/CD", "Bash", "Problem Solving"]),
    ("Content Writer Intern", "WordCraft Media", "Kuala Lumpur",
     "Write and edit content for web and social. Apply SEO best practices. "
     "Strong communication, creativity and attention to detail.",
     ["Content Writing", "SEO", "Communication", "Creativity", "Attention to Detail"]),
    ("Social Media Intern", "BuzzReach", "Petaling Jaya",
     "Manage social campaigns and create content. Apply digital marketing and "
     "SEO. Analyse results. Communication and creativity needed.",
     ["Digital Marketing", "SEO", "Content Writing", "Communication", "Creativity"]),
    ("Project Management Intern", "DeliverIt", "Shah Alam",
     "Support project tracking in Jira using Agile and Scrum. Document work. "
     "Communication, time management and teamwork needed.",
     ["Project Management", "Jira", "Agile", "Scrum", "Communication", "Time Management"]),
    ("Finance Analyst Intern", "LedgerPro", "Kuala Lumpur",
     "Analyse financial data in Excel. Support reporting and accounting. "
     "Strong critical thinking and attention to detail required.",
     ["Financial Analysis", "Excel", "Accounting", "Critical Thinking", "Attention to Detail"]),
    ("Video Editor Intern", "FrameHouse", "George Town",
     "Edit video content and produce graphics. Strong creativity and "
     "attention to detail. Collaborate with the content team.",
     ["Video Editing", "Graphic Design", "Creativity", "Attention to Detail", "Collaboration"]),
    ("Automation QA Intern", "TestLab MY", "Cyberjaya",
     "Write automated tests with Selenium and unit tests. Use Postman for API "
     "testing and Git. Problem solving and attention to detail needed.",
     ["Selenium", "Unit Testing", "Postman", "Git", "Problem Solving", "Attention to Detail"]),
    ("Blockchain Developer Intern", "ChainWorks", "Kuala Lumpur",
     "Build smart contracts and dApps with JavaScript and cryptography. Use "
     "Git. Problem solving and strong fundamentals required.",
     ["JavaScript", "Cryptography", "Git", "Problem Solving", "Networking"]),
    ("Statistics Research Intern", "DataStat Lab", "Petaling Jaya",
     "Apply statistics with Python, Pandas and Matplotlib. Analyse data and "
     "report findings. Strong data analysis skills needed.",
     ["Statistics", "Python", "Pandas", "Matplotlib", "Data Analysis"]),
    ("Systems Administrator Intern", "CoreOps", "Shah Alam",
     "Administer Linux servers and networking. Script with Bash. Handle "
     "problem solving and time management under pressure.",
     ["Linux", "Networking", "Bash", "Problem Solving", "Time Management"]),
    ("Product Design Intern", "FormLab", "Kuala Lumpur",
     "Design product interfaces in Figma and Adobe XD. Run usability research. "
     "Strong creativity and collaboration required.",
     ["UI/UX Design", "Figma", "Adobe XD", "Creativity", "Collaboration"]),
    ("Java Developer Intern", "Enterprise Soft", "Cyberjaya",
     "Build backend services in Java with Spring Boot. Work with SQL and Git. "
     "Problem solving and teamwork required.",
     ["Java", "Spring Boot", "SQL", "Git", "Problem Solving", "Teamwork"]),
    # --- Entry-level "bridge" roles: easier stepping stones that share skills
    #     with harder roles, so students always see achievable alternatives. ---
    ("Junior Web Assistant Intern", "StartRight Digital", "Kuala Lumpur",
     "Assist with simple website updates using HTML, CSS and Git. Great entry "
     "point for aspiring developers. Teamwork and eagerness to learn valued.",
     ["HTML", "CSS", "Git", "Teamwork", "Communication"]),
    ("Data Entry & Reporting Intern", "InsightWorks", "Petaling Jaya",
     "Enter data and build simple reports in Excel and SQL. A stepping stone "
     "into data analytics. Attention to detail and communication needed.",
     ["Excel", "SQL", "Data Entry", "Attention to Detail", "Communication"]),
    ("IT Helpdesk Assistant Intern", "HelpDesk Solutions", "Shah Alam",
     "Front-line tech support on Windows and Linux. Great first step toward "
     "networking or security roles. Communication and problem solving needed.",
     ["Linux", "Networking", "Customer Service", "Communication", "Problem Solving"]),
    ("Junior Python Intern", "CodeStart Labs", "Cyberjaya",
     "Learn and build small tools in Python with Git. An approachable entry "
     "into software, data and AI tracks. Problem solving encouraged.",
     ["Python", "Git", "Problem Solving", "Teamwork", "Communication"]),
    ("Marketing Assistant Intern", "GrowthLab", "Kuala Lumpur",
     "Support content and social posts. A friendly entry into digital "
     "marketing. Creativity, communication and attention to detail needed.",
     ["Content Writing", "Communication", "Creativity", "Attention to Detail", "Canva"]),
    ("Junior QA Intern", "QualityFirst", "Penang",
     "Learn software testing: run test cases and log issues with Postman and "
     "Git. A gentle start toward QA automation. Attention to detail needed.",
     ["Postman", "Git", "Attention to Detail", "Problem Solving", "Communication"]),
    ("Associate UI Intern", "DesignHive", "Kuala Lumpur",
     "Support designers in Figma on real projects. A welcoming first step into "
     "UI/UX. Creativity and collaboration valued.",
     ["Figma", "Creativity", "Collaboration", "Communication", "Attention to Detail"]),
    ("Cloud Fundamentals Intern", "SkyStack", "Cyberjaya",
     "Learn cloud basics on AWS with Linux and Git. A stepping stone toward "
     "DevOps and cloud engineering. Problem solving encouraged.",
     ["AWS", "Linux", "Git", "Problem Solving", "Communication"]),
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
    ("R-013", "Cloud Engineer Intern",
     "Comfortable with AWS and Docker. Learning Terraform. Strong Linux and "
     "networking fundamentals. Problem solver."),
    ("R-014", "Android Developer Intern",
     "Built Android apps with Kotlin and Firebase. Used REST APIs and Git. "
     "Detail oriented and collaborative."),
    ("R-015", "AI Engineer Intern",
     "Python developer exploring NLP and computer vision with PyTorch. Used "
     "Git. Comfortable with deep learning basics."),
    ("R-016", "Data Engineer Intern",
     "Skilled in Python and SQL. Some exposure to big data and Apache Spark. "
     "Works on Linux and uses Git daily."),
    ("R-017", "QA / Test Engineer Intern",
     "Wrote unit tests and automated tests with Selenium. Used Postman and "
     "Git. Detail oriented with good problem solving."),
    ("R-018", "Java Developer Intern",
     "Backend developer in Java with Spring Boot. Comfortable with SQL and "
     "Git. Strong teamwork and problem solving."),
    ("R-019", "Business Analyst Intern",
     "Analyses requirements and data in Excel. Uses Jira. Strong "
     "communication and critical thinking skills."),
    ("R-020", "Network Support Intern",
     "Interested in networking and TCP/IP. Comfortable on Linux. Good problem "
     "solving and communication."),
    ("R-021", "Content Writer Intern",
     "Writes web and social content. Knows SEO and content writing. Creative "
     "with strong attention to detail."),
    ("R-022", "Project Management Intern",
     "Coordinated a team project using Agile and Jira. Strong communication, "
     "time management and teamwork."),
    ("R-023", "Graphic Design Intern",
     "Design student producing graphics and video edits. Very creative with "
     "sharp attention to detail."),
    ("R-024", "Web Developer Intern",
     "Builds websites with HTML, CSS, JavaScript and Bootstrap. Uses Git. "
     "Some PHP experience. Enjoys teamwork."),
    ("R-025", "Computer Vision Intern",
     "Python developer working on computer vision with TensorFlow. Applies "
     "machine learning. Comfortable on Linux with Git."),
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
    "HTML": "https://developer.mozilla.org/en-US/docs/Learn/HTML",
    "CSS": "https://web.dev/learn/css/",
    "Bootstrap": "https://getbootstrap.com/docs/5.3/getting-started/introduction/",
    "Java": "https://dev.java/learn/",
    "Spring Boot": "https://spring.io/guides/gs/spring-boot/",
    "Node.js": "https://nodejs.org/en/learn",
    "PostgreSQL": "https://www.postgresqltutorial.com/",
    "MySQL": "https://dev.mysql.com/doc/mysql-getting-started/en/",
    "Kubernetes": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
    "Kotlin": "https://kotlinlang.org/docs/getting-started.html",
    "Android": "https://developer.android.com/courses",
    "Swift": "https://www.swift.org/getting-started/",
    "Flutter": "https://docs.flutter.dev/get-started/learn-more",
    "PyTorch": "https://pytorch.org/tutorials/beginner/basics/intro.html",
    "Pandas": "https://pandas.pydata.org/docs/getting_started/index.html",
    "scikit-learn": "https://scikit-learn.org/stable/getting_started.html",
    "Statistics": "https://www.khanacademy.org/math/statistics-probability",
    "Tableau": "https://www.tableau.com/learn/training",
    "Networking": "https://www.professormesser.com/network-plus/n10-008/n10-008-training-course/",
    "Network Security": "https://www.cybrary.it/",
    "Cybersecurity": "https://www.cybrary.it/",
    "Penetration Testing": "https://tryhackme.com/",
    "Cryptography": "https://www.coursera.org/learn/crypto",
    "SEO": "https://developers.google.com/search/docs/fundamentals/seo-starter-guide",
    "Digital Marketing": "https://learndigital.withgoogle.com/digitalgarage",
    "Agile": "https://www.atlassian.com/agile",
    "Scrum": "https://www.scrum.org/resources/what-is-scrum",
    "Jira": "https://www.atlassian.com/software/jira/guides",
    "Excel": "https://support.microsoft.com/en-us/office/excel-video-training-9bc05390-e94c-46af-a5b3-d7c22f6990bb",
    "Selenium": "https://www.selenium.dev/documentation/",
    "REST API": "https://restfulapi.net/",
    "Apache Spark": "https://spark.apache.org/docs/latest/quick-start.html",
    "Bash": "https://www.learnshell.org/",
    # --- Languages / frameworks previously uncovered ---
    "C#": "https://learn.microsoft.com/en-us/dotnet/csharp/",
    "PHP": "https://www.phptutorial.net/",
    "Dart": "https://dart.dev/language",
    "Express": "https://expressjs.com/en/starter/installing.html",
    "iOS": "https://developer.apple.com/tutorials/app-dev-training",
    "Jetpack Compose": "https://developer.android.com/jetpack/compose/tutorial",
    "Firebase": "https://firebase.google.com/docs",
    "Azure": "https://learn.microsoft.com/en-us/training/azure/",
    "Terraform": "https://developer.hashicorp.com/terraform/tutorials",
    "Jenkins": "https://www.jenkins.io/doc/tutorials/",
    "Big Data": "https://www.ibm.com/think/topics/big-data",
    "Matplotlib": "https://matplotlib.org/stable/tutorials/index.html",
    "Natural Language Processing": "https://www.nltk.org/book/",
    "Computer Vision": "https://opencv.org/get-started/",
    "TCP/IP": "https://www.cloudflare.com/learning/ddos/glossary/tcp-ip/",
    "Postman": "https://learning.postman.com/docs/getting-started/overview/",
    "Unit Testing": "https://docs.pytest.org/en/stable/getting-started.html",
    # --- Design / content / business previously uncovered ---
    "Adobe XD": "https://helpx.adobe.com/xd/tutorials.html",
    "UI/UX Design": "https://www.coursera.org/learn/ui-ux-design",
    "Graphic Design": "https://www.coursera.org/learn/fundamentals-of-graphic-design",
    "Video Editing": "https://www.youtube.com/learningvideoediting",
    "Content Writing": "https://www.hubspot.com/resources/courses/content-marketing",
    "Business Analysis": "https://www.coursera.org/learn/business-analysis-foundations",
    "Project Management": "https://www.coursera.org/learn/project-management-basics",
    "Accounting": "https://www.khanacademy.org/economics-finance-domain/core-finance/accounting-and-financial-stateme",
    "Financial Analysis": "https://corporatefinanceinstitute.com/resources/accounting/",
    # --- Soft skills (free, to motivate and round out the student) ---
    "Teamwork": "https://www.coursera.org/learn/teamwork-skills-effective-communication",
    "Collaboration": "https://www.coursera.org/learn/teamwork-skills-effective-communication",
    "Problem Solving": "https://www.coursera.org/learn/problem-solving",
    "Critical Thinking": "https://www.coursera.org/learn/mindware",
    "Creativity": "https://www.coursera.org/learn/creativity-innovation",
    "Time Management": "https://www.coursera.org/learn/work-smarter-not-harder",
    "Attention to Detail": "https://www.open.edu/openlearn/education-development/learning-learn",
    "Canva": "https://www.canva.com/designschool/",
    "Customer Service": "https://www.hubspot.com/resources/courses/customer-service",
    "Data Entry": "https://www.gcfglobal.org/en/excel/",
    "Communication": "https://www.coursera.org/learn/wharton-communication-skills",
}


def run():
    db.init_db()

    # --- Postings ---
    # Load REAL internships from real_internships.csv (not synthetic data).
    # The legacy synthetic POSTINGS list is kept in this file only for
    # reference/history; it is no longer inserted.
    from pathlib import Path
    csv_path = Path(__file__).parent / "real_internships.csv"
    if db.get_all_postings():
        print("Postings already exist — skipping posting seed.")
    elif csv_path.exists():
        n = db.import_postings_csv(str(csv_path))
        print(f"Seeded {n} real postings from real_internships.csv.")
        # Broaden apply URLs to reliable field searches.
        try:
            import fix_apply_urls
            fix_apply_urls.main()
        except Exception as e:
            print(f"(apply-url broadening skipped: {e})")
    else:
        print("real_internships.csv not found — no postings seeded.")

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
        skills = nlp.extract_skills(text)   # skills are not PII
        scrubbed = nlp.scrub_pii(text)
        rid = db.add_resume(scrubbed_text=scrubbed, label=label,
                            skills=skills, target_role=role, consent=1)
        ranked = matching.rank_postings(scrubbed, skills, postings, top_n=5)
        for item in ranked:
            db.save_match(rid, item["posting"]["id"], item["score"], item["gap"])
    print(f"Seeded {len(SAMPLE_RESUMES)} sample resumes with matches.")


if __name__ == "__main__":
    run()
