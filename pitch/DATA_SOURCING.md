# SiapLI — Data Sourcing, Copyright & Privacy (presentation notes)

Keep this handy for the pitch and Q&A. It explains where our data comes from,
why it's responsible, and the honest caveats — turning a potential "gotcha"
question into a point in our favour.

---

## 1. What data is in the system

| Data | Source | Contains personal data? |
|---|---|---|
| **Internship postings** (title, company, location, skills, apply URL) | Public listings aggregated by **Prosple** (a graduate/internship aggregator) | No — company adverts, not individuals |
| **Sample postings** | Synthetic (written by us for the demo) | No |
| **Skills dictionary & courses** | Curated by us; course links to free public providers | No |
| **Student resumes** | Uploaded by the student | Yes — handled carefully (see §3) |

---

## 2. Copyright & terms of use (say this if asked about sourcing)

- The real internships are **public postings aggregated by Prosple**. We copied
  factual fields (role title, company, location, required skills) and the
  listing's apply link into our database for a **non-commercial student
  prototype**.
- **Descriptions are paraphrased in our own words**, not copied verbatim — this
  avoids reproducing their copyrighted text.
- Factual data (who is hiring, for what role, what skills) is generally not
  itself copyrightable; the *presentation/compilation* can be. Paraphrasing +
  non-commercial use keeps us on safe ground for a prototype.

**Honest line for the pitch:**
> "Our internship listings are public postings aggregated for this prototype.
> A production version would use official employer feeds or direct university /
> employer partnerships rather than a third-party aggregator."

**What we did NOT do (and should say so):**
- We did **not** scrape sites that forbid it (no LinkedIn / Indeed / JobStreet
  scraping).
- We did **not** invent fake application URLs or point 'Apply' at a company
  homepage as a substitute.

**Known caveat to be upfront about:**
- The apply links currently point to the **aggregator's listing page**, which
  then links to the employer — one hop from the employer's own apply form.
  That's honest (not a homepage substitute), and a production version would
  resolve to the employer's direct application page.

---

## 3. Privacy (this is our strength — lead with it)

- The sensitive data is the **student resume**, and we treat it carefully:
  - The raw file is **never stored** — read once, then discarded.
  - **PII is removed** (name, email, phone, ID, links) **before any analysis**.
  - **Consent** is required before a resume is processed.
  - Students can **delete their data** at any time.
- Job postings contain **no personal data**, so they raise no privacy concern.
- Cohort dashboard is **aggregated and anonymous**; small groups are hidden.

Relevant law: Malaysia's **PDPA** governs personal data of individuals. Our
design (scrub-before-process, consent, deletion) aligns with its principles.
Company job adverts are not personal data.

---

## 4. One-line summaries for the slide / Q&A

- **"Is this real data?"** → "Yes — real public Malaysian internship postings,
  aggregated via Prosple for the prototype; descriptions paraphrased by us."
- **"Any copyright issue?"** → "Non-commercial student use, factual fields +
  paraphrased summaries, no scraping of sites that forbid it. Production would
  use official employer feeds."
- **"What about student privacy?"** → "Raw file never stored, PII stripped
  before analysis, consent required, one-click delete. PDPA-aligned."

---

## 5. To-do before a real/commercial launch (shows maturity if asked)
- Replace aggregator data with **official employer or university feeds**.
- Resolve apply links to the **employer's direct application page**.
- Review the data provider's **terms of service** for redistribution.
- Add visible **attribution** for listing sources.
