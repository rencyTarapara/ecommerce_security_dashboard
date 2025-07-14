import streamlit as st

st.set_page_config(
    page_title="E-Commerce Security Dashboard",
    layout="wide",
)

# 🛡️ Initialize session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# 🔘 LOGOUT UI in Sidebar
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown(f"👤 Logged in as: **{st.session_state.username}** ({st.session_state.role})")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.success("🔓 You have been logged out. Redirecting to Login...")
            st.experimental_rerun()

    # ✅ Auto-redirect based on role
    if st.session_state.role == "admin":
        st.switch_page("pages/4_AdminDashboard.py")
    elif st.session_state.role == "user":
        st.switch_page("pages/3_UserDashboard.py")

# 🛒 Dashboard Title (Shown only if not logged in)
st.title("🛒 E-Commerce Security Dashboard")
st.write("Welcome! Use the sidebar to access login, user panel, or admin panel.")
