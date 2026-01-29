import json
from pathlib import Path
import bcrypt

USERS_PATH = Path("data/users.json")

def _load_users() -> dict:
    if not USERS_PATH.exists():
        USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
        USERS_PATH.write_text("{}", encoding="utf-8")
    return json.loads(USERS_PATH.read_text(encoding="utf-8") or "{}")

def _save_users(users: dict):
    USERS_PATH.write_text(json.dumps(users, indent=2), encoding="utf-8")

def register_user(email: str, password: str) -> tuple[bool, str]:
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, "Enter a valid email."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    users = _load_users()
    if email in users:
        return False, "User already exists. Please login."

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users[email] = {"password_hash": hashed, "created_at": int(__import__("time").time())}
    _save_users(users)
    return True, "Registered successfully."

def verify_password(email: str, password: str) -> bool:
    email = email.strip().lower()
    users = _load_users()
    if email not in users:
        return False
    stored_hash = users[email]["password_hash"].encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash)
