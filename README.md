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
