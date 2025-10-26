# Seeds employee table from data/employees_500.csv
import sqlite3, pandas as pd
conn = sqlite3.connect("prr.db")
emp = pd.read_csv("data/employees_500.csv")
emp_out = emp.rename(columns={"employee_id":"id"})
emp_out["manager_id"] = None
emp_out["location"] = "HQ"
emp_out["employment_type"] = "Full-Time"
cols = ["id","name","org_unit","manager_id","current_rank","last_promotion_date","location","employment_type"]
emp_out[cols].to_sql("employee", conn, if_exists="append", index=False)
conn.close()
print("Seeded employees.")
