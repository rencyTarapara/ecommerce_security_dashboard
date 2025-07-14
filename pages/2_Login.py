import streamlit as st
from utils.auth import verify_login

st.title("🔐 Login")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.phone = ""
    st.session_state.email = ""

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user_data = verify_login(username, password)
    if user_data:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = user_data["role"]
        st.session_state.phone = user_data.get("phone", "")
        st.session_state.email = user_data.get("email", "")
        st.success(f"Welcome, {username}! You are logged in as {user_data['role']}.")
    else:
        st.error("❌ Invalid username or password.")
