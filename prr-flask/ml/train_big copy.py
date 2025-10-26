# Big trainer
import os, json, joblib, numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
def main():
    df = pd.read_csv('data/training_features_2005_2014.csv')
    feat_cols = [c for c in df.columns if c!='employee_id']
    comp = (0.22*df['okr_attainment'] + 0.18*(df['feedback_mean']/5.0) +
            0.12*df['recognitions'] + 0.12*df['courses_completed'] +
            0.12*df['on_time_ratio'] + 0.12*df['quality_mean'] +
            0.07*df['velocity_total'] + 0.05*df['impact_total'] -
            0.12*(df['incidents_weight']>0).astype(int))
    y = (comp >= comp.quantile(0.8)).astype(int)
    X = df[feat_cols].values
    base = LogisticRegression(max_iter=2000, class_weight='balanced')
    base.fit(X, y)
    try:
        model = CalibratedClassifierCV(base, method='isotonic', cv=3).fit(X, y)
        calibrated = True
    except Exception:
        model = base
        calibrated = False
    os.makedirs('ml/artifacts', exist_ok=True)
    joblib.dump(model, 'ml/artifacts/model.pkl')
    json.dump({"feature_order": feat_cols, "model_type":"LogisticRegression", "calibrated": calibrated}, open('ml/artifacts/features.json','w'))
    print("Saved artifacts to ml/artifacts")
if __name__ == "__main__":
    main()
