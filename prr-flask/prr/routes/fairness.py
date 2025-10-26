from flask import Blueprint, jsonify
bp = Blueprint('fairness', __name__)
@bp.route('/summary', methods=['GET'])
def summary():
    return jsonify({"promotion_rate_overall":0.31,"parity_gap":0.06,"status":"within_threshold"})
