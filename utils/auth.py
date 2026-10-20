
import os
from pathlib import Path

import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
USER_DB = DATA_DIR / "users.csv"
ADMIN_DB = DATA_DIR / "admin.csv"

COLUMNS = ["username", "password", "role", "phone", "email"]


def get_db_path(role):
    if role == "user":
        return USER_DB
    if role == "admin":
        return ADMIN_DB
    raise ValueError("Invalid role.")


def load_users(role="user"):
    db_path = get_db_path(role)

    try:
        df = pd.read_csv(db_path)
    except FileNotFoundError:
        return pd.DataFrame(columns=COLUMNS)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=COLUMNS)

    for column in COLUMNS:
        if column not in df.columns:
            df[column] = ""

    return df[COLUMNS]


def _save_account(username, password, role, phone="", email=""):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    df = load_users(role)

    if df["username"].astype(str).str.casefold().eq(
        username.strip().casefold()
    ).any():
        return False

    new_row = pd.DataFrame([{
        "username": username.strip(),
        "password": generate_password_hash(password),
        "role": role,
        "phone": phone.strip(),
        "email": email.strip(),
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    db_path = get_db_path(role)
    df.to_csv(db_path, index=False)
    return True


def save_user(username, password, role="user", phone="", email=""):
    # Public registration is restricted to ordinary user accounts.
    if role != "user":
        raise ValueError("Public registration can only create user accounts.")

    if not username.strip() or not password:
        raise ValueError("Username and password are required.")

    return _save_account(username, password, "user", phone, email)


def save_admin(username, password, phone="", email=""):
    # Call only from a trusted, private admin-provisioning process.
    if not username.strip() or not password:
        raise ValueError("Username and password are required.")

    return _save_account(username, password, "admin", phone, email)


def verify_login(username, password):
    for role in ("user", "admin"):
        df = load_users(role)
        match = df[
            df["username"].astype(str).str.casefold()
            == username.strip().casefold()
        ]

        if not match.empty:
            stored_hash = str(match.iloc[0]["password"])

            if check_password_hash(stored_hash, password):
                return {
                    "role": role,
                    "phone": str(match.iloc[0].get("phone", "") or ""),
                    "email": str(match.iloc[0].get("email", "") or ""),
                }

    return None


def get_user_contact(username):
    for role in ("user", "admin"):
        df = load_users(role)
        match = df[
            df["username"].astype(str).str.casefold()
            == username.strip().casefold()
        ]

        if not match.empty:
            return {
                "phone": str(match.iloc[0].get("phone", "") or ""),
                "email": str(match.iloc[0].get("email", "") or ""),
            }

    return {"phone": "", "email": ""}
