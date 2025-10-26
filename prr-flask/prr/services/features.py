from sqlalchemy import text
from prr.utils.db import db
def build_features(employee_id: int, as_of: str) -> dict:
    proj = db.session.execute(text("""SELECT AVG(on_time) on_time_ratio, AVG(quality_score) qmean,
                                    SUM(velocity) vtot, SUM(customer_impact) itot
                                    FROM project_activity WHERE employee_id=:eid"""), {"eid": employee_id}).mappings().first()
    fb = db.session.execute(text("SELECT AVG(rating) fbmean FROM feedback360 WHERE employee_id=:eid"), {"eid": employee_id}).mappings().first()
    rec = db.session.execute(text("SELECT COUNT(*) rcount FROM recognition WHERE employee_id=:eid"), {"eid": employee_id}).mappings().first()
    inc = db.session.execute(text("SELECT SUM(CASE severity WHEN 'Low' THEN 1 WHEN 'Medium' THEN 2 WHEN 'High' THEN 4 END) iw FROM incidents WHERE employee_id=:eid"), {"eid": employee_id}).mappings().first()
    lrn = db.session.execute(text("SELECT SUM(CASE WHEN completion THEN 1 ELSE 0 END) AS courses_completed FROM learning_history WHERE employee_id=:eid"), {"eid": employee_id}).mappings().first()
    return {
        "okr_attainment": 0.95,
        "on_time_ratio": (proj["on_time_ratio"] or 0.9) if proj else 0.9,
        "quality_mean": (proj["qmean"] or 0.85) if proj else 0.85,
        "velocity_total": (proj["vtot"] or 0) if proj else 0,
        "impact_total": (proj["itot"] or 0) if proj else 0,
        "feedback_mean": (fb["fbmean"] or 4.1) if fb else 4.1,
        "recognitions": (rec["rcount"] or 0) if rec else 0,
        "incidents_weight": (inc["iw"] or 0) if inc else 0,
        "courses_completed": (lrn["courses_completed"] or 0) if lrn else 0
    }
