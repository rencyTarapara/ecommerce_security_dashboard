import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Load data
df = pd.read_csv("centralized_behavior_fraud_security_dataset.csv")

features = [
    'failed_login_attempts', 'geo_location_mismatch', 'timezone_mismatch',
    'multiple_sessions_same_ip', 'account_takeover_risk', 'sudden_ip_change',
    'captcha_triggered'
]
X = df[features]
y = df["is_security_threat"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, "security_model.pkl")
joblib.dump(scaler, "security_scaler.pkl")
