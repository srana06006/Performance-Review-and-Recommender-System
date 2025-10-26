from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import text
from prr.utils.db import db
from prr.services.features import build_features
from prr.services.model import ModelService
bp = Blueprint("promotion", __name__)
def decide(score, promote_thresh, borderline_low):
    if score >= promote_thresh: return "PROMOTE"
    if score >= borderline_low: return "BORDERLINE"
    return "HOLD"
@bp.route('/score', methods=['POST'])
def score():
    data = request.get_json(force=True)
    eid = int(data['employee_id'])
    as_of = data.get('as_of','2014-12-31')
    feats = build_features(eid, as_of)
    p = ModelService.score(feats)
    emp = db.session.execute(text("SELECT name FROM employee WHERE id=:eid"), {"eid":eid}).mappings().first()
    decision = decide(p, current_app.config['PROMOTE_THRESH'], current_app.config['BORDERLINE_LOW'])
    confidence = round(0.8 + min(0.16, abs(p-0.5)), 2)
    return jsonify({"employee_id": eid, "employee": emp["name"] if emp else None, "as_of": as_of, "readiness_score": round(p,3), "decision": decision, "confidence": confidence})
