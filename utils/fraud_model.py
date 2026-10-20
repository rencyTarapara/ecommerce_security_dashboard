import joblib
import pandas as pd
from pathlib import Path
from functools import lru_cache

# Resolve paths relative to project root (parent of utils/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MODEL_PATH = str(_PROJECT_ROOT / "model" / "fraud_model.pkl")
_SCALER_PATH = str(_PROJECT_ROOT / "model" / "fraud_scaler.pkl")


@lru_cache(maxsize=1)
def _load_model():
    """Load fraud model and scaler (cached after first call)."""
    model = joblib.load(_MODEL_PATH)
    scaler = joblib.load(_SCALER_PATH)
    return model, scaler


def predict_fraud(features_df: pd.DataFrame):
    """
    Predict fraud likelihood for each row in the features dataframe.
    Expected columns: ['purchase_amount', 'num_items', 'account_age_days', 'session_duration']
    """
    expected_cols = ["purchase_amount", "num_items", "account_age_days", "session_duration"]
    if not all(col in features_df.columns for col in expected_cols):
        raise ValueError(f"Input DataFrame must contain these columns: {expected_cols}")

    model, scaler = _load_model()
    X_scaled = scaler.transform(features_df[expected_cols])
    predictions = model.predict(X_scaled)
    return predictions
