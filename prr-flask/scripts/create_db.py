import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import create_app
from prr.utils.db import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized.')
