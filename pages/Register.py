
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st
from utils.auth import save_user

st.title("📝 Register")

new_username = st.text_input("Choose a username")
new_password = st.text_input("Choose a password", type="password")
new_phone = st.text_input("📱 Enter your phone number")
new_email = st.text_input("📧 Enter your email address")

register_button = st.button("Register")

if register_button:
    if not new_username.strip():
        st.error("Username is required.")
    elif not new_password:
        st.error("Password is required.")
    elif not new_phone.strip() or not new_email.strip():
        st.error("Phone number and email are required.")
    else:
        try:
            success = save_user(
                username=new_username,
                password=new_password,
                phone=new_phone,
                email=new_email,
            )

            if not success:
                st.error("Username already exists. Please choose another.")
            else:
                st.success("Account created. You can now log in.")

                try:
                    sender_email = st.secrets["EMAIL"]["sender"]
                    app_password = st.secrets["EMAIL"]["app_password"]

                    message = MIMEMultipart("alternative")
                    message["Subject"] = "Registration Successful"
                    message["From"] = sender_email
                    message["To"] = new_email

                    text = (
                        f"Hello {new_username},\n\n"
                        "Your user account has been registered successfully.\n\n"
                        "Thank you for joining our platform!"
                    )
                    message.attach(MIMEText(text, "plain"))

                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(sender_email, app_password)
                        server.sendmail(
                            sender_email,
                            new_email,
                            message.as_string(),
                        )

                    st.success("Confirmation email sent!")

                except (KeyError, FileNotFoundError):
                    st.info(
                        "Email confirmation skipped: email secrets "
                        "are not configured."
                    )
                except Exception:
                    st.warning(
                        "Account created, but the confirmation email "
                        "could not be sent. Check email configuration."
                    )

        except (OSError, pd.errors.ParserError) as exc:
            st.error("Unable to save the account. Check file access and CSV data.")
        except ValueError as exc:
            st.error(str(exc))
