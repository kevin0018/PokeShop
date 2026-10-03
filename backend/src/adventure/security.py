"""Opaque database sessions, scrypt passwords and explicit CSRF protection."""
import hashlib
import hmac
import secrets
from threading import BoundedSemaphore

COOKIE = "pokeshop_session"
SESSION_SECONDS = 7 * 24 * 60 * 60
_password_slots = BoundedSemaphore(2)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def csrf_token(token):
    return digest("csrf:" + token)


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    # Bound memory even when the allowed authentication attempts arrive together.
    with _password_slots:
        value = hashlib.scrypt(
            password.encode(),
            salt=bytes.fromhex(salt),
            n=32768,
            r=8,
            p=1,
            maxmem=64 * 1024 * 1024,
        ).hex()
    return f"scrypt${salt}${value}"


def verify_password(password, encoded):
    try:
        _, salt, _ = encoded.split("$")
        return hmac.compare_digest(hash_password(password, salt), encoded)
    except (ValueError, TypeError):
        return False
