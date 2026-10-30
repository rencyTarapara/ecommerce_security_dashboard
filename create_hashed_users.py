"""Provision an admin account.

Run from the project root:

    python create_hashed_users.py

The password is read from a hidden prompt, hashed with Werkzeug, and written to
data/admin.csv through utils.auth.save_admin. Nothing is hardcoded, and existing
accounts are never overwritten (a duplicate username is rejected).
"""
import getpass
import sys

from utils.auth import save_admin


def main() -> int:
    username = input("Admin username: ").strip()
    email = input("Admin email: ").strip()
    phone = input("Admin phone: ").strip()
    password = getpass.getpass("Admin password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Passwords do not match.")
        return 1

    try:
        created = save_admin(username, password, phone=phone, email=email)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    if not created:
        print("An admin with that username already exists.")
        return 1

    print(f"Admin '{username}' created.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
