# utils/fraud_model.py

import joblib
import pandas as pd

# Load model and scaler
model = joblib.load("model/fraud_model.pkl")
scaler = joblib.load("model/fraud_scaler.pkl")

def predict_fraud(features_df: pd.DataFrame):
    """
    Predict fraud likelihood for each row in the features dataframe.
    Expected columns: ['purchase_amount', 'num_items', 'account_age_days', 'session_duration']
    """
    # Basic check
    expected_cols = ['purchase_amount', 'num_items', 'account_age_days', 'session_duration']
    if not all(col in features_df.columns for col in expected_cols):
        raise ValueError(f"Input DataFrame must contain these columns: {expected_cols}")

    # Scale and predict
    X_scaled = scaler.transform(features_df[expected_cols])
    predictions = model.predict(X_scaled)
    return predictions
