from sqlalchemy import text
from prr.utils.db import db
def infer_gaps(features: dict, org_unit: str) -> list[str]:
    gaps = []
    if features.get("feedback_mean", 4.1) < 4.0: gaps.append("Leadership")
    if features.get("on_time_ratio", 0.9) < 0.8: gaps.append("Time Management")
    if features.get("quality_mean", 0.85) < 0.78: gaps.append("Attention to Detail")
    if "Software" in org_unit and features.get("velocity_total", 0) < 20000: gaps.append("System Design")
    return gaps[:3] or ["Leadership"]
def recommend_courses(gaps: list[str]) -> list[dict]:
    rows = db.session.execute(text("SELECT course_id,title,provider,duration_h,skills_json FROM catalog")).mappings().all()
    out = []
    for r in rows:
        for g in gaps:
            if g.lower().split()[0] in (r["title"].lower() + " " + r["skills_json"].lower()):
                out.append({"course_id": r["course_id"], "title": r["title"], "provider": r["provider"], "duration_h": r["duration_h"]})
                break
    return out[:3]
def mentor_suggestion(org_unit: str) -> dict:
    return {"name": "Mary Johnson", "role": "Senior PM" if "Software" in org_unit else "Senior Manager"}
