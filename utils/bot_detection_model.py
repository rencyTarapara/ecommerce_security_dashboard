import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Load data
df = pd.read_csv("centralized_behavior_fraud_security_dataset.csv")

features = [
    'user_agent_contains_bot', 'navigator_webdriver', 'js_enabled', 'cookie_enabled',
    'typing_time', 'paste_detected', 'mouse_moves_per_second'
]
X = df[features]
y = df["is_bot"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, "bot_model.pkl")
joblib.dump(scaler, "bot_scaler.pkl")
