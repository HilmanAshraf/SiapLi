# Failure Case We Caught & Fixed (P5 — for Validation & Responsible-AI slides)

Judges scored **Validation & Performance 4/10** and **Responsible & Ethical
Use 4/10**. This real bug from our own build directly answers both: it shows
testing that caught an error, and a responsible-data-handling fix.

Use it as the "honest limitation / failure case" slide. Keep it to one slide.

---

## The one-liner (say this)
"While testing our PII scrubber, we found it was silently deleting real skills.
We caught it, understood why, and fixed it — here's how."

---

## What happened
Our pipeline removes personal info (name, email, phone, IC) from a resume
before storing it or sending anything to an AI model. The PII remover uses a
named-entity model (spaCy) to spot people and places.

The model mislabelled technical terms as **place names** — it tagged **"Python"
and "Flask" as locations** and replaced them with `[PLACE]`. Because scrubbing
ran *before* we read the skills, those skills vanished from the analysis.

**Impact if shipped:** a student skilled in Python/Flask would be told they are
*missing* Python/Flask — the opposite of the truth. Match scores and the
skill-gap report would be wrong, and the cohort dashboard would over-report gaps.

## How we caught it
Our automated end-to-end test (`smoke_test.py`) asserts that a resume saying
"Python, Flask, SQL..." actually yields those skills. The test **failed** the
moment we switched on the real NER model:

```
AssertionError: skills off: ['Data Analysis', 'Git', 'React', 'SQL', 'Teamwork']
# expected Python and Flask — they were missing
```

## Root cause
Two design mistakes, both about **order and trust**:
1. We extracted skills from the *scrubbed* text. Skills are not PII, so they
   should be read from the original text.
2. We trusted the NER model's labels blindly. NER is probabilistic and
   mislabels out-of-domain tokens like tech terms.

## The fix
1. **Extract skills from the original text** (skills are not personal data).
2. **Protect known skills from scrubbing** — the scrubber now skips any entity
   that matches our skills dictionary, so even the stored/LLM-bound text keeps
   legitimate technical terms.
3. We also tightened the phone-number pattern so `+60...` numbers scrub fully.

After the fix, the same test passes and the real model confirms correct output.

## Before vs after (put on the slide)

| Input resume text | Before fix | After fix |
|---|---|---|
| "Skilled in Python, Flask, SQL..." | Python & Flask **deleted** as `[PLACE]`; marked as skill gaps | Python & Flask **kept** and detected |
| "Ahmad bin Ali, ahmad@gmail.com, +60123456789, 900101-14-5523, Kuala Lumpur" | — | name→`[NAME]`, email→`[EMAIL]`, phone→`[PHONE]`, IC→`[IC]`, Kuala Lumpur→`[PLACE]`, Python kept |

## Why this matters for the judges
- **Validation & Performance:** we have automated tests that catch regressions,
  and we interpret failures with evidence (the exact assertion + root cause).
- **Responsible & Ethical Use:** PII is still removed before storage or any
  external AI call — but we learned that naive scrubbing can damage the data,
  so we added a safeguard. This is human oversight of an imperfect model.

## Known limitations we still acknowledge
- NER is not perfect; rare names shaped like tech terms may slip through either
  way. We mitigate with the skills allow-list + regex for structured PII.
- Our skills dictionary (~150 now, ~400 planned) isn't exhaustive, so a very
  niche skill could still be miscategorised. It's extensible.
