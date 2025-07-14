import pandas as pd
import os
from werkzeug.security import generate_password_hash, check_password_hash

USER_DB = "data/users.csv"
ADMIN_DB = "data/admin.csv"

# Utility: get the right database file based on role
def get_db_path(role):
    return USER_DB if role == "user" else ADMIN_DB

# Load users/admins based on role
def load_users(role="user"):
    db_path = get_db_path(role)
    try:
        return pd.read_csv(db_path)
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "password", "role", "phone", "email"])

# Save user/admin in appropriate file
def save_user(username, password, role="user", phone="", email=""):
    df = load_users(role)
    if username in df['username'].values:
        return False  # Username already exists

    hashed_password = generate_password_hash(password)
    new_user = pd.DataFrame([[username, hashed_password, role, phone, email]],
                            columns=["username", "password", "role", "phone", "email"])
    df = pd.concat([df, new_user], ignore_index=True)

    db_path = get_db_path(role)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    df.to_csv(db_path, index=False)
    return True

# Verify login by checking both user and admin databases
def verify_login(username, password):
    for role in ["user", "admin"]:
        df = load_users(role)
        user = df[df['username'] == username]
        if not user.empty:
            hashed_password = user.iloc[0]['password']
            if check_password_hash(hashed_password, password):
                return {
                    "role": user.iloc[0]["role"],
                    "phone": user.iloc[0].get("phone", ""),
                    "email": user.iloc[0].get("email", "")
                }
    return None

# Get contact info from both databases
def get_user_contact(username):
    for role in ["user", "admin"]:
        df = load_users(role)
        user = df[df['username'] == username]
        if not user.empty:
            return {
                "phone": user.iloc[0].get("phone", ""),
                "email": user.iloc[0].get("email", "")
            }
    return {"phone": "", "email": ""}
