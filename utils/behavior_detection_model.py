import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Load data
df = pd.read_csv("centralized_behavior_fraud_security_dataset.csv")

# Features for behavior detection
features = [
    'typing_time', 'paste_detected', 'mouse_moves_per_second', 'scroll_depth',
    'total_time_on_page', 'keystroke_variance', 'click_count', 'mouse_click_rate',
    'idle_time_ratio', 'hover_time', 'scroll_velocity'
]
X = df[features]
y = df["is_bot"]

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model and scaler
joblib.dump(model, "behavior_model.pkl")
joblib.dump(scaler, "behavior_scaler.pkl")
