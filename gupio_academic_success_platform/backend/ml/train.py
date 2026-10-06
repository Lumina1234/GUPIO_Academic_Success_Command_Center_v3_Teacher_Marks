import json
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from ml.feature_policy import CATEGORICAL_COLUMNS, PROHIBITED_SEMESTER_COLUMNS, TARGET_COLUMN

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT.parent / "data" / "data.csv"
MODEL_DIR = ROOT / "models"
OUTPUT_DIR = ROOT / "outputs"
MODEL_PATH = MODEL_DIR / "student_outcome_pipeline.joblib"


def normalise_headers(df):
    df = df.copy()
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    return df


def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing panel-supplied dataset: {DATA_PATH}")
    return normalise_headers(pd.read_csv(DATA_PATH, sep=";"))


def build_preprocessor(columns):
    categorical = [c for c in CATEGORICAL_COLUMNS if c in columns]
    numeric = [c for c in columns if c not in categorical]
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    return ColumnTransformer([
        ("cat", cat_pipe, categorical),
        ("num", num_pipe, numeric),
    ])


def main():
    df = load_dataset()
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Expected target column '{TARGET_COLUMN}', found {list(df.columns)}")

    missing = sorted(set(PROHIBITED_SEMESTER_COLUMNS).intersection(df.columns))
    for col in missing:
        df = df.drop(columns=[col])

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    preprocess = build_preprocessor(X_train.columns)
    models = {
        "logistic_regression": Pipeline([
            ("preprocess", preprocess),
            ("model", LogisticRegression(max_iter=2500, class_weight="balanced", random_state=42)),
        ]),
        "random_forest": Pipeline([
            ("preprocess", build_preprocessor(X_train.columns)),
            ("model", RandomForestClassifier(
                n_estimators=400,
                random_state=42,
                class_weight="balanced_subsample",
                min_samples_leaf=2,
                n_jobs=-1,
            )),
        ]),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = {}
    for name, pipeline in models.items():
        scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=1)
        cv_scores[name] = {
            "macro_f1_mean": float(scores.mean()),
            "macro_f1_std": float(scores.std()),
            "folds": [float(s) for s in scores],
        }

    selected_name = max(cv_scores, key=lambda key: cv_scores[key]["macro_f1_mean"])
    selected = models[selected_name]
    selected.fit(X_train, y_train)
    y_pred = selected.predict(X_test)

    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    precision, recall, f1, support = precision_recall_fscore_support(y_test, y_pred, labels=sorted(y.unique()), zero_division=0)

    evaluation = {
        "dataset_rows": int(len(df)),
        "dataset_columns_after_leakage_exclusion": int(df.shape[1]),
        "target_distribution": y.value_counts().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_values_total": int(df.isna().sum().sum()),
        "prohibited_columns_removed": missing,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "candidate_models": cv_scores,
        "selected_model": selected_name,
        "test_accuracy": float(accuracy_score(y_test, y_pred)),
        "test_macro_f1": float(report["macro avg"]["f1-score"]),
        "classification_report": report,
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=sorted(y.unique())).tolist(),
        "classes": sorted(y.unique()),
        "per_class": {
            label: {
                "precision": float(p),
                "recall": float(r),
                "f1": float(f),
                "support": int(s),
            }
            for label, p, r, f, s in zip(sorted(y.unique()), precision, recall, f1, support)
        },
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": selected, "feature_names": list(X.columns), "classes": sorted(y.unique()), "model_name": selected_name}, MODEL_PATH)
    (OUTPUT_DIR / "evaluation.json").write_text(json.dumps(evaluation, indent=2))

    # Actual transformed feature importance; never interpreted as causation.
    importance = []
    model = selected.named_steps["model"]
    transformer = selected.named_steps["preprocess"]
    try:
        names = transformer.get_feature_names_out()
        if hasattr(model, "feature_importances_"):
            vals = np.asarray(model.feature_importances_)
        else:
            vals = np.mean(np.abs(np.asarray(model.coef_)), axis=0)
        top = np.argsort(vals)[::-1][:15]
        importance = [{"feature": str(names[i]), "importance": float(vals[i])} for i in top]
    except Exception as exc:
        importance = [{"feature": "unavailable", "importance": 0.0, "note": str(exc)}]
    (OUTPUT_DIR / "feature_importance.json").write_text(json.dumps(importance, indent=2))

    print(json.dumps({"selected_model": selected_name, "test_accuracy": evaluation["test_accuracy"], "test_macro_f1": evaluation["test_macro_f1"]}, indent=2))


if __name__ == "__main__":
    main()
