# HACKPIRE LUMINA — Updated Canvas

**Team:** NullForce
**Project:** SiapLI — AI Internship Readiness & Matching for Students
**Status:** Working prototype (not just a plan) — updated after build

> This updates the round-1 canvas to reflect what is now actually built and
> tested. Changes vs. round 1 are noted in _italics_.

---

## PROBLEM
Students struggle to find internships (LI) that match their skills, and don't
know which skills they are missing. This affects Year 2–3 students preparing for
industrial training. They apply blindly, face many rejections, and get placed
late. Universities only see skill gaps when it's too late.

---

## CUSTOMER ELEMENT
- **Target users:** undergraduate students preparing for internships.
- **Also benefits:** university career / industrial-training units, and
  employers looking for suitable interns.
- **Benefits most:** students with no industry network or guidance.

---

## UNIQUE VALUE PROPOSITION
We help students see **which internships they're ready for now** and **what to
learn next** — explaining *why* they match a role, not just listing jobs.
_Now delivered as a working app with two recommendation modes and a live link to
real openings._

---

## SOLUTION  _(now built, not planned)_
A web app where a student uploads a resume and gets:
- A **match score (%)** and skills-covered breakdown for each internship.
- **Option 1 — Exact Target Role Match:** the single best match for a chosen
  role, with matched vs missing skills and a free course per gap.
- **Option 2 — Alternative Related Roles:** data-grounded alternatives that fit
  the student's current skills better, each explaining *why* it's a good fit.
- **AI resume feedback** tailored to a target role (privacy-safe, no PII sent).
- A **"Find live openings"** button that opens a live search for that role type.
- A **cohort dashboard** showing common skill gaps for career units.

---

## CHANNELS
- **Reach:** faculty and class group chats, student societies, the industrial
  training unit, and Instagram/TikTok demos.
- **Access:** a mobile-friendly web app, no install needed.

---

## REVENUE / FUNDING MODEL
- **Free** for students.
- **Universities** pay a yearly licence for the cohort dashboard.
- **Employers** pay for featured internship listings.
- **Grants / partners:** TalentCorp, MDEC, university innovation funds.

---

## COST STRUCTURE  _(confirmed during build)_
- **Tools:** Python, Flask, SQLite, spaCy, sentence-transformers — all free.
- **AI feedback:** rule-based and runs locally — **RM0, no API cost** _(changed:
  we no longer depend on a paid LLM; this also removed a privacy risk)._
- **Hosting:** free tier (RM0). **Domain:** ~RM50/year (optional).
- **Main resource:** team development time.

---

## KEY METRICS  _(now measured, not just targeted)_
- **Matching accuracy:** top-3 agreement with reference judgement — **100%
  (25/25) in our proxy study** (target was ≥80%).
- **Match-score improvement after acting on feedback:** **+20.3 points average**
  (target was +20%).
- Number of resumes analysed and active users.
- Time saved finding suitable internships.
_(Honest caveat: ground truth is a proxy pending a real lecturer pilot.)_

---

## UNFAIR ADVANTAGES
- We are the target users and understand the LI struggle first-hand.
- Direct access to classmates for testing.
- Can pilot with our faculty's industrial training unit.
- Focused on Malaysian internship roles.
- _New:_ **explainable** matching (we show matched/missing skills, not a
  black-box score) and a **university cohort view** no job board offers.

---

## UNIQUE / COMPETITOR POSITION  _(new — judges flagged this was missing)_
Existing Malaysian players are **job boards** (Hiredly, Ricebowl, JobStreet,
A Job Thing, FastApply) or an interview tool (Monash CareerEdge). None combine:
**readiness scoring + skill-gap diagnosis + a university cohort dashboard**,
internship-specific and Malaysia-first.
> "They answer *which job*. We answer *are you ready, and what next.*"

---

## RESPONSIBLE & ETHICAL USE  _(strengthened — judges scored this low)_
- Raw resume file is **never stored** — read once, then discarded.
- **PII removed** (name, email, phone, IC, links) **before any analysis**.
- **Consent** required; students can **delete their data** anytime.
- AI feedback is **rule-based and local** — no student data leaves the app.
- Job postings contain **no personal data**; apply links are LinkedIn searches
  (no scraping, nothing invented). Aligns with Malaysia's **PDPA** principles.

---

## DATA  _(now real)_
- **75 real Malaysian IT internships** (software, data, AI, network, systems,
  security) across real companies — _replaced the earlier synthetic samples._
- **~230-skill** dictionary + **88 free-course** links for gap closing.
- **25 anonymised sample resumes** for the cohort dashboard demo.

---

## ROADMAP

**PHASE 1 — Prototype (DONE)**
Resume upload, PII scrubbing, spaCy skill extraction, embedding match score,
skill-gap report + courses, two recommendation options, AI feedback, cohort
dashboard, 75 real internships, automated tests passing.

**PHASE 2 — Pilot**
Replace proxy validation with a real industrial-training-unit study; deep-link
apply buttons to employers' own application pages; expand postings and skills;
deploy to a public URL.

**PHASE 3 — Scale**
Employer side (featured listings), university licences, more faculties, official
employer/university data feeds, link-health checks.

---

## WHAT CHANGED SINCE ROUND 1 (quick reference for the pitch)
1. Plan → **working, tested prototype**.
2. Added **competitor comparison** (was missing).
3. **Validation with real numbers** (100% top-3, +20.3 lift).
4. **Responsible-use hardened** (local AI, no PII to external services) + a
   documented failure case we caught and fixed.
5. **Real data** (75 Malaysian internships) replacing synthetic samples.
6. Added **AI resume feedback** and **two recommendation options**.
