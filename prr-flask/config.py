import os
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///prr.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_DIR = os.getenv("MODEL_DIR", "ml/artifacts")
    PROMOTE_THRESH = float(os.getenv("PROMOTE_THRESH", 0.72))
    BORDERLINE_LOW = float(os.getenv("BORDERLINE_LOW", 0.60))
    SECRET_KEY = os.getenv("SECRET_KEY","dev_secret_key_change_me")
    LOG_LEVEL = os.getenv("LOG_LEVEL","DEBUG")
