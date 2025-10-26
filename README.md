# Performance-Review-and-Recommender-System

An AI-driven service that scores employee promotion readiness and recommends personalized training plans.

## Quickstart (local)
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
