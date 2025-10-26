from flask import Blueprint, request, jsonify
from sqlalchemy import text
from prr.utils.db import db
from prr.services.features import build_features
from prr.services.model import ModelService
from prr.services.recommender import infer_gaps, recommend_courses, mentor_suggestion
bp = Blueprint("plan", __name__)
@bp.route('/recommend', methods=['POST'])
def plan():
    data = request.get_json(force=True)
    eid = int(data['employee_id'])
    as_of = data.get('as_of','2014-12-31')
    feats = build_features(eid, as_of)
    emp = db.session.execute(text("SELECT org_unit FROM employee WHERE id=:eid"), {"eid": eid}).mappings().first()
    org = emp['org_unit'] if emp else ''
    score = ModelService.score(feats)
    gaps = infer_gaps(feats, org)
    courses = recommend_courses(gaps)
    plan = {
        "milestones": [{"day":30,"goal":"Lead a cross-functional meeting"},
                       {"day":60,"goal":"Run a postmortem & publish actions"},
                       {"day":90,"goal":"Deliver an approved design/plan"}],
        "items": [{"type":"course", **c} for c in courses] + [{"type":"mentor", **mentor_suggestion(org)}],
        "expected_readiness_gain": 0.08
    }
    return jsonify({"employee_id": eid,"readiness_score": round(score,3),"gaps": gaps, "plan": plan})
