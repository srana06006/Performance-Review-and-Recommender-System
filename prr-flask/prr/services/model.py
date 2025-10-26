import os, json, joblib, numpy as np
from config import Config
class ModelService:
    _model = None
    _feat_order = None
    @classmethod
    def load(cls, model_dir=None):
        if cls._model: return
        md = model_dir or Config.MODEL_DIR
        cls._model = joblib.load(os.path.join(md, "model.pkl"))
        with open(os.path.join(md, "features.json")) as f:
            cls._feat_order = json.load(f)["feature_order"]
    @classmethod
    def score(cls, features: dict) -> float:
        cls.load()
        x = np.array([[features.get(k,0) for k in cls._feat_order]])
        if hasattr(cls._model, "predict_proba"):
            return float(cls._model.predict_proba(x)[0,1])
        p = cls._model.predict(x)
        try: return float(p[0])
        except Exception: return float(p)
