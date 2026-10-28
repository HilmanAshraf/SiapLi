# Deploy SiapLI to a free tier (P5)

Two easy options. **Render** is the simplest for a Flask app.

## Option A — Render (recommended)
1. Push the repo to GitHub (done: https://github.com/HilmanAshraf/SiapLi).
2. Go to https://render.com → New → **Web Service** → connect the repo.
3. Settings:
   - **Environment:** Python
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
4. Render reads `PORT` automatically; `app.py` already binds to it.
5. First deploy: the `release` step in the `Procfile` runs `db.py` + `seed_data.py`
   to create and seed the database.
6. You get a public URL like `https://siapli.onrender.com`.

> Free tier sleeps after inactivity. **Open the URL ~1 min before the pitch**
> to wake it up (avoid a cold-start during the demo).

## Option B — Railway
1. https://railway.app → New Project → Deploy from GitHub repo.
2. Railway auto-detects Python + the Procfile.
3. Add no env vars needed; it injects `PORT`.

## Notes
- `requirements.txt` includes `gunicorn` (production server).
- `runtime.txt` pins Python 3.11.
- SQLite is file-based; on free tiers the DB may reset on redeploy — fine for a
  demo because the `release` step re-seeds it every deploy.
- For the demo, the seeded sample resumes already populate the dashboard chart.

## Backup plan (demo safety)
Record a screen capture of the full flow (upload → results → dashboard) and keep
it ready in case the live site has a cold-start or network issue.
