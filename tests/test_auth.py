"""
Unit tests for utils/auth.py
Run with: pytest tests/test_auth.py -v
"""
import os
import tempfile
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch

# Ensure the project root is on the path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# Patch the DB paths to use a temp directory so tests don't touch real data
@pytest.fixture(autouse=True)
def isolated_db(tmp_path):
    """Redirect USER_DB and ADMIN_DB to a temp directory for each test."""
    import utils.auth as auth_module
    user_db = str(tmp_path / "users.csv")
    admin_db = str(tmp_path / "admin.csv")
    original_user = auth_module.USER_DB
    original_admin = auth_module.ADMIN_DB
    auth_module.USER_DB = user_db
    auth_module.ADMIN_DB = admin_db
    yield
    auth_module.USER_DB = original_user
    auth_module.ADMIN_DB = original_admin


def test_load_users_returns_empty_df_when_no_file():
    from utils.auth import load_users
    df = load_users("user")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["username", "password", "role", "phone", "email"]
    assert df.empty


def test_save_user_creates_user():
    from utils.auth import save_user, load_users
    result = save_user("testuser", "securepass123", role="user", phone="1234567890", email="test@example.com")
    assert result is True
    df = load_users("user")
    assert "testuser" in df["username"].values


def test_save_user_rejects_duplicate():
    from utils.auth import save_user
    save_user("dupeuser", "pass1", role="user")
    result = save_user("dupeuser", "pass2", role="user")
    assert result is False


def test_verify_login_correct_credentials():
    from utils.auth import save_user, verify_login
    save_user("loginuser", "correctpass", role="user", phone="9999999999", email="login@example.com")
    result = verify_login("loginuser", "correctpass")
    assert result is not None
    assert result["role"] == "user"
    assert result["email"] == "login@example.com"


def test_verify_login_wrong_password():
    from utils.auth import save_user, verify_login
    save_user("loginuser2", "realpass", role="user")
    result = verify_login("loginuser2", "wrongpass")
    assert result is None


def test_verify_login_unknown_user():
    from utils.auth import verify_login
    result = verify_login("nonexistent", "anypass")
    assert result is None


def test_save_admin_user():
    from utils.auth import save_admin, load_users
    result = save_admin("adminuser", "adminpass", phone="0000000000", email="admin@example.com")
    assert result is True
    df = load_users("admin")
    assert "adminuser" in df["username"].values
    # Verify it's NOT in users.csv
    user_df = load_users("user")
    assert "adminuser" not in user_df["username"].values


def test_verify_admin_login():
    from utils.auth import save_admin, verify_login
    save_admin("adminlogin", "adminpass123")
    result = verify_login("adminlogin", "adminpass123")
    assert result is not None
    assert result["role"] == "admin"


def test_public_registration_cannot_create_admin():
    from utils.auth import save_user, load_users
    import pytest
    with pytest.raises(ValueError):
        save_user("sneaky", "pass", role="admin")
    assert load_users("admin").empty


def test_passwords_are_stored_hashed():
    from utils.auth import save_user, load_users
    save_user("hashcheck", "plaintext-pass")
    stored = load_users("user").iloc[0]["password"]
    assert stored != "plaintext-pass"
    assert stored.startswith(("scrypt:", "pbkdf2:"))


def test_get_user_contact():
    from utils.auth import save_user, get_user_contact
    save_user("contactuser", "pass", role="user", phone="5551234567", email="contact@example.com")
    info = get_user_contact("contactuser")
    assert info["phone"] == "5551234567"
    assert info["email"] == "contact@example.com"


def test_get_user_contact_not_found():
    from utils.auth import get_user_contact
    info = get_user_contact("ghost")
    assert info == {"phone": "", "email": ""}
