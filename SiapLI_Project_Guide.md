# SiapLI — Build & Delivery Guide (3-Day Sprint to 29/10)

**Team:** NullForce
**Project:** SiapLI — AI Internship Readiness & Matching for Students
**Event:** Hackspire Lumina
**Deadline:** Wednesday, 29 October 2026
**Today:** Tuesday, 27 October 2026 — you have **~3 working days**.

---

## 0. Where You Stand (Judge Feedback Recap)

You already pitched once and have two score sheets. Use them as your to-do list.

| Criterion | Judge A (Alex Yap) | Judge B (Ts Dr Amar) | Verdict |
|---|---|---|---|
| Problem & User Understanding | 6 | 8 | Strong — keep |
| Data Use & Preparation | 5 | 6 | Needs real data shown |
| Technical Implementation | 5 | 7 | Need a working demo |
| Innovation & Solution Value | 5 | 7 | **Fix: no competitor comparison** |
| User Experience & Accessibility | 5 | 7 | Needs usable UI |
| **Validation & Performance** | **4** | **4** | **Weakest — must show testing** |
| Impact & Practical Feasibility | 6 | 7 | OK |
| **Responsible & Ethical Use** | **4** | **4** | **Weakest — PII to external LLM** |
| Pitch & Communication | 6 | 7 | OK |
| Team Execution & Learning | 5 | 6 | OK |
| **TOTAL** | **51/100** | **63/100** | Target: 75+ |

**Three things that will move your score the most:**
1. **Competitor comparison** (Innovation) — judges said the space is crowded and you ignored it. Section 2 below fixes this.
2. **PII handling** (Responsible Use, scored 4/4) — Ts Dr Amar explicitly said: scrub PII from resumes *before* sending to any external LLM. Section 5 fixes this.
3. **Validation evidence** (scored 4/4) — show you tested matches against lecturer judgement with real numbers. Section 6 fixes this.

---

## 1. What SiapLI Is (One-Paragraph Pitch)

SiapLI is a mobile-friendly web app where Malaysian Year 2–3 students upload a resume and instantly get: a **match score (%)** against real internship postings, a **skill-gap report** with free course suggestions, and **AI feedback** to improve their resume for a target role. Universities get a **cohort dashboard** showing the most common skill gaps across students. Free for students; universities pay a licence; employers pay for featured listings.

---

## 2. Competitor Analysis (Malaysia) — THE GAP YOU MISSED

The judges penalised you for ignoring a crowded market. Here is the comparison to put on a slide. Sources are cited inline.

### Direct / adjacent players

| Platform | What it does | Student internship focus? | Skill-gap diagnosis? | University cohort dashboard? |
|---|---|---|---|---|
| [Hiredly (ex-WOBB)](https://my.hiredly.com/) | Job portal with AI job matching + company "vibe check" videos | No — general jobs | No | No |
| [Ricebowl](https://play.google.com/store/apps/details?hl=en&id=my.ricebowl.applicant) | Job portal, EN/Mandarin, AI skill suggestions + resume description generation | Partial | Light (skill suggestions) | No |
| [JobStreet](https://www.jobstreet.com.my/) | Largest MY job board, resume + matching | No | No | No |
| [A Job Thing / Maukerja](https://www.ajobthing.com/) | Recruitment + direct employer chat | No | No | No |
| [FastApply](https://fastapply.co/my) | AI auto-applies to jobs with tailored resume | No | No | No |
| [Monash CareerEdge](https://www.monash.edu.my/pages/latest/articles/2026/monash-university-malaysia-launches-careeredge,-a-university-developed-ai-interview-simulation-platform) | University AI *interview* simulation | Yes (students) | No (interview prep, not matching) | Partial |

*(Content on competitor features was rephrased from the linked sources for licensing compliance.)*

### Your defensible differentiation (say this out loud in the pitch)
1. **Readiness, not just listings.** Every competitor answers "which job?"; SiapLI answers "**am I ready, and what do I learn next?**" via the skill-gap report. Ricebowl gives skill hints but doesn't score readiness against a target role.
2. **University cohort dashboard.** No job board shows a career/industrial-training unit the *aggregate* skill gaps of a whole cohort. This is a B2B wedge none of the job boards have.
3. **Internship-specific, Malaysia-first.** Tuned to LI (Latihan Industri) roles and the Year 2–3 timeline, not general hiring.
4. **Explainability.** You show *why* a match scored what it did (which skills matched/missed), vs. black-box "smart AI" matching.

### Market context (strengthens your "Impact" slide)
- Malaysian employers report persistent **digital-skills gaps** among graduates ([PMC study, 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11387931/)).
- Fresh graduates increasingly struggle as AI automates entry-level roles ([The Edge Malaysia, 2025](https://theedgemalaysia.com/node/777835)).
- The talent gap is driven by "credentials, not job-ready skills" — exactly the readiness gap SiapLI targets ([Complete AI Training, 2025](https://completeaitraining.com/news/job-ready-not-just-qualified-fixing-malaysias-ai-talent/)).

---

## 3. Tech Stack & How to Use Each Tool

Stick with your proposed stack (judges liked it — "perfectly matched to the use case"). Keep it free-tier.

| Layer | Tool | Why | How you use it |
|---|---|---|---|
| Language | **Python 3.11+** | Team knows it; best NLP ecosystem | Core app logic |
| Web framework | **Flask** | Lightweight, fast to build | Routes for upload, results, dashboard; serves Jinja2 templates |
| Database | **SQLite** | Zero-config, file-based, free | Store resumes (scrubbed), postings, match results, skill lists |
| Resume parsing | **pdfplumber** (PDF) + **python-docx** (DOCX) | Extract text from uploads | `resume_text = extract(file)` |
| Skill extraction | **spaCy** + a curated skills list (PhraseMatcher) | Reliable, offline, no API cost | Match resume + job text against a known skills dictionary |
| Semantic matching | **sentence-transformers** (`all-MiniLM-L6-v2`) | Embeddings → cosine similarity for match score | Encode resume & each posting, compute similarity → % score |
| AI resume feedback | **LLM API** (OpenAI/Gemini free tier) — **on scrubbed text only** | Human-like improvement tips | Send *redacted* resume + target role, get feedback bullets |
| Frontend | **Jinja2 + Bootstrap 5** (or Tailwind CDN) | Mobile-friendly, no build step, accessible | Responsive templates, ARIA labels |
| Charts (dashboard) | **Chart.js** (CDN) | Cohort skill-gap bar chart | Feed aggregated gap counts |
| Hosting | **Render / Railway / PythonAnywhere free tier** | RM0 demo URL | Deploy Flask app |
| Version control | **GitHub** | Collaboration, demo proof | One repo, feature branches per person |

### Minimal setup commands (each dev runs once)
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install flask pdfplumber python-docx spacy sentence-transformers chart-studio
python -m spacy download en_core_web_sm
```

### Core matching logic (reference snippet)
```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")  # loads once, free, offline

def match_score(resume_text: str, job_text: str) -> float:
    emb = model.encode([resume_text, job_text], convert_to_tensor=True)
    sim = util.cos_sim(emb[0], emb[1]).item()   # -1..1
    return round(max(0.0, sim) * 100, 1)         # as a percentage
```

```python
# Skill-gap: skills in job but NOT in resume
def skill_gap(resume_skills: set, job_skills: set) -> list:
    return sorted(job_skills - resume_skills)
```

---

## 4. Data You Need (fix the "Data Use" score)

Judges want to see *real* data, quality notes, and acknowledged gaps.

- **~200 internship postings** — scrape/collect from Malaysian sources (title, company, description, required skills). Store in SQLite.
- **~30 volunteer resumes** — collect from classmates (consent required — see Section 5).
- **Curated skills dictionary** (~300–500 terms) — tech + soft skills, with aliases (e.g. "JS" → "JavaScript"). This powers spaCy extraction. **This is your highest-leverage data asset** — accuracy depends on it.
- **Course mapping** — map each skill to 1–2 free courses (Coursera free, YouTube, freeCodeCamp) for the skill-gap report.

**Acknowledge the gaps on a slide:** small sample (30 resumes), skills list isn't exhaustive, postings may be stale. Judges reward honesty here.

---

## 5. Responsible Use / PII — THE FIX THAT WAS SCORED 4/10

Both judges hit this. Do all of the following and **say it in the pitch**:

1. **Scrub PII before any external LLM call.** Strip name, email, phone, address, matric number, IC. Use spaCy NER (PERSON, GPE) + regex for email/phone/IC.
   ```python
   import re
   def scrub_pii(text: str) -> str:
       text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[EMAIL]", text)
       text = re.sub(r"\b\d{6}-\d{2}-\d{4}\b", "[IC]", text)      # MY IC
       text = re.sub(r"\b(?:\+?60|0)\d{1,2}-?\d{7,8}\b", "[PHONE]", text)
       # + spaCy NER to replace PERSON / GPE entities
       return text
   ```
2. **Consent on upload.** A checkbox: "I consent to my resume being analysed. PII is removed before AI processing." Store consent flag in DB.
3. **Store scrubbed text, not raw.** Keep raw file only transiently in memory; persist the redacted version.
4. **Human oversight note.** Match scores are *decision support*, not gatekeeping — a human (student/advisor) decides.
5. **Bias note.** Acknowledge embedding models can carry bias; you mitigate by showing the *explainable* skill list, not a hidden verdict.

Put a single **"Responsible AI"** slide covering these five points. This alone should lift you several marks.

---

## 6. Validation Plan — THE OTHER 4/10 FIX

Show evidence, numbers, and limitations.

- **Ground truth:** have a lecturer (or you, role-playing the industrial-training unit) rank the top-3 internship matches for ~10–15 resumes.
- **Metric:** % of cases where SiapLI's top-3 overlaps the human's top-3. **Target: ≥80% agreement** (this is already in your pitch — now actually measure it).
- **Before/after:** take 5 resumes, apply the AI feedback, re-score. Show match-score improvement (target +20%).
- **Report a confusion case:** pick one where the model got it wrong and explain why (shows you understand limitations).
- Put the results in a small table on a **"Validation" slide**. Even n=15 with honest caveats beats no evidence.

---

## 7. Constraints (be explicit — judges reward realism)

| Constraint | Reality | Mitigation |
|---|---|---|
| **Time** | 3 days, 5 people, part-time | Freeze scope (Section 8); no new features after Day 2 noon |
| **Budget** | ~RM0; LLM API has small cost | Use free tiers; cap LLM calls; spaCy/embeddings are offline/free |
| **Data** | Only ~30 resumes, ~200 postings | State as a known limitation; design to scale later |
| **PII / privacy** | Real student resumes = sensitive | Scrub + consent (Section 5) |
| **Model accuracy** | Embeddings ≠ perfect understanding | Explainable skill list + human-in-the-loop |
| **Skills dictionary coverage** | Misses niche/emerging skills | Curate top ~400; note it's extensible |
| **Demo risk** | Live demo may fail on stage | Pre-record a backup demo video + seed DB with known-good sample |
| **Deployment** | Free tier can sleep/cold-start | Warm it up before pitch; have localhost fallback |

---

## 8. Scope Freeze — Build Only This (MVP)

**Must-have (demo-critical):**
1. Resume upload (PDF/DOCX) → text extraction
2. Match score vs. internship postings (top-3 ranked)
3. Skill-gap report + free course links
4. PII scrubbing + consent checkbox
5. One cohort dashboard page (bar chart of top skill gaps)

**Nice-to-have (only if time):**
- LLM resume feedback (can be mocked with templated tips if API fails)
- Login/accounts (use a simple session, skip auth if tight)

**Explicitly OUT of scope (say so):** employer accounts, payments, mobile native app, real-time scraping.

---

## 9. 5-Person Work Split + 3-Day Timeline

Assign one **owner** per track. Owners integrate daily into `main`.

### Roles
| # | Person | Role | Owns |
|---|---|---|---|
| 1 | **P1 — Backend/Matching Lead** | Core engine | Flask app skeleton, embeddings matching, match-score API, DB schema |
| 2 | **P2 — NLP/Data Lead** | Skills + parsing | Resume parsing, spaCy skill extraction, skills dictionary, skill-gap logic, PII scrubbing |
| 3 | **P3 — Data/Content Lead** | Dataset + courses | Collect ~200 postings + ~30 resumes, course mapping, seed SQLite, run validation study |
| 4 | **P4 — Frontend/UX Lead** | UI + accessibility | Upload page, results page, dashboard (Chart.js), Bootstrap, ARIA/accessibility |
| 5 | **P5 — PM / Pitch / Responsible-AI Lead** | Glue + story | Deck, competitor slide, Responsible-AI slide, demo video, deployment, integration testing |

### Day 1 — Tue 27 Oct: Foundations
- **P1:** Flask skeleton + routes (`/`, `/upload`, `/results`, `/dashboard`), SQLite schema. Push repo. ← unblocks everyone
- **P2:** Resume text extraction (pdfplumber/python-docx) + first skills dictionary (~150 skills). PII scrubber v1.
- **P3:** Collect first 100 postings + 15 resumes (with consent form). Start course mapping.
- **P4:** Static upload + results page mockup (Bootstrap), mobile layout.
- **P5:** Draft deck outline, write competitor slide (use Section 2), set up Render/Railway account, pick LLM API + key.
- **End-of-day sync (15 min):** repo runs locally for all 5.

### Day 2 — Wed 28 Oct: Build & Integrate
- **P1:** Wire embeddings matching → return top-3 scores to the results page. Match-score endpoint done by noon.
- **P2:** Finish skills dictionary (~400), skill-gap function, integrate scrubber into upload flow.
- **P3:** Finish dataset (200 postings, 30 resumes) + course links; **start validation study** with lecturer/mock ground truth.
- **P4:** Connect real data to results + dashboard (Chart.js cohort gaps). Accessibility pass.
- **P5:** LLM feedback integration on *scrubbed* text (+ templated fallback). Responsible-AI slide. Deploy to free tier.
- **🔒 Scope freeze at noon.** After this, only bug-fixing and polish.
- **End-of-day:** full flow works end-to-end on the deployed URL.

### Day 3 — Wed→demo / final polish (before 29/10 deadline)
- **P1 + P2:** Bug fixes, edge cases (empty resume, unsupported file), freeze code.
- **P3:** Finalise validation numbers → fill the Validation slide (≥80% target, before/after +20%).
- **P4:** Final UI polish, test on a phone, fix any accessibility warnings.
- **P5:** **Record backup demo video**, finalise deck, rehearse pitch (3× timed), prep answers for judge Q&A on PII + competitors.
- **Buffer:** last 3 hours = no code, only rehearsal + submission.

---

## 10. Pitch Checklist (what wins the points back)

Order your deck so the weak areas are visibly fixed:
1. Problem + users (you're strong — keep short)
2. Solution demo (live or video)
3. **Competitor slide** (Section 2) ← was missing
4. How it works (spaCy + embeddings + explainable match)
5. **Responsible-AI slide** (Section 5) ← scored 4/10
6. **Validation slide** with real numbers (Section 6) ← scored 4/10
7. Impact + market (Section 2 context) + roadmap
8. Team + what you learned

**Rehearse answers to the two questions judges will ask:**
- "How do you protect student PII?" → Section 5, five points.
- "How are you different from Hiredly/Ricebowl?" → Section 2, four differentiators.

---

## 11. Definition of Done (check before submitting)
- [ ] Deployed URL loads on mobile
- [ ] Upload → match score → skill-gap → course links works end-to-end
- [ ] Cohort dashboard shows a real chart
- [ ] PII scrubbing verified on a sample resume (show redacted output)
- [ ] Consent checkbox present and stored
- [ ] Validation table has real numbers + one honest limitation
- [ ] Competitor slide + Responsible-AI slide in deck
- [ ] Backup demo video recorded
- [ ] Repo pushed, README with run instructions
- [ ] Pitch rehearsed and timed

---

*Sources cited inline. Competitor feature descriptions were rephrased from their public pages/listings for licensing compliance; verify current features before the pitch.*
