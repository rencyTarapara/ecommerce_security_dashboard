import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.auth import save_user

st.title("📝 Register")

new_username = st.text_input("Choose a username")
new_password = st.text_input("Choose a password", type="password")
new_phone = st.text_input("📱 Enter your phone number")
new_email = st.text_input("📧 Enter your email address")

# 👤 Add role selection
role = st.selectbox("Select your role", ["user", "admin"])

register_button = st.button("Register")

if register_button:
    if not new_phone or not new_email:
        st.error("Phone number and email are required.")
    else:
        success = save_user(
            username=new_username,
            password=new_password,
            phone=new_phone,
            email=new_email,
            role=role  # Pass role to saving function
        )

        if success:
            st.success("Account created. You can now log in.")

            # 📧 Send confirmation email
            try:
                sender_email = st.secrets["email_sender"]
                app_password = st.secrets["email_password"]

                message = MIMEMultipart("alternative")
                message["Subject"] = "📝 Registration Successful"
                message["From"] = sender_email
                message["To"] = new_email

                text = f"Hello {new_username},\n\nYour account has been registered with role: {role}.\n\nThank you for joining our platform!"
                message.attach(MIMEText(text, "plain"))

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, app_password)
                    server.sendmail(sender_email, new_email, message.as_string())

                st.success("📧 Confirmation email sent!")
            except Exception as e:
                st.error(f"Email Error: {e}")
        else:
            st.error("Username already exists or error saving user.")
