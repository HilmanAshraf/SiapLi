# SiapLI — Data Sourcing, Copyright & Privacy (presentation notes)

Keep this handy for the pitch and Q&A. It explains where our data comes from,
why it's responsible, and the honest caveats — turning a potential "gotcha"
question into a point in our favour.

---

## 1. What data is in the system

| Data | Source | Contains personal data? |
|---|---|---|
| **Internship postings** (title, company, location, skills) | Real Malaysian roles compiled from public listings; the roles and companies are genuine | No — company adverts, not individuals |
| **Apply links** | A **live LinkedIn job search** for that role + `location=Malaysia` | No |
| **Sample postings** | Synthetic (written by us for demo volume) | No |
| **Skills dictionary & courses** | Curated by us; course links to free public providers | No |
| **Student resumes** | Uploaded by the student | Yes — handled carefully (see §3) |

---

## 2. How "Apply Now" works (important — explain this clearly)

- Each internship's **Apply Now** button opens a **live LinkedIn job search**
  for that field in Malaysia, e.g.
  `linkedin.com/jobs/search/?keywords=network+engineer+intern&location=Malaysia`.
- We deliberately use **broad, field-level keywords** (e.g. "network engineer
  intern", "cybersecurity intern") rather than one specific posting URL.

**Why we chose a live search instead of a fixed posting URL:**
- A specific posting URL **expires** when the role closes — students hit dead
  links. A live search always shows **current** openings for that field.
- It's honest: it's a genuine LinkedIn search, not a fabricated vacancy and not
  a company homepage substitute.

**Honest line for the pitch:**
> "Apply opens a live LinkedIn search for that role in Malaysia, so students
> always land on current openings rather than an expired link. A production
> version would integrate official employer feeds and deep-link to each
> employer's own application page."

**The tradeoff to acknowledge:**
- The student lands on a **search results page** for that field, then clicks
  into the specific posting — one step more than a direct apply form. We chose
  reliability (never a dead link) over that one extra click.

---

## 3. Copyright & terms of use (say this if asked)

- The role/company information is **factual public data** (who hires, for what
  role, what skills). Factual data is generally not copyrightable; only a
  specific creative *presentation* would be — and we don't copy that.
- **Descriptions are written in our own words**, not copied verbatim from any
  listing.
- Apply links are **LinkedIn search query URLs** — just a URL with keywords, not
  copied LinkedIn content.
- We did **not scrape** LinkedIn / Indeed / JobStreet (which forbid it); we
  built search links by hand.
- We did **not invent** vacancies or point Apply at a company homepage as a
  substitute.

---

## 4. Privacy (this is our strength — lead with it)

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

## 5. One-line summaries for the slide / Q&A

- **"Is this real data?"** → "The roles and companies are real Malaysian
  internships. Apply opens a live LinkedIn search for that field, so it always
  shows current openings."
- **"Why a search link, not the exact posting?"** → "Specific posting links
  expire; a live search never goes stale. We chose reliability over one extra
  click."
- **"Any copyright issue?"** → "Factual role data, our own descriptions, search
  URLs only, no scraping, nothing invented. Non-commercial student prototype."
- **"What about student privacy?"** → "Raw file never stored, PII stripped
  before analysis, consent required, one-click delete. PDPA-aligned."

---

## 6. To-do before a real/commercial launch (shows maturity if asked)
- Integrate **official employer or university feeds** for live, structured data.
- **Deep-link** each Apply button to the employer's own application page.
- Add visible **source attribution** for listings.
- Add link-health checks so any dead link is caught automatically.

---

## 7. Honest limitation we can state ourselves
- We can't guarantee every field has an open posting at any given moment —
  but because Apply runs a live search, the button never points at a dead
  posting; at worst it shows the current (possibly short) list for that field.
