# SiapLI — AI Internship Readiness & Matching

Team NullForce · Hackspire Lumina · Flask + SQLite + spaCy + sentence-transformers

## Quick start

```bash
# 1. Create & activate a virtualenv
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm   # only needed once P2's NLP is wired in

# 3. Set up the database + sample data
python db.py          # create tables
python seed_data.py   # load sample postings & skills

# 4. Run the app
python app.py         # http://127.0.0.1:5000
```

> First run installs `requirements.txt`. If sentence-transformers isn't
> installed yet, matching falls back to a keyword score so the app still runs.

## Smoke test (no browser)

```bash
python smoke_test.py   # verifies upload -> match -> PII scrub -> dashboard
```

## Project layout

| File | Owner | Purpose |
|---|---|---|
| `app.py` | P1 | Flask routes (/, /upload, /results, /dashboard) |
| `db.py` | P1 | SQLite schema + helpers |
| `matching.py` | P1 | Embedding match score + skill-gap ranking |
| `nlp_stub.py` | P2 | **Stub** — real text extraction, spaCy skills, PII scrub go here |
| `seed_data.py` | P3 | Sample postings + skills (replace with real dataset) |
| `templates/` | P4 | Jinja2 + Bootstrap pages |
| `smoke_test.py` | P1 | End-to-end test |

## Integration contract (keep these signatures stable)

`nlp_stub.py` (P2 replaces internals, not signatures):
- `extract_text(file_path) -> str`
- `extract_skills(text) -> list[str]`
- `scrub_pii(text) -> str`

As long as these hold, `app.py` needs no changes when P2 swaps in real NLP.

## Responsible AI
- Raw uploads are **never persisted** — deleted right after text extraction.
- PII (email, phone, Malaysian IC) is scrubbed before storage/any LLM call.
- Consent checkbox is required on upload and stored per resume.
