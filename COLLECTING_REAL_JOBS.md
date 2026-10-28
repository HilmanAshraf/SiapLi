# Collecting Real Internships for SiapLI

A short guide to fill `real_internships_template.csv` with ~15–20 **real**
Malaysian internships so the Apply Now buttons link to genuine application pages.

Goal: honest, working data for the demo. Never invent an apply link, and never
use a company homepage as a stand-in for the real job posting.

---

## 1. The CSV columns

| Column | Required? | What to put |
|---|---|---|
| `title` | Yes | The role title, e.g. `Software Engineering Intern` |
| `company` | Recommended | The employer, e.g. `Maybank` |
| `location` | Recommended | City, e.g. `Kuala Lumpur` |
| `description` | Recommended | 1–3 sentences from the posting (helps matching) |
| `skills` | **Yes** | The required skills, separated by `;` (see §3) |
| `apply_url` | Yes if known | The **exact** application page URL (see §4) |

Separate multiple skills with a semicolon `;`
(e.g. `Python;SQL;Excel;Communication`).

---

## 2. Where to find real postings (public, copy by hand)

Copying a handful of public listings by hand for a student project is normal
research — not scraping. Good sources:

- Your **university career / industrial-training portal**
- **Company career pages** that run internship programs (e.g. Petronas, Maybank,
  CIMB, Grab Malaysia, Shopee Malaysia, Intel Malaysia, Sunway)
- Public listings on **JobStreet**, **Ricebowl**, **Hiredly**, **LinkedIn**
  (copy the title, company, a line or two of the description, the named skills,
  and the posting's own URL)

For each posting, open it and copy the **URL of that specific job page** — the
one with an Apply button — into `apply_url`.

---

## 3. Picking the `skills` (important for matching)

Read the posting's requirements and list the skills it actually names. Use the
**canonical skill names** below so SiapLI matches them to resumes correctly.
If a posting names a skill not in this list, you can still add it — matching
will use it literally, it just won't have a free-course link.

Common canonical names (full list in `skills_data.py`):

```
Programming: Python, Java, JavaScript, TypeScript, C++, C#, Go, PHP, Swift, Kotlin, Dart, R
Web:         HTML, CSS, React, Vue, Angular, Node.js, Express, Flask, Django, Bootstrap, REST API
Mobile:      Android, iOS, Flutter, Jetpack Compose
Data/AI:     SQL, Excel, Power BI, Tableau, Pandas, NumPy, scikit-learn, TensorFlow, PyTorch,
             Data Analysis, Data Science, Machine Learning, Deep Learning, Statistics,
             Natural Language Processing, Computer Vision
Databases:   MySQL, PostgreSQL, MongoDB, Firebase
Cloud/DevOps:AWS, Azure, Docker, Kubernetes, Terraform, Jenkins, CI/CD, Linux, Bash
Security/Net:Cybersecurity, Network Security, Penetration Testing, Cryptography, Networking,
             TCP/IP, SIEM, Incident Response, Firewall, OWASP, Ethical Hacking
Tools:       Git, GitHub, Jira, Agile, Scrum, Selenium, Postman, Figma, Adobe XD
Business:    Project Management, Business Analysis, Digital Marketing, SEO, Content Writing,
             Accounting, Financial Analysis, UI/UX Design, Graphic Design, Video Editing
Soft skills: Communication, Teamwork, Leadership, Problem Solving, Critical Thinking,
             Time Management, Creativity, Collaboration, Attention to Detail
```

Tip: 4–7 skills per posting is a good target.

---

## 4. The `apply_url` rule (read this)

- Paste the **direct URL of the specific job posting** (the page with the Apply
  button).
- Do **not** use the company's homepage or a generic careers landing page.
- If you can't find the real apply URL, **leave `apply_url` blank** — SiapLI
  will show a disabled "Apply Now" button, which is honest and fine.

---

## 5. Fill the template

1. Open `real_internships_template.csv`.
2. **Delete the two EXAMPLE rows** (keep the header row).
3. Add one row per real internship. Keep commas out of fields, or wrap the
   field in double quotes if it must contain a comma.
4. Save.

---

## 6. Import into SiapLI

From the repo root:

```bash
./venv/bin/python import_jobs.py real_internships_template.csv
```

This loads your rows into the database. Re-running is safe — it skips rows whose
`title + company` already exist, so you won't get duplicates. See `import_jobs.py`
for options (e.g. `--replace` to clear previous imports first).

After importing, the Apply Now buttons on matching postings become live links
that open the real application page in a new tab.
