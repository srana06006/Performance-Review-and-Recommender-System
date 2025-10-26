# Performance-Review-and-Recommender-System

An AI-driven service that scores employee promotion readiness and recommends personalized training plans.
An AI-Driven Framework for Promotion Assessment and Personalized Workforce Development

1. Introduction
Organizations today manage increasingly complex and distributed workforces, making traditional performance reviews slow, subjective, and prone to bias. The Performance Review and Recommender (PRR) system introduces an AI-assisted approach to employee evaluation — integrating data from projects, feedback, learning activities, and behavioral indicators to provide:
•	Promotion readiness scoring: Identifying employees most likely ready for advancement based on historical performance patterns.
•	Personalized development planning: Recommending training courses, mentorships, and projects to close specific skill gaps for those not yet ready for promotion.
The PRR system supports data-driven HR decision-making while maintaining transparency, fairness, and explainability. It embodies responsible AI principles by combining machine learning analytics with human oversight in the promotion process.

2. Objectives
a.	Automate performance evaluations using structured and unstructured HR data.
b.	Predict promotion readiness through historical pattern recognition and behavioral modeling.
c.	Provide individualized upskilling pathways via a recommendation engine.
d.	Support fairness and explainability, enabling HR managers to audit AI decisions.
e.	Offer an interactive dashboard for both managers and employees to visualize insights.

3. System Overview

3.1 Core Modules
Module	Function
•	Data Ingestion Layer:	Collects and integrates data from HRIS, LMS, project management, and feedback systems.
•	Performance Evaluation Engine:	Uses machine learning models (LightGBM, CatBoost) to compute promotion readiness scores.
•	Recommendation Engine	Matches: skill gaps with relevant courses, mentorships, and career development resources.
•	HR Dashboard:	Provides HR managers a visual interface to view scores, approve promotions, and track learning outcomes.
•	Employee Portal:	Displays personal progress reports, readiness scores, and recommended learning paths.

3.2 Data Sources
•	HR Information Systems (HRIS): Employee demographics, promotions, performance history.
•	Project Management Tools: Task completion, deadlines, quality metrics.
•	Learning Management Systems (LMS): Completed courses, skill achievements, certifications.
•	360° Feedback: Peer and manager reviews, sentiment analysis.
•	Incident/Recognition Logs: Behavioral insights and achievements.

4. Dataset Generation and Architecture
4.1 Synthetic Data Design
A large synthetic dataset was generated to emulate a realistic corporate environment:
•	Employees: 500
•	Time Range: 10 years (2005–2014)
•	Daily Tasks: 4–5 per employee
•	Departments: IT, Engineering, Sales, HR, Finance, Marketing, Operations, Software Development

<img width="468" height="645" alt="image" src="https://github.com/user-attachments/assets/7dfdaf62-69b2-42b0-aac9-2973a8ac4415" />


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
