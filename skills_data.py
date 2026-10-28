"""
SiapLI — Curated skills dictionary (P2, Day 1).

~150 skills across software, data, cloud, and soft skills, with common aliases.
P2 extends this toward ~400 on Day 2. Used by nlp.py for extraction.

- SKILLS:        canonical skill names
- SKILL_ALIASES: canonical name -> list of alternate spellings/abbreviations
"""

SKILLS = [
    # --- Programming languages ---
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go",
    "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
    "Dart", "Perl", "Objective-C",
    # --- Web frontend ---
    "HTML", "CSS", "React", "Vue", "Angular", "Next.js", "Svelte",
    "Tailwind CSS", "Bootstrap", "jQuery", "Redux", "Sass",
    # --- Web backend ---
    "Node.js", "Express", "Flask", "Django", "FastAPI", "Spring Boot",
    "Laravel", "Ruby on Rails", "ASP.NET", "GraphQL", "REST API",
    # --- Mobile ---
    "Android", "iOS", "React Native", "Flutter", "Jetpack Compose",
    # --- Databases ---
    "SQL", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis",
    "Oracle Database", "Microsoft SQL Server", "Firebase", "Cassandra",
    # --- Data / ML / AI ---
    "Data Analysis", "Data Science", "Machine Learning", "Deep Learning",
    "Natural Language Processing", "Computer Vision", "Pandas", "NumPy",
    "scikit-learn", "TensorFlow", "PyTorch", "Keras", "Matplotlib",
    "Power BI", "Tableau", "Excel", "Data Visualization", "Statistics",
    "Big Data", "Apache Spark", "Hadoop",
    # --- Cloud / DevOps ---
    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform",
    "Jenkins", "CI/CD", "Linux", "Bash", "Nginx", "Ansible",
    # --- Tools / practices ---
    "Git", "GitHub", "GitLab", "Jira", "Agile", "Scrum", "Kanban",
    "Unit Testing", "Selenium", "Postman", "Figma", "Adobe XD",
    # --- Security / networking ---
    "Cybersecurity", "Network Security", "Penetration Testing",
    "Cryptography", "Networking", "TCP/IP",
    # --- Business / domain ---
    "Project Management", "Business Analysis", "Digital Marketing", "SEO",
    "Content Writing", "Accounting", "Financial Analysis",
    "UI/UX Design", "Graphic Design", "Video Editing",
    # --- Soft skills ---
    "Communication", "Teamwork", "Leadership", "Problem Solving",
    "Critical Thinking", "Time Management", "Adaptability", "Creativity",
    "Presentation", "Public Speaking", "Collaboration", "Attention to Detail",
    # --- More programming / web ---
    "Spring", "Flask-RESTful", "Svelte", "Deno", "WebSockets", "Web Development",
    # --- More data / ML / AI ---
    "Data Engineering", "ETL", "Data Mining", "Jupyter", "OpenCV",
    "Hugging Face", "Prompt Engineering", "Reinforcement Learning",
    "Time Series Analysis", "A/B Testing", "SciPy", "Seaborn",
    # --- More cloud / devops ---
    "Google Cloud Platform", "DigitalOcean", "Heroku", "Grafana",
    "Prometheus", "Helm", "Serverless", "Microservices", "Load Balancing",
    # --- More databases ---
    "NoSQL", "Elasticsearch", "MariaDB", "DynamoDB", "Database Design",
    # --- More security / networking ---
    "SIEM", "Incident Response", "Firewall", "VPN", "OWASP",
    "Ethical Hacking", "Vulnerability Assessment", "Security Auditing",
    # --- More tools / practices ---
    "VS Code", "Confluence", "Trello", "Notion", "CI", "Code Review",
    "Test-Driven Development", "Debugging", "Technical Writing",
    # --- More business / domain ---
    "Market Research", "Copywriting", "Social Media Marketing",
    "Email Marketing", "Google Analytics", "CRM", "Customer Service",
    "Data Entry", "Microsoft Office", "PowerPoint", "Canva",
    # --- More soft skills ---
    "Analytical Thinking", "Decision Making", "Negotiation", "Mentoring",
    "Conflict Resolution", "Organization", "Self-Motivation", "Multitasking",
]

SKILL_ALIASES = {
    "Python": ["py"],
    "JavaScript": ["js", "ecmascript"],
    "TypeScript": ["ts"],
    "C++": ["cpp", "c plus plus"],
    "C#": ["c sharp", "csharp"],
    "Node.js": ["nodejs", "node"],
    "Next.js": ["nextjs", "next js"],
    "React": ["react.js", "reactjs"],
    "Vue": ["vue.js", "vuejs"],
    "Angular": ["angular.js", "angularjs"],
    "Ruby on Rails": ["rails"],
    "REST API": ["rest", "restful", "restful api"],
    "PostgreSQL": ["postgres"],
    "Microsoft SQL Server": ["mssql", "sql server"],
    "Machine Learning": ["ml"],
    "Deep Learning": ["dl"],
    "Natural Language Processing": ["nlp"],
    "Computer Vision": ["cv"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "Google Cloud": ["gcp", "google cloud platform"],
    "AWS": ["amazon web services"],
    "CI/CD": ["cicd", "continuous integration"],
    "UI/UX Design": ["ui/ux", "ux", "ui design", "ux design"],
    "Power BI": ["powerbi"],
    "Data Visualization": ["data viz", "dataviz"],
    "Unit Testing": ["unit tests", "pytest", "junit"],
    "Google Cloud Platform": ["gcp"],
    "Test-Driven Development": ["tdd"],
    "Google Analytics": ["ga4", "google analytics 4"],
    "Microsoft Office": ["ms office", "office suite"],
    "PowerPoint": ["ms powerpoint", "powerpoint"],
    "OpenCV": ["open cv"],
    "Hugging Face": ["huggingface"],
    "Reinforcement Learning": ["rl"],
    "Social Media Marketing": ["smm"],
    "Ethical Hacking": ["white hat", "white-hat hacking"],
    "Incident Response": ["ir"],
    "Web Development": ["web dev"],
    "Data Engineering": ["data pipelines"],
}
