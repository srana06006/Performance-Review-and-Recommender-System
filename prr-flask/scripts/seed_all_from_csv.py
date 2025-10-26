import os, sys, sqlite3, math, json, random
from pathlib import Path
import pandas as pd
import numpy as np

# Resolve DB path from DATABASE_URL (supports sqlite:///relative.db or sqlite:////abs/path.db)
def _resolve_db_path():
    url = os.getenv("DATABASE_URL", "").strip()
    if url.startswith("sqlite:///"):
        p = url.replace("sqlite:///", "", 1)
        # absolute if it starts with '/', else relative to CWD
        return p if p.startswith("/") else str(Path.cwd() / p)
    elif url.startswith("sqlite:////"):
        return url.replace("sqlite:////", "/", 1)
    # default to instance/prr.db if present, else project root prr.db
    inst = Path("instance") / "prr.db"
    return str(inst if inst.parent.exists() else Path("prr.db"))

DB_PATH = _resolve_db_path()
DATA_DIR = Path("data")
RNG = np.random.default_rng(2025)

def ensure_db():
    """Create schema if DB file is missing."""
    if Path(DB_PATH).exists():
        return
    print(f"⚠️  {DB_PATH} not found. Initializing schema now...")
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from app import create_app
    from prr.utils.db import db
    app = create_app()
    with app.app_context():
        db.create_all()
    if Path(DB_PATH).exists():
        print("✓ Database created.")
    else:
        print("❌ Failed to create database. Check DATABASE_URL in .env and your working directory.")
        sys.exit(1)


def connect():
    ensure_db()
    return sqlite3.connect(DB_PATH)

def truncate(conn, table):
    try:
        conn.execute(f"DELETE FROM {table}")
        conn.commit()
        print(f"✓ Cleared {table}")
    except Exception as e:
        print(f"… skipping clear for {table}: {e}")

def seed_employees(conn):
    csv = DATA_DIR / "employees_500.csv"
    if not csv.exists():
        print(f"❌ {csv} not found. Generate data first: python scripts/generate_big_data.py")
        sys.exit(1)
    df = pd.read_csv(csv)
    out = df.rename(columns={"employee_id":"id"})
    out["manager_id"] = None
    out["location"] = "HQ"
    out["employment_type"] = "Full-Time"
    cols = ["id","name","org_unit","manager_id","current_rank","last_promotion_date","location","employment_type"]
    truncate(conn, "employee")
    out[cols].to_sql("employee", conn, if_exists="append", index=False)
    print(f"✓ Seeded employee ({len(out):,} rows)")

def seed_project_activity(conn):
    csv = DATA_DIR / "monthly_activity_2005_2014.csv"
    if not csv.exists():
        print(f"❌ {csv} not found. Generate data first: python scripts/generate_big_data.py")
        sys.exit(1)
    monthly = pd.read_csv(csv)
    # Map monthly → project_activity schema (1 row per month per employee)
    # We’ll use the last day of month as date; role by org_unit; on_time boolean from on_time_ratio
    def last_day(period_str):
        # period like "2005-01"
        year, month = map(int, str(period_str).split("-"))
        if month == 12:
            return f"{year}-12-31"
        from calendar import monthrange
        d = monthrange(year, month)[1]
        return f"{year}-{month:02d}-{d:02d}"

    role_map = {
        "Sales":"Account Exec", "Engineering":"Engineer", "Software Development":"Engineer",
        "IT":"Analyst", "Operations":"Coordinator", "Marketing":"Specialist",
        "Finance":"Analyst", "HR":"Generalist"
    }

    df = monthly.copy()
    df["date"] = df["year_month"].apply(last_day)
    df["project_id"] = "PRJ-" + (df["employee_id"] % 50).astype(str).str.zfill(2)
    df["role"] = df["org_unit"].map(role_map).fillna("Contributor")
    # On-time boolean per-month: compare on_time_ratio to a random threshold around 0.85
    thresh = RNG.normal(0.85, 0.05, size=len(df))
    df["on_time"] = (df["on_time_ratio"] >= np.clip(thresh, 0.6, 0.98)).astype(int)
    df = df.rename(columns={
        "quality_mean":"quality_score",
        "customer_impact":"customer_impact"
    })
    out = df[[
        "employee_id","date","project_id","role","hours","velocity","quality_score","on_time","customer_impact"
    ]].copy()
    truncate(conn, "project_activity")
    out.to_sql("project_activity", conn, if_exists="append", index=False)
    print(f"✓ Seeded project_activity ({len(out):,} rows)")

def _pick_rel():
    return RNG.choice(["peer","direct","cross-functional","client"], p=[0.5,0.3,0.15,0.05])

def seed_feedback360(conn, n_per_emp=6):
    # synthetic 360s (since we don’t have a CSV for it)
    emp = pd.read_sql_query("SELECT id FROM employee", conn)
    rows = []
    for eid in emp["id"].tolist():
        for i in range(n_per_emp):
            rows.append({
                "employee_id": eid,
                "rater_id": int(RNG.integers(1, len(emp)+1)),
                "date": str(pd.Timestamp(RNG.integers(2009,2015), RNG.integers(1,13), RNG.integers(1,28)).date()),
                "dimension": RNG.choice(["Leadership","Collaboration","Communication","Execution"]),
                "rating": int(np.clip(round(RNG.normal(4.1, 0.6)), 1, 5)),
                "relationship": _pick_rel(),
                "comment_redacted": RNG.choice(["Great work on Q3 project.","Improved collaboration.","Could communicate timelines better.","Strong execution."])
            })
    df = pd.DataFrame(rows)
    truncate(conn, "feedback360")
    df.to_sql("feedback360", conn, if_exists="append", index=False)
    print(f"✓ Seeded feedback360 ({len(df):,} rows)")

def seed_manager_review(conn, n_per_emp=4):
    emp = pd.read_sql_query("SELECT id FROM employee", conn)
    rows = []
    for eid in emp["id"].tolist():
        for yr in [2011,2012,2013,2014][:n_per_emp]:
            rows.append({
                "employee_id": eid,
                "period": f"{yr}-H{RNG.integers(1,3)}",
                "dimension": RNG.choice(["Impact","Ownership","Leadership","Craft"]),
                "rating": int(np.clip(round(RNG.normal(4.0, 0.7)), 1, 5)),
                "narrative_redacted": RNG.choice(["Solid progress","Ready for more scope","Needs delegation practice","Strong partner mgmt"])
            })
    df = pd.DataFrame(rows)
    truncate(conn, "manager_review")
    df.to_sql("manager_review", conn, if_exists="append", index=False)
    print(f"✓ Seeded manager_review ({len(df):,} rows)")

def seed_learning_history(conn, max_courses_per_emp=5):
    emp = pd.read_sql_query("SELECT id FROM employee", conn)
    providers = ["LinkedIn Learning","Coursera","Udemy","Internal"]
    skills = ["Leadership","Time Management","System Design","Data Analysis","Negotiation","Project Mgmt"]
    rows = []
    for eid in emp["id"].tolist():
        k = int(RNG.integers(0, max_courses_per_emp+1))
        for _ in range(k):
            sdate = pd.Timestamp(RNG.integers(2010,2015), RNG.integers(1,13), RNG.integers(1,28))
            edate = sdate + pd.Timedelta(days=int(RNG.integers(3,30)))
            rows.append({
                "employee_id": eid,
                "course_id": f"C{RNG.integers(100,999)}",
                "start_dt": str(sdate.date()),
                "end_dt": str(edate.date()),
                "completion": bool(RNG.integers(0,2)),
                "assessment_score": int(RNG.integers(60,100)),
                "hours": int(RNG.integers(2,16))
            })
    df = pd.DataFrame(rows)
    truncate(conn, "learning_history")
    df.to_sql("learning_history", conn, if_exists="append", index=False)
    print(f"✓ Seeded learning_history ({len(df):,} rows)")

def seed_incidents(conn, rate=0.08):
    emp = pd.read_sql_query("SELECT id FROM employee", conn)
    severities = ["Low","Medium","High"]
    rows = []
    for eid in emp["id"].tolist():
        if RNG.random() < rate:
            n = int(RNG.integers(1,3))
            for _ in range(n):
                rows.append({
                    "employee_id": eid,
                    "date": str(pd.Timestamp(RNG.integers(2010,2015), RNG.integers(1,13), RNG.integers(1,28)).date()),
                    "type": RNG.choice(["Policy","Quality","Security","Conduct"]),
                    "severity": RNG.choice(severities, p=[0.7,0.25,0.05])
                })
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["employee_id","date","type","severity"])
    truncate(conn, "incidents")
    if len(df):
        df.to_sql("incidents", conn, if_exists="append", index=False)
    print(f"✓ Seeded incidents ({len(df):,} rows)")

def seed_recognition(conn, avg_per_emp=2.5):
    emp = pd.read_sql_query("SELECT id FROM employee", conn)
    badges = ["Kudos","Customer Hero","Team Player","Innovator","Mentor"]
    rows = []
    for eid in emp["id"].tolist():
        k = np.random.poisson(avg_per_emp)
        for _ in range(k):
            rows.append({
                "employee_id": eid,
                "date": str(pd.Timestamp(RNG.integers(2010,2015), RNG.integers(1,13), RNG.integers(1,28)).date()),
                "badge_type": RNG.choice(badges),
                "nominator_id": int(RNG.integers(1, len(emp)+1))
            })
    df = pd.DataFrame(rows)
    truncate(conn, "recognition")
    df.to_sql("recognition", conn, if_exists="append", index=False)
    print(f"✓ Seeded recognition ({len(df):,} rows)")

def seed_competency_framework(conn):
    rows = []
    ranks = ["IC","Senior","Lead","Manager"]
    comp = ["Leadership","Collaboration","Communication","Execution","System Design","Customer Focus"]
    for r in ranks:
        for c in comp:
            rows.append({
                "rank": r,
                "competency": c,
                "expected_level": {"IC":1,"Senior":2,"Lead":3,"Manager":3}[r],
                "rubric_json": json.dumps({"examples":[f"{c} examples for {r}"],"anchors":[1,2,3,4]})
            })
    df = pd.DataFrame(rows)
    truncate(conn, "competency_framework")
    df.to_sql("competency_framework", conn, if_exists="append", index=False)
    print(f"✓ Seeded competency_framework ({len(df):,} rows)")

def seed_catalog(conn):
    rows = [
        {"course_id":"L-LEAD-101","title":"Leading Teams Under Pressure","provider":"LinkedIn Learning","modality":"online","duration_h":6,"skills_json":json.dumps(["Leadership","Conflict Resolution"]),"price":0,"internal_flag":0},
        {"course_id":"U-TM-200","title":"Advanced Time Management","provider":"Udemy","modality":"online","duration_h":5,"skills_json":json.dumps(["Time Management","Prioritization"]),"price":0,"internal_flag":0},
        {"course_id":"C-SD-310","title":"System Design for Scaling","provider":"Coursera","modality":"online","duration_h":12,"skills_json":json.dumps(["System Design","Architecture"]),"price":0,"internal_flag":0},
        {"course_id":"INT-MENT-001","title":"Internal Mentoring Program","provider":"Internal","modality":"blended","duration_h":8,"skills_json":json.dumps(["Mentorship","Leadership"]),"price":0,"internal_flag":1},
    ]
    df = pd.DataFrame(rows)
    truncate(conn, "catalog")
    df.to_sql("catalog", conn, if_exists="append", index=False)
    print(f"✓ Seeded catalog ({len(df):,} rows)")

def main():
    conn = connect()
    try:
        seed_employees(conn)
        seed_project_activity(conn)
        # Optional synthetic tables (uncomment any you want to skip)
        seed_feedback360(conn)
        seed_manager_review(conn)
        seed_learning_history(conn)
        seed_incidents(conn)
        seed_recognition(conn)
        seed_competency_framework(conn)
        seed_catalog(conn)
        print("🎉 All seeds completed.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
