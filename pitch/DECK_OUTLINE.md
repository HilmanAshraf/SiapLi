# SiapLI — Pitch Deck Outline (P5, Day 1)

Target: lift score from 51–63 → 75+. Order the deck so the weak areas
(competitors, responsible AI, validation) are visibly addressed.

Suggested length: 8–10 slides, ~5 min pitch + Q&A.

---

## Slide 1 — Title
- **SiapLI: AI Internship Readiness & Matching for Students**
- Team NullForce · Hackspire Lumina
- One line: "We tell students if they're ready for an internship — and what to learn next."

## Slide 2 — Problem
- Year 2–3 students apply blindly, face rejections, get placed late.
- Universities only see skill gaps when it's too late.
- Evidence: MY employers report persistent graduate digital-skills gaps.

## Slide 3 — Solution (demo-driven)
- Upload resume → match score % → skill-gap report + free courses → AI feedback.
- Two recommendation modes: **Match My Skills** and **Explore My Preferred Field**.
- **Target a role**: see the single best match + **alternative related roles**
  that fit your current skills better (motivates students who aren't ready yet).
- **AI resume feedback** per target role (privacy-safe, runs on scrubbed text).
- University cohort dashboard of common gaps.
- **Show the live demo or the backup video here.**

## Slide 4 — Competitor comparison  ← WAS MISSING (judge feedback)
- Table: Hiredly, Ricebowl, JobStreet, A Job Thing, FastApply, Monash CareerEdge.
- Our wedge: readiness + skill-gap diagnosis + university cohort dashboard,
  internship-specific and Malaysia-first, with explainable matches.
- Line to say: "They answer *which job*. We answer *are you ready, and what next*."

## Slide 5 — How it works
- Resume → PII scrub → spaCy skill extraction → sentence-transformer embeddings
  → cosine similarity match score → skill-gap = required − have.
- Emphasise **explainability**: we show which skills matched/missed.

## Slide 6 — Responsible AI  ← SCORED 4/10 (judge feedback)
- Raw file never stored; deleted right after text extraction.
- PII (name, email, phone, IC, places) scrubbed BEFORE any external LLM call.
- Consent required and stored per resume.
- Human-in-the-loop: scores are decision support, not gatekeeping.
- Bias noted; mitigated by showing the explainable skill list.
- **Data sourcing & copyright** (full notes in pitch/DATA_SOURCING.md):
  - Internship listings are PUBLIC postings aggregated via Prosple for this
    prototype; descriptions paraphrased in our own words (not copied verbatim).
  - No scraping of sites that forbid it; no invented apply URLs; no homepage
    substitutes.
  - Honest line to say: "Listings are public postings aggregated for the
    prototype; production would use official employer feeds."
  - Job postings contain NO personal data — the privacy care is on the resume.

## Slide 7 — Validation  ← SCORED 4/10 (judge feedback)
- **Real numbers (from `python validation.py`): top-3 agreement 100% (25/25),
  average match-score lift +20.3 points after learning the gaps.** The +20
  lands on our pitch metric.
- Honestly labelled: ground truth is a PROXY (each resume's intended role), a
  stand-in for lecturer judgement — the real pilot replaces it with the
  industrial-training-unit's rankings. Say this out loud; honesty scores.
- Honest limitation: small sample (n=25), skills list not exhaustive.
- **Failure case we caught & fixed** → see pitch/FAILURE_CASE.md (the PII
  scrubber was deleting real skills; our test caught it; we fixed it).
  This doubles as evidence for Slide 6 (Responsible AI).
- Full numbers + per-resume table in pitch/VALIDATION_RESULTS.md.

## Slide 8 — Impact & feasibility
- Free for students; university licence; employer featured listings.
- Costs ~RM0 (free tiers) + small AI API; built on Flask/SQLite/spaCy.
- Metrics: resumes analysed, active users, time saved, match-score lift.

## Slide 9 — Roadmap
- Phase 1 (done): prototype — upload, match, skill-gap, dashboard, PII scrub.
- Phase 2: more postings/resumes, LLM feedback, pilot with industrial training unit.
- Phase 3: employer side, expand skills, scale to more faculties.

## Slide 10 — Team & learning
- 5 roles: Backend/Matching, NLP, Data, Frontend, PM/Responsible-AI.
- What we learned + realistic next steps.

---

## Judge Q&A — rehearse these two
1. **"How do you protect student PII?"** → Slide 6, five points.
2. **"How are you different from Hiredly / Ricebowl?"** → Slide 4, the wedge.
