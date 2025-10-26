# Generates 2005-2014 monthly aggregates, features, labels.
import numpy as np, pandas as pd
from pathlib import Path
import argparse, datetime as dt

ap = argparse.ArgumentParser()
ap.add_argument("--full-tasks", action="store_true", help="Also write massive per-task CSV (10 tasks/day)")
args = ap.parse_args()

DATA = Path("data"); DATA.mkdir(parents=True, exist_ok=True)
np.random.seed(123)
N_EMP = 500
ORG_UNITS = ["IT","Engineering","Sales","HR","Finance","Marketing","Operations","Software Development"]

# employees
emp = pd.DataFrame({
    "employee_id": np.arange(1, N_EMP+1),
    "name": [f"Emp {i:03d}" for i in range(1, N_EMP+1)],
    "org_unit": np.random.choice(ORG_UNITS, size=N_EMP),
    "current_rank": np.random.choice(["IC","Senior","Lead","Manager"], size=N_EMP, p=[0.55,0.28,0.12,0.05]),
    "last_promotion_date": np.random.choice(pd.date_range("2007-01-01","2013-12-31",freq="D").astype(str), size=N_EMP)
})
emp.to_csv(DATA/"employees_500.csv", index=False)

# monthly activity
months = pd.period_range("2005-01-01","2014-12-31",freq="M")
rows = []
rng = np.random.default_rng(42)
org_params = {
    "Sales":(1.8,0.7,0.80,0.07,2.4),
    "Engineering":(1.2,0.6,0.86,0.06,2.0),
    "Software Development":(1.3,0.6,0.86,0.06,2.2),
    "IT":(1.0,0.5,0.84,0.06,2.0),
    "Operations":(1.1,0.5,0.83,0.06,2.1),
    "Marketing":(0.9,0.5,0.84,0.06,2.0),
    "Finance":(0.8,0.5,0.87,0.05,1.8),
    "HR":(0.9,0.5,0.85,0.05,1.9)
}
for _, e in emp.iterrows():
    p = org_params[e["org_unit"]]
    for m in months:
        dim = m.to_timestamp(how='end').day
        tasks = 10 * dim
        vel = max(0, rng.normal(p[0], p[1])) * tasks
        qual = float(np.clip(rng.normal(p[2], p[3]), 0, 1))
        ontime = float(np.clip(rng.normal(0.90, 0.05), 0, 1))
        impact = np.clip(rng.normal(p[4], 0.8), 0, 5) * tasks
        hours_task = rng.uniform(1.0,2.0)
        rows.append([
            int(e["employee_id"]), str(m), e["org_unit"], tasks,
            round(hours_task*tasks,1), int(vel), round(qual,3),
            round(ontime,3), int(np.clip(impact,0,5*tasks))
        ])
monthly = pd.DataFrame(rows, columns=[
    "employee_id","year_month","org_unit","tasks","hours","velocity",
    "quality_mean","on_time_ratio","customer_impact"
])
monthly.to_csv(DATA/"monthly_activity_2005_2014.csv", index=False)

# features since last promotion
emp["last_promotion_date"] = pd.to_datetime(emp["last_promotion_date"])
monthly["period_end"] = pd.PeriodIndex(monthly["year_month"], freq="M").to_timestamp(how="end")
monthly["period_end"] = pd.to_datetime(monthly["period_end"])
j = monthly.merge(emp[["employee_id","org_unit","current_rank","last_promotion_date"]],
                  on=["employee_id","org_unit"], how="left")
mask = (j["period_end"] >= j["last_promotion_date"]) & (j["period_end"] <= pd.Timestamp("2014-12-31"))
j = j[mask]
feat = j.groupby("employee_id", as_index=False).agg(
    hours_total=("hours","sum"),
    velocity_total=("velocity","sum"),
    on_time_ratio=("on_time_ratio","mean"),
    quality_mean=("quality_mean","mean"),
    impact_total=("customer_impact","sum"),
    tasks_total=("tasks","sum")
)
feat["recognitions"] = np.random.poisson(lam=np.clip(feat["impact_total"]/feat["tasks_total"]/1.5, 0.2, 5.0))
feat["feedback_mean"] = np.clip(np.random.normal(4.1, 0.3, size=len(feat)), 3.0, 5.0)
feat["incidents_weight"] = np.random.choice([0,1,2,4], size=len(feat), p=[0.78,0.15,0.06,0.01])
feat["courses_completed"] = np.random.poisson(lam=2.6, size=len(feat))
def nz_norm(s):
    s = s.astype(float); return (s - s.min())/(s.max()-s.min()+1e-9)
feat["okr_attainment"] = np.clip(
    0.75 + 0.2 * nz_norm(feat["velocity_total"]) + 0.03*np.random.randn(len(feat)),
    0, 1.2
)
FSET = ["okr_attainment","feedback_mean","recognitions","courses_completed",
        "on_time_ratio","quality_mean","velocity_total","impact_total","incidents_weight"]
train_df = feat[["employee_id"] + FSET].copy()
train_df.to_csv(DATA/"training_features_2005_2014.csv", index=False)

# labels top-20%
comp = (0.22*train_df['okr_attainment'] + 0.18*(train_df['feedback_mean']/5.0) +
        0.12*train_df['recognitions'] + 0.12*train_df['courses_completed'] +
        0.12*train_df['on_time_ratio'] + 0.12*train_df['quality_mean'] +
        0.07*train_df['velocity_total'] + 0.05*train_df['impact_total'] -
        0.12*(train_df['incidents_weight']>0).astype(int))
q = float(comp.quantile(0.8))
labels = (comp >= q).astype(int)
lbl = pd.DataFrame({
    "employee_id":train_df["employee_id"],
    "as_of":"2014-12-31",
    "readiness_score":comp.round(3),
    "decision":[ "PROMOTE" if c>=q else ("BORDERLINE" if c>=q-0.05 else "HOLD") for c in comp ],
    "label": labels
})
lbl.to_csv(DATA/"promotion_labels_2014.csv", index=False)

# optional huge per-task CSV
if args.full_tasks:
    out = DATA/"full_project_tasks.csv"
    with open(out, "w") as f:
        f.write("employee_id,date,task_id,project_id,hours,velocity,quality,on_time,impact\n")
        start, end = dt.date(2005,1,1), dt.date(2014,12,31)
        day = start
        rng = np.random.default_rng(1234)
        while day <= end:
            for eid in range(1, N_EMP+1):
                for t in range(10):
                    f.write(f"{eid},{day},{t+1},P{(eid%50)+1},{rng.uniform(0.3,1.2):.2f},{rng.integers(0,3)},{rng.uniform(0.6,1.0):.2f},{rng.integers(0,2)},{rng.integers(0,6)}\n")
            day += dt.timedelta(days=1)
    print("Wrote", out)
print("✅ Data generated.")
