import streamlit as st

st.set_page_config(
    page_title="E-Commerce Security Dashboard",
    layout="wide",
)

# 🛡️ Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.phone = ""
    st.session_state.email = ""

# 🔘 Sidebar: show logged-in user info and logout button
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown(
            f"👤 Logged in as: **{st.session_state.username}** ({st.session_state.role})"
        )
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.session_state.phone = ""
            st.session_state.email = ""
            st.success("🔓 You have been logged out.")
            st.rerun()

    # ✅ Auto-redirect based on role after login
    if st.session_state.role == "admin":
        st.switch_page("pages/Admin_Dashboard.py")
    elif st.session_state.role == "user":
        st.switch_page("pages/User_Dashboard.py")

# 🛒 Landing page (shown when not logged in)
st.title("🛒 E-Commerce Security Dashboard")
st.write(
    "Welcome! Use the sidebar to navigate to **Login** or **Register**. "
    "After logging in you will be automatically redirected to your dashboard."
)
