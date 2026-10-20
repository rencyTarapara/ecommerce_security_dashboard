import streamlit as st
import pandas as pd
import joblib
import os
from pathlib import Path
from utils.fraud_model import predict_fraud

# Resolve model paths relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ----------------------------
# 🔐 Role-Based Access Control
# ----------------------------
st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("🛠️ Admin Dashboard")

if not st.session_state.get("logged_in"):
    st.warning("🔒 You must be logged in to access this page.")
    st.stop()

if st.session_state.get("role") != "admin":
    st.error("⛔ Access denied. This page is for admins only.")
    st.stop()

st.success(f"✅ Welcome, Admin: {st.session_state.get('username')}")


# ----------------------------
# 🧠 Load Models & Scalers (cached)
# ----------------------------
@st.cache_resource
def load_admin_models():
    fraud_model = joblib.load(str(_PROJECT_ROOT / "model" / "fraud_model.pkl"))
    fraud_scaler = joblib.load(str(_PROJECT_ROOT / "model" / "fraud_scaler.pkl"))
    security_model = joblib.load(str(_PROJECT_ROOT / "model" / "security_model.pkl"))
    security_scaler = joblib.load(str(_PROJECT_ROOT / "model" / "security_scaler.pkl"))
    behavior_model = joblib.load(str(_PROJECT_ROOT / "model" / "behavior_model.pkl"))
    behavior_scaler = joblib.load(str(_PROJECT_ROOT / "model" / "behavior_scaler.pkl"))
    bot_model = joblib.load(str(_PROJECT_ROOT / "model" / "bot_model.pkl"))
    bot_scaler = joblib.load(str(_PROJECT_ROOT / "model" / "bot_scaler.pkl"))
    return (
        fraud_model, fraud_scaler,
        security_model, security_scaler,
        behavior_model, behavior_scaler,
        bot_model, bot_scaler,
    )

try:
    (
        fraud_model, fraud_scaler,
        security_model, security_scaler,
        behavior_model, behavior_scaler,
        bot_model, bot_scaler,
    ) = load_admin_models()
except Exception as e:
    st.error(f"🚫 Model loading error: {e}")
    st.stop()


# ----------------------------
# 📡 Real-Time Session Monitoring
# ----------------------------
st.subheader("📡 Real-Time User Sessions")
live_file = str(_PROJECT_ROOT / "data" / "live_predictions.csv")
try:
    live_df = pd.read_csv(live_file)
    st.dataframe(live_df.sort_values("timestamp", ascending=False))
    if len(live_df) >= 2:
        st.line_chart(live_df[["is_bot_predicted", "is_behavior_anomalous"]].rolling(5).mean())
except FileNotFoundError:
    st.info("⏳ No live predictions yet. Waiting for user activity...")


# ----------------------------
# 📤 Upload CSV for Prediction
# ----------------------------
st.subheader("🔍 Upload Session/Transaction Data for Analysis")
uploaded_file = st.file_uploader(
    "Upload CSV containing session and transaction data", type="csv"
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("📋 Uploaded Data Sample:")
        st.dataframe(df.head())

        if st.button("🧠 Run All Predictions"):
            with st.spinner("Running multi-model analysis..."):

                # --- Fraud Detection ---
                fraud_features = ["purchase_amount", "num_items", "account_age_days", "session_duration"]
                missing_fraud = [c for c in fraud_features if c not in df.columns]
                if missing_fraud:
                    st.error(f"Missing fraud features in CSV: {missing_fraud}")
                else:
                    fraud_X = fraud_scaler.transform(df[fraud_features])
                    df["is_fraud_predicted"] = fraud_model.predict(fraud_X)

                # --- Security Alert Detection ---
                security_features = [
                    "failed_login_attempts", "geo_location_mismatch", "timezone_mismatch",
                    "multiple_sessions_same_ip", "account_takeover_risk", "sudden_ip_change",
                    "captcha_triggered",
                ]
                missing_sec = [c for c in security_features if c not in df.columns]
                if missing_sec:
                    st.error(f"Missing security features in CSV: {missing_sec}")
                else:
                    security_X = security_scaler.transform(df[security_features])
                    df["is_security_threat_predicted"] = security_model.predict(security_X)

                # --- Behavior Detection ---
                behavior_features = [
                    "typing_time", "paste_detected", "mouse_moves_per_second", "scroll_depth",
                    "total_time_on_page", "keystroke_variance", "click_count", "mouse_click_rate",
                    "idle_time_ratio", "hover_time", "scroll_velocity",
                ]
                missing_beh = [c for c in behavior_features if c not in df.columns]
                if missing_beh:
                    st.error(f"Missing behavior features in CSV: {missing_beh}")
                else:
                    behavior_X = behavior_scaler.transform(df[behavior_features])
                    df["is_behavior_anomalous"] = behavior_model.predict(behavior_X)

                # --- Bot Detection ---
                bot_features = [
                    "user_agent_contains_bot", "navigator_webdriver", "js_enabled", "cookie_enabled",
                    "typing_time", "paste_detected", "mouse_moves_per_second",
                ]
                missing_bot = [c for c in bot_features if c not in df.columns]
                if missing_bot:
                    st.error(f"Missing bot features in CSV: {missing_bot}")
                else:
                    bot_X = bot_scaler.transform(df[bot_features])
                    df["is_bot_predicted"] = bot_model.predict(bot_X)

                st.success("✅ All Predictions Complete!")

                # ----------------------------
                # 📊 Results Section
                # ----------------------------
                if "is_fraud_predicted" in df.columns:
                    st.subheader("📊 Fraud Predictions")
                    cols_to_show = [c for c in ["username", "purchase_amount", "is_fraud_predicted"] if c in df.columns]
                    st.dataframe(df[cols_to_show])

                if "is_security_threat_predicted" in df.columns:
                    st.subheader("🔐 Security Alerts")
                    cols_to_show = [c for c in ["username", "failed_login_attempts", "geo_location_mismatch", "is_security_threat_predicted"] if c in df.columns]
                    st.dataframe(df[cols_to_show])

                if "is_behavior_anomalous" in df.columns:
                    st.subheader("🧠 Behavior Overview")
                    cols_to_show = [c for c in ["username", "typing_time", "click_count", "is_behavior_anomalous"] if c in df.columns]
                    st.dataframe(df[cols_to_show])

                if "is_bot_predicted" in df.columns:
                    st.subheader("🤖 Bot Detection Overview")
                    cols_to_show = [c for c in ["username", "user_agent_contains_bot", "navigator_webdriver", "is_bot_predicted"] if c in df.columns]
                    st.dataframe(df[cols_to_show])

                # 📥 CSV Download
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇ Download Full Prediction CSV",
                    csv,
                    "prediction_results.csv",
                    "text/csv",
                )

                # ----------------------------
                # 📈 Daily Reports (Anomaly Summary)
                # ----------------------------
                st.subheader("📈 Daily Anomaly Summary")
                try:
                    if "timestamp" in df.columns:
                        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                        df["date"] = df["timestamp"].dt.date

                        agg_cols = {
                            c: "sum"
                            for c in ["is_fraud_predicted", "is_security_threat_predicted", "is_bot_predicted", "is_behavior_anomalous"]
                            if c in df.columns
                        }
                        if agg_cols:
                            daily_summary = df.groupby("date").agg(agg_cols).reset_index()
                            st.dataframe(daily_summary)
                            st.area_chart(daily_summary.set_index("date"))
                    else:
                        st.info("No 'timestamp' column found in the uploaded CSV.")
                except Exception as e:
                    st.warning(f"Report error: {e}")

    except Exception as e:
        st.error(f"⚠️ Error while processing uploaded file: {e}")
