from re import search as re_search
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError


def password_requirements(password: str) -> list:
    errors = []

    if len(password) < 8:
        errors.append("The password must be at least 8 characters.")

    if (w := re_search(r"\s", password)) and w.group():
        errors.append("The password cannot have whitespaces.")

    return errors

def verify_password(password: str, hashed_password: str) -> bool:
    ph = PasswordHasher()
    try:
        ph.verify(hashed_password, password)
        return True
    except VerifyMismatchError:
        return False

def hash_password(password: str) -> Any:
    ph = PasswordHasher()
    try:
        return ph.hash(password)
    except HashingError as e:
        print(f"ERROR::", e)
        return None
