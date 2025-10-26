from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv            # <-- add this
from config import Config
from prr.utils.db import init_db
from prr.routes.promotion import bp as promotion_bp
from prr.routes.plan import bp as plan_bp
from prr.routes.explain import bp as explain_bp
from prr.routes.fairness import bp as fairness_bp
from prr.routes.ingest import bp as ingest_bp

def create_app():
    load_dotenv()                         # <-- add this line
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    init_db(app)
    app.register_blueprint(promotion_bp, url_prefix="/v1/promotion")
    app.register_blueprint(plan_bp, url_prefix="/v1/plan")
    app.register_blueprint(explain_bp, url_prefix="/v1/explain")
    app.register_blueprint(fairness_bp, url_prefix="/v1/fairness")
    app.register_blueprint(ingest_bp, url_prefix="/v1/ingest")

    @app.route("/")
    def root():
        return jsonify({
            "app": "PRR Flask API",
            "status": "ok",
            "endpoints": [
                "GET  /v1/ingest/health",
                "POST /v1/promotion/score",
                "POST /v1/plan/recommend",
                "GET  /v1/explain/local?employee_id=1",
                "GET  /v1/fairness/summary"
            ]
        })

    @app.route("/favicon.ico")
    def favicon():
        return ("", 204)

    @app.route("/dashboard")
    def dashboard():
        return send_from_directory("templates", "index.html")

    return app

app = create_app()
