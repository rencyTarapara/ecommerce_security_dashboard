import streamlit as st
import pandas as pd
import datetime
import os
import smtplib
import joblib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.fraud_model import predict_fraud

# Resolve model paths relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ----------------------------
# 🔐 Role-Based Access Control
# ----------------------------
st.set_page_config(page_title="User Dashboard", layout="wide")
st.title("🛍️ User Dashboard")

if not st.session_state.get("logged_in"):
    st.warning("🔒 You must be logged in to access this page.")
    st.stop()

if st.session_state.get("role") != "user":
    st.error("⛔ Access denied. This page is for users only.")
    st.stop()

st.success(f"Welcome, {st.session_state.get('username')} 👋")

# ----------------------------
# 🧠 Load Models & Scalers (lazy, cached)
# ----------------------------
@st.cache_resource
def load_models():
    behavior_model = joblib.load(str(_PROJECT_ROOT / "model" / "behavior_model.pkl"))
    behavior_scaler = joblib.load(str(_PROJECT_ROOT / "model" / "behavior_scaler.pkl"))
    bot_model = joblib.load(str(_PROJECT_ROOT / "model" / "bot_model.pkl"))
    bot_scaler = joblib.load(str(_PROJECT_ROOT / "model" / "bot_scaler.pkl"))
    return behavior_model, behavior_scaler, bot_model, bot_scaler

try:
    behavior_model, behavior_scaler, bot_model, bot_scaler = load_models()
except Exception as e:
    st.error(f"🚫 Failed to load ML models: {e}")
    st.stop()

# ----------------------------
# 🛒 Shop Items
# ----------------------------
st.header("🏍️ Shop Items")

products = [
    {"name": "Wireless Headphones", "price": 1200},
    {"name": "Smartwatch", "price": 2499},
    {"name": "Bluetooth Speaker", "price": 999},
    {"name": "Phone Case", "price": 299},
    {"name": "Power Bank", "price": 699},
]

if "cart" not in st.session_state:
    st.session_state.cart = []

cols = st.columns(2)
for i, product in enumerate(products):
    with cols[i % 2]:
        st.subheader(product["name"])
        st.write(f"💰 Price: ₹{product['price']}")
        qty_key = f"qty_{product['name']}"
        quantity = st.number_input(
            f"Quantity for {product['name']}", 1, 10, 1, key=qty_key
        )
        if st.button(f"Add to Cart: {product['name']}", key=product["name"]):
            st.session_state.cart.append(
                {
                    "name": product["name"],
                    "price": product["price"],
                    "quantity": quantity,
                }
            )
            st.success(f"✅ Added {product['name']} to cart!")

# ----------------------------
# 🛒 Cart and Checkout
# ----------------------------
if st.session_state.cart:
    st.subheader("🛒 Your Cart")
    cart_df = pd.DataFrame(st.session_state.cart)
    cart_df["total"] = cart_df["price"] * cart_df["quantity"]
    st.dataframe(cart_df)

    total = cart_df["total"].sum()
    st.success(f"📿 Total: ₹{total}")

    payment_method = st.selectbox(
        "💳 Choose Payment Method",
        ["Credit Card", "Debit Card", "UPI", "Cash on Delivery"],
    )

    if st.button("✅ Place Order"):
        order_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save purchase data
        df_to_save = cart_df.copy()
        df_to_save["username"] = st.session_state.get("username")
        df_to_save["timestamp"] = order_time
        df_to_save["payment_method"] = payment_method

        file_path = str(_PROJECT_ROOT / "data" / "purchase_history.csv")
        file_exists = os.path.exists(file_path)
        df_to_save.to_csv(file_path, mode="a", index=False, header=not file_exists)

        # 📧 Send Confirmation Email
        user_email = st.session_state.get("email")
        if user_email:
            try:
                sender_email = st.secrets["EMAIL"]["sender"]
                app_password = st.secrets["EMAIL"]["app_password"]

                msg = MIMEMultipart("alternative")
                msg["Subject"] = "🛒 Order Confirmation"
                msg["From"] = sender_email
                msg["To"] = user_email
                text = (
                    f"Hi {st.session_state['username']},\n\n"
                    f"Your order of ₹{total} has been placed successfully on {order_time} "
                    f"using {payment_method}.\n\nThank you for shopping with us!"
                )
                msg.attach(MIMEText(text, "plain"))

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, app_password)
                    server.sendmail(sender_email, user_email, msg.as_string())

                st.success("📧 Confirmation email sent!")
            except KeyError:
                pass  # Email secrets not configured — silently skip
            except Exception as e:
                st.warning(f"Order placed, but email could not be sent: {e}")

        # 🔍 Rule-based anomaly detection
        item_counts = df_to_save["name"].value_counts()
        for item, count in item_counts.items():
            if count >= 5:
                st.warning(f"⚠️ Anomaly Detected: {count} units of '{item}' in one order.")

        # 🔐 ML-based behavior & bot analysis
        st.subheader("🧠 Behavior & Bot Detection Analysis")

        session_input = {
            "typing_time": 1.3,
            "paste_detected": 0,
            "mouse_moves_per_second": 4.5,
            "scroll_depth": 80,
            "total_time_on_page": 260,
            "keystroke_variance": 0.05,
            "click_count": 22,
            "mouse_click_rate": 0.085,
            "idle_time_ratio": 0.2,
            "hover_time": 35,
            "scroll_velocity": 6.7,
            "user_agent_contains_bot": 0,
            "navigator_webdriver": 0,
            "js_enabled": 1,
            "cookie_enabled": 1,
        }

        # Behavior detection
        behavior_X = behavior_scaler.transform([[
            session_input["typing_time"],
            session_input["paste_detected"],
            session_input["mouse_moves_per_second"],
            session_input["scroll_depth"],
            session_input["total_time_on_page"],
            session_input["keystroke_variance"],
            session_input["click_count"],
            session_input["mouse_click_rate"],
            session_input["idle_time_ratio"],
            session_input["hover_time"],
            session_input["scroll_velocity"],
        ]])
        behavior_pred = behavior_model.predict(behavior_X)[0]

        # Bot detection
        bot_X = bot_scaler.transform([[
            session_input["user_agent_contains_bot"],
            session_input["navigator_webdriver"],
            session_input["js_enabled"],
            session_input["cookie_enabled"],
            session_input["typing_time"],
            session_input["paste_detected"],
            session_input["mouse_moves_per_second"],
        ]])
        bot_pred = bot_model.predict(bot_X)[0]

        st.info(f"🧠 Behavior Detection: {'⚠️ Anomalous' if behavior_pred == 1 else '✅ Normal'}")
        st.info(f"🤖 Bot Detection: {'🚨 Detected as Bot' if bot_pred == 1 else '✅ Human'}")

        # Fraud detection
        try:
            fraud_input = pd.DataFrame([{
                "purchase_amount": total,
                "num_items": cart_df["quantity"].sum(),
                "account_age_days": 150,
                "session_duration": session_input["total_time_on_page"],
            }])
            fraud_result = predict_fraud(fraud_input)
            st.info(f"🛡️ Fraud Detection: {'🚨 Fraudulent' if fraud_result[0] == 1 else '✅ Safe'}")
        except Exception as e:
            st.error(f"Fraud check error: {e}")

        # Save live prediction
        live_df = pd.DataFrame([{
            "username": st.session_state["username"],
            "timestamp": order_time,
            "is_bot_predicted": int(bot_pred),
            "is_behavior_anomalous": int(behavior_pred),
            "typing_time": session_input["typing_time"],
            "click_count": session_input["click_count"],
            "total_time_on_page": session_input["total_time_on_page"],
        }])

        live_file = str(_PROJECT_ROOT / "data" / "live_predictions.csv")
        if os.path.exists(live_file):
            old = pd.read_csv(live_file)
            live_df = pd.concat([old, live_df], ignore_index=True)
        live_df.to_csv(live_file, index=False)

        # Clear cart
        st.session_state.cart = []
        st.success("✅ Order placed successfully!")
        st.rerun()
else:
    st.info("🛒 Your cart is empty.")

# ----------------------------
# 📦 Past Orders
# ----------------------------
st.header("📦 Your Past Orders")
try:
    history_file = str(_PROJECT_ROOT / "data" / "purchase_history.csv")
    df_history = pd.read_csv(history_file)
    df_user_orders = df_history[df_history["username"] == st.session_state["username"]]
    if not df_user_orders.empty:
        st.dataframe(df_user_orders.sort_values("timestamp", ascending=False))
    else:
        st.info("No past orders found.")
except FileNotFoundError:
    st.info("No order history available yet.")
