from flask import Blueprint, request, jsonify
import numpy as np
from prr.services.features import build_features
from prr.services.model import ModelService
bp = Blueprint("explain", __name__)
@bp.route('/local', methods=['GET'])
def local():
    eid = int(request.args['employee_id'])
    as_of = request.args.get('as_of','2014-12-31')
    feats = build_features(eid, as_of)
    ModelService.load()
    order = ModelService._feat_order
    x = np.array([[feats.get(k,0) for k in order]])
    top = sorted([{"feature":k, "value":float(v)} for k,v in zip(order, x[0])],
                 key=lambda t: abs(t['value']), reverse=True)[:5]
    return jsonify({"employee_id": eid, "top_factors": top})
