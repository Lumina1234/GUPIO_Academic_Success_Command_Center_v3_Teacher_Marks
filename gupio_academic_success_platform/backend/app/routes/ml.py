from pathlib import Path
import json
import joblib
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Request
from app.config import get_settings
from app.dependencies import current_user
from app.schemas import PredictionRequest
from app.security import audit, verify_csrf

router = APIRouter(prefix="/api/v1/ml", tags=["ml"])
ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "student_outcome_pipeline.joblib"
OUTPUT_DIR = ROOT / "outputs"
settings = get_settings()


@router.get("/model-info")
def model_info():
    payload = {"trained": MODEL_PATH.exists(), "model_name": None, "classes": [], "features": []}
    if MODEL_PATH.exists():
        bundle = joblib.load(MODEL_PATH)
        payload.update({
            "model_name": bundle.get("model_name"),
            "classes": bundle.get("classes", []),
            "features": bundle.get("feature_names", []),
        })
        eval_path = OUTPUT_DIR / "evaluation.json"
        if eval_path.exists():
            evaluation = json.loads(eval_path.read_text())
            payload["evaluation"] = {
                "test_accuracy": evaluation.get("test_accuracy"),
                "test_macro_f1": evaluation.get("test_macro_f1"),
                "test_rows": evaluation.get("test_rows"),
            }
    return payload


@router.post("/predict")
def predict(payload: PredictionRequest, request: Request, user=Depends(current_user)):
    session = getattr(request.state, "db_session", None)
    if not session or not verify_csrf(session, request.headers.get("X-CSRF-Token")):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    if not MODEL_PATH.exists():
        raise HTTPException(status_code=503, detail="Model not trained. Place the panel-supplied data.csv in data/ and run `python -m ml.train`.")

    bundle = joblib.load(MODEL_PATH)
    expected = bundle["feature_names"]
    row = {col: payload.features.get(col) for col in expected}
    df = pd.DataFrame([row])
    pipeline = bundle["pipeline"]
    pred = pipeline.predict(df)[0]
    probabilities = pipeline.predict_proba(df)[0] if hasattr(pipeline, "predict_proba") else []
    classes = list(bundle.get("classes", []))
    probs = {str(c): round(float(p), 5) for c, p in zip(classes, probabilities)}

    audit_db = request.app.state.db_factory()
    try:
        audit(audit_db, user.id, "ml_prediction", request.client.host if request.client else None, json.dumps({"predicted": str(pred)}))
    finally:
        audit_db.close()

    return {
        "prediction": str(pred),
        "probabilities": probs,
        "features_received": sum(v is not None for v in row.values()),
        "features_total": len(row),
        "interpretation_note": "Feature importance expresses predictive association for the fitted model; it does not establish causation.",
    }
