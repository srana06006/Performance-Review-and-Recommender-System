from flask import Blueprint, jsonify
bp = Blueprint('ingest', __name__)
@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status':'ok'})
