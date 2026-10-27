# SiapLI — 3-Day Sprint Plan (27 → 29 Oct)

Team NullForce · 5 people · Deadline **Wed 29 Oct 2026**

## Roles
| # | Role | Owns |
|---|---|---|
| P1 | Backend/Matching Lead | Flask app, matching engine, DB, integration |
| P2 | NLP/Data Lead | Resume parsing, spaCy skills, PII scrubbing |
| P3 | Data/Content Lead | Dataset (postings + resumes), courses, validation study |
| P4 | Frontend/UX Lead | UI, accessibility, dashboard charts |
| P5 | PM/Pitch/Responsible-AI Lead | Deck, competitor + Responsible-AI slides, deploy, demo video |

---

## DAY 1 — Tue 27 Oct · Foundations

### P1 — Backend/Matching ✅ DONE (scaffolded today)
- [x] Flask skeleton + routes: `/`, `/upload`, `/results/<id>`, `/dashboard`
- [x] SQLite schema: `postings`, `resumes`, `match_results`, `skills` (`db.py`)
- [x] Matching engine with embedding score + keyword fallback (`matching.py`)
- [x] PII-safe upload flow (raw file deleted, scrubbed text stored, consent required)
- [x] End-to-end smoke test passing (`smoke_test.py`)
- [x] README + requirements.txt + .gitignore
- [ ] **Your next step:** push the repo to GitHub so P2–P5 can clone (see commands below)

### P2 — NLP/Data
- [ ] Clone repo, run `smoke_test.py` to confirm it works
- [ ] Build first skills dictionary (~150 skills) in the `skills` table
- [ ] Start real text extraction (pdfplumber for PDF, python-docx for DOCX)
- [ ] PII scrubber v1 already stubbed — extend with spaCy NER for names/places

### P3 — Data/Content
- [ ] Collect first ~100 internship postings (title, company, description, skills)
- [ ] Collect ~15 volunteer resumes **with signed consent**
- [ ] Start mapping skills → free courses

### P4 — Frontend/UX
- [ ] Clone repo — templates already exist (`templates/`), restyle them
- [ ] Polish upload + results pages (Bootstrap), confirm mobile layout

### P5 — PM/Pitch
- [ ] Draft deck outline; write the **competitor slide** (Guide §2)
- [ ] Create Render/Railway account; pick LLM API + get a key
- [ ] **End-of-day sync:** confirm all 5 can run the app locally

---

## DAY 2 — Wed 28 Oct · Build & Integrate  🔒 scope freeze at noon

### P1
- [ ] Confirm embedding model works (`pip install sentence-transformers`); top-3 scores correct
- [ ] Help P2 swap `nlp_stub` → real NLP module (signatures already match)
- [ ] Fix any integration bugs as teammates merge

### P2
- [ ] Finish skills dictionary (~400 terms + aliases)
- [ ] Finalise spaCy PhraseMatcher extraction + full PII scrub, integrate into upload
- [ ] Verify scrubber on real resumes (show redacted output for the pitch)

### P3
- [ ] Finish dataset: ~200 postings + ~30 resumes, all course links
- [ ] **Start the validation study** (top-3 vs lecturer/mock ground truth)

### P4
- [ ] Wire real data into results + dashboard (Chart.js cohort gaps)
- [ ] Accessibility pass (ARIA labels, contrast, keyboard nav)

### P5
- [ ] LLM feedback on **scrubbed** text (+ templated fallback if API fails)
- [ ] Build Responsible-AI slide (Guide §5); deploy app to free tier
- [ ] **Scope freeze at noon** — after this, bugfix + polish only
- [ ] End-of-day: full flow works on the deployed URL

---

## DAY 3 — Wed 29 Oct · Polish, Validate, Rehearse (deadline today)

### P1 + P2
- [ ] Bug fixes + edge cases (empty resume, unsupported file); freeze code
- [ ] Final `smoke_test.py` green

### P3
- [ ] Finalise validation numbers → Validation slide (≥80% top-3 agreement, +20% after feedback)
- [ ] Write one honest limitation + one failure case

### P4
- [ ] Final UI polish; test on a real phone; fix accessibility warnings

### P5
- [ ] **Record backup demo video** (in case live demo fails)
- [ ] Finalise deck; rehearse pitch 3× timed; prep Q&A on PII + competitors
- [ ] Last 3 hours = no code, rehearsal + submission only

---

## Push the repo (P1 — do this first so the team can clone)

```bash
cd /Users/hilmanashraf/SiapLi
git init
git add .
git commit -m "Day 1: Flask skeleton, DB schema, matching engine, PII-safe upload"
# then create an empty repo on GitHub and:
git branch -M main
git remote add origin https://github.com/<your-username>/siapli.git
git push -u origin main
```

Teammates then: `git clone`, create a branch (`git checkout -b p2-nlp`), work, open PRs.
