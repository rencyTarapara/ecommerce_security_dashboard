import streamlit as st
import pandas as pd
import joblib
from utils.fraud_model import predict_fraud  # ✅ Optional, if used
import os

# ----------------------------
# 🔐 Role-Based Access Control
# ----------------------------
st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("🛠️ Admin Dashboard")

if not st.session_state.get("logged_in"):
    st.warning("🔒 You must be logged in.")
    st.stop()

if st.session_state.get("role") != "admin":
    st.error("⛔ Access denied. This page is for admins only.")
    st.stop()

st.success(f"✅ Welcome, Admin: {st.session_state.get('username')}")


# ----------------------------
# 🧠 Load Models & Scalers
# ----------------------------
try:
    fraud_model = joblib.load("model/fraud_model.pkl")
    fraud_scaler = joblib.load("model/fraud_scaler.pkl")

    security_model = joblib.load("model/security_model.pkl")
    security_scaler = joblib.load("model/security_scaler.pkl")

    behavior_model = joblib.load("model/behavior_model.pkl")
    behavior_scaler = joblib.load("model/behavior_scaler.pkl")

    bot_model = joblib.load("model/bot_model.pkl")
    bot_scaler = joblib.load("model/bot_scaler.pkl")
except Exception as e:
    st.error(f"🚫 Model loading error: {e}")
    st.stop()


# ----------------------------
# 📤 Upload CSV for Prediction
# ----------------------------
st.subheader("🔍 Upload Session/Transaction Data")
uploaded_file = st.file_uploader("Upload CSV containing session and transaction data", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("📋 Uploaded Data Sample:")
        st.dataframe(df.head())

        if st.button("🧠 Run All Predictions"):
            with st.spinner("Running multi-model analysis..."):

                # --- Fraud Detection ---
                fraud_features = ['purchase_amount', 'num_items', 'account_age_days', 'session_duration']
                fraud_X = fraud_scaler.transform(df[fraud_features])
                df["is_fraud_predicted"] = fraud_model.predict(fraud_X)

                # --- Security Alert Detection ---
                security_features = [
                    'failed_login_attempts', 'geo_location_mismatch', 'timezone_mismatch',
                    'multiple_sessions_same_ip', 'account_takeover_risk', 'sudden_ip_change', 'captcha_triggered'
                ]
                security_X = security_scaler.transform(df[security_features])
                df["is_security_threat_predicted"] = security_model.predict(security_X)

                # --- Behavior Detection ---
                behavior_features = [
                    'typing_time', 'paste_detected', 'mouse_moves_per_second', 'scroll_depth',
                    'total_time_on_page', 'keystroke_variance', 'click_count', 'mouse_click_rate',
                    'idle_time_ratio', 'hover_time', 'scroll_velocity'
                ]
                behavior_X = behavior_scaler.transform(df[behavior_features])
                df["is_behavior_anomalous"] = behavior_model.predict(behavior_X)

                # --- Bot Detection ---
                bot_features = [
                    'user_agent_contains_bot', 'navigator_webdriver', 'js_enabled', 'cookie_enabled',
                    'typing_time', 'paste_detected', 'mouse_moves_per_second'
                ]
                bot_X = bot_scaler.transform(df[bot_features])
                df["is_bot_predicted"] = bot_model.predict(bot_X)

                st.success("✅ All Predictions Complete!")

                # ----------------------------
                # 📊 Results Section
                # ----------------------------
                st.subheader("📊 Fraud Predictions")
                st.dataframe(df[['username', 'purchase_amount', 'is_fraud_predicted']])

                st.subheader("🔐 Security Alerts")
                st.dataframe(df[['username', 'failed_login_attempts', 'geo_location_mismatch', 'is_security_threat_predicted']])

                st.subheader("🧠 Behavior Overview")
                st.dataframe(df[['username', 'typing_time', 'click_count', 'is_behavior_anomalous']])

                st.subheader("🤖 Bot Detection Overview")
                st.dataframe(df[['username', 'user_agent_contains_bot', 'navigator_webdriver', 'is_bot_predicted']])

                # 📥 CSV Download
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇ Download Full Prediction CSV", csv, "prediction_results.csv", "text/csv")

                # ----------------------------
                # 📡 Real-Time Session Monitoring
                # ----------------------------
                st.subheader("📡 Real-Time User Sessions")
                try:
                    live_df = pd.read_csv("data/live_predictions.csv")
                    st.dataframe(live_df.sort_values("timestamp", ascending=False))
                    st.line_chart(live_df[["is_bot_predicted", "is_behavior_anomalous"]].rolling(5).mean())
                except FileNotFoundError:
                    st.info("⏳ No live predictions yet. Waiting for user activity...")

                # ----------------------------
                # 📈 Daily Reports (Anomaly Summary)
                # ----------------------------
                st.subheader("📈 Daily Anomaly Summary")
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df['date'] = df['timestamp'].dt.date

                    daily_summary = df.groupby("date").agg({
                        "is_fraud_predicted": "sum",
                        "is_security_threat_predicted": "sum",
                        "is_bot_predicted": "sum",
                        "is_behavior_anomalous": "sum"
                    }).reset_index()

                    st.dataframe(daily_summary)
                    st.area_chart(daily_summary.set_index("date"))

                except Exception as e:
                    st.warning(f"Report error: {e}")
    except Exception as e:
        st.error(f"⚠️ Error while processing uploaded file: {e}")
