from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
def init_db(app):
    db.init_app(app)
    with app.app_context():
        from prr.models.employee import Employee
        from prr.models.okr import OKR
        from prr.models.project_activity import ProjectActivity
        from prr.models.feedback360 import Feedback360
        from prr.models.manager_review import ManagerReview
        from prr.models.learning import LearningHistory
        from prr.models.incidents import Incident
        from prr.models.recognition import Recognition
        from prr.models.competency import CompetencyFramework
        from prr.models.catalog import Catalog
        db.create_all()
