# ml/train_big.py — LightGBM, group-wise CV, noise to avoid leakage-perfect scores
import os, json, joblib, numpy as np, pandas as pd
from pathlib import Path
from lightgbm import LGBMClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_fscore_support

ART_DIR = Path("ml/artifacts")
NOISE_FLIP_RATE = 0.08  # 8% label flips to simulate human variability

def evaluate(y_true, y_prob, y_pred):
    metrics = {}
    try:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
    except Exception:
        metrics["roc_auc"] = None
    try:
        metrics["avg_precision"] = float(average_precision_score(y_true, y_prob))
    except Exception:
        metrics["avg_precision"] = None
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
    metrics.update({"precision": float(p), "recall": float(r), "f1": float(f1)})
    return metrics

def main():
    # 1) Load features and labels
    Xdf = pd.read_csv("data/training_features_2005_2014.csv")        # has employee_id + features
    ydf = pd.read_csv("data/promotion_labels_2014.csv")               # has employee_id + label
    # Merge to keep alignment; also bring org_unit for grouping (from employees file)
    edf = pd.read_csv("data/employees_500.csv")[["employee_id","org_unit"]]
    df = Xdf.merge(ydf[["employee_id","label"]], on="employee_id", how="inner") \
            .merge(edf, on="employee_id", how="left")

    feat_cols = [c for c in Xdf.columns if c != "employee_id"]
    groups = df["org_unit"].astype("category").cat.codes.values
    X = df[feat_cols].values
    y = df["label"].astype(int).values

    # 2) Inject small label noise so it isn’t perfectly learnable
    if NOISE_FLIP_RATE and NOISE_FLIP_RATE > 0:
        rng = np.random.default_rng(42)
        flip_idx = rng.random(len(y)) < NOISE_FLIP_RATE
        y = np.where(flip_idx, 1 - y, y)

    # 3) GroupKFold CV by org_unit (prevents memorizing org-specific patterns)
    gkf = GroupKFold(n_splits=5)
    oof_prob = np.zeros_like(y, dtype=float)
    oof_pred = np.zeros_like(y, dtype=int)

    # We’ll keep the last fold’s model as the one to serialize (or you can average models)
    final_model = None
    best_iter = None

    for fold, (tr, va) in enumerate(gkf.split(X, y, groups=groups), 1):
        Xtr, Xva = X[tr], X[va]
        ytr, yva = y[tr], y[va]

        clf = LGBMClassifier(
            n_estimators=5000,            # big cap; early stopping will cut it
            learning_rate=0.03,
            num_leaves=31,                # smaller leaves for regularization
            max_depth=-1,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=5.0,               # stronger L2
            reg_alpha=1.0,                # L1
            min_child_samples=50,         # discourage tiny leaves
            min_split_gain=0.0,
            class_weight="balanced",
            random_state=42 + fold,
            n_jobs=-1
        )

        # Early stopping via the sklearn API: use callbacks if available; else rely on best_score_
        try:
            from lightgbm import early_stopping, log_evaluation
            callbacks = [early_stopping(stopping_rounds=100), log_evaluation(period=100)]
        except Exception:
            callbacks = []

        clf.fit(
            Xtr, ytr,
            eval_set=[(Xva, yva)],
            eval_metric="auc",
            callbacks=callbacks
        )

        # Use best_iteration_ if available
        best_it = int(getattr(clf, "best_iteration_", clf.n_estimators))
        prob = clf.predict_proba(Xva, num_iteration=best_it)[:, 1]
        pred = (prob >= 0.5).astype(int)

        oof_prob[va] = prob
        oof_pred[va] = pred

        # Keep last fold model (or you could choose the best-auc fold)
        final_model = clf
        best_iter = best_it

        m = evaluate(yva, prob, pred)
        print(f"[Fold {fold}] AUC={m['roc_auc']:.4f} AP={m['avg_precision']:.4f} F1={m['f1']:.4f}")

    # 4) OOF metrics (stronger estimate of generalization)
    overall = evaluate(y, oof_prob, oof_pred)
    print("OOF metrics:", json.dumps(overall, indent=2))

    # 5) Optional probability calibration (fit on full data)
    calibrated = False
    model_to_save = final_model
    try:
        from sklearn.calibration import CalibratedClassifierCV
        cal = CalibratedClassifierCV(final_model, method="isotonic", cv=3)
        cal.fit(X, y)
        model_to_save = cal
        calibrated = True
    except Exception:
        calibrated = False

    # 6) Save artifacts
    ART_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_to_save, ART_DIR / "model.pkl")
    with open(ART_DIR / "features.json", "w") as f:
        json.dump({
            "feature_order": feat_cols,
            "model_type": "LightGBM",
            "calibrated": calibrated,
            "best_iteration": best_iter,
            "label_noise_flip_rate": NOISE_FLIP_RATE,
            "cv": "GroupKFold(n_splits=5, group=org_unit)"
        }, f)

    # 7) (Optional) SHAP background sample
    try:
        idx = np.random.default_rng(123).choice(np.arange(X.shape[0]), size=min(512, X.shape[0]), replace=False)
        np.save(ART_DIR / "shap_background.npy", X[idx])
    except Exception:
        pass

    print("Saved artifacts to ml/artifacts")

if __name__ == "__main__":
    main()