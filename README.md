# Performance-Review-and-Recommender-System

An AI-driven service that scores employee promotion readiness and recommends personalized training plans.


## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt

# create instance db + data
python -m scripts.create_db
python scripts/generate_big_data.py
python scripts/seed_all_from_csv.py

# train model
python ml/train_big.py

# run API
flask run

## Endpoints
```bash
GET /v1/ingest/health

POST /v1/promotion/score

POST /v1/plan/recommend

GET /v1/explain/local?employee_id=1

GET /v1/fairness/summary

## Frontend

A simple single-file React dashboard lives in templates/index.html (open /dashboard once the API runs).

## Environment

Set your variables in .env (not committed). Example:

FLASK_ENV=development
DATABASE_URL=sqlite:////absolute/path/to/prr-flask/instance/prr.db
MODEL_DIR=ml/artifacts
PROMOTE_THRESH=0.72
BORDERLINE_LOW=0.60
SECRET_KEY=dev_secret_key_change_me
LOG_LEVEL=DEBUG

Publish the app (API + dashboard)

You’ve got two simple paths. Pick one.

Option 1 — Render (free-tier friendly)
1) Add production dependencies
pip install gunicorn
echo "gunicorn==23.0.0" >> requirements.txt

2) Add a Procfile
cat > Procfile << 'P'
web: gunicorn wsgi:application --log-file -
P

3) Choose a database strategy

Best: Managed PostgreSQL on Render.

In Render: Databases → PostgreSQL → copy its DATABASE_URL.

Optional local test:

# example format
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME


Install driver:

pip install psycopg2-binary
echo "psycopg2-binary==2.9.9" >> requirements.txt


Your app should run db.create_all() (or Alembic migrations) on startup. To seed data into the cloud DB, you’ll run the seeder from your laptop (step 6).

4) Push the latest
git add .
git commit -m "Render deployment: gunicorn + Procfile + psycopg2"
git push

5) Create a web service on Render

New + → Web Service → GitHub repo

Environment: Python 3.x

Build command:

pip install -r requirements.txt


Start command:

gunicorn wsgi:application --log-file -


Environment variables (Dashboard → Environment):

FLASK_ENV=production
MODEL_DIR=ml/artifacts
PROMOTE_THRESH=0.72
BORDERLINE_LOW=0.60
SECRET_KEY=<secure random>       # generate with: python -c "import secrets; print(secrets.token_hex(32))"
DATABASE_URL=<your Render Postgres URL>   # critical
# Optional:
LOG_LEVEL=INFO


Deploy. You’ll get a public URL like:

https://your-prr.onrender.com

6) Seed the cloud DB from your laptop
# New terminal
cd prr-flask
export DATABASE_URL="postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME"

# if needed:
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# generate CSVs locally and seed into the cloud DB
python scripts/generate_big_data.py
python scripts/seed_all_from_csv.py

# (Optional) train locally and commit artifacts
python ml/train_big.py
git add ml/artifacts
git commit -m "Add model artifacts"
git push


Render redeploys; your API will load ml/artifacts/model.pkl from the repo.

7) Open your dashboard
https://your-prr.onrender.com/dashboard
