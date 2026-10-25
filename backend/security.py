"""Argon2 password hashes and revocable, opaque bearer sessions."""

import hashlib
import secrets

from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError


_passwords = PasswordHash.recommended()
# Match the expensive verification path even when an account does not exist or
# still has a fixture placeholder (hash1 etc.). This is not a login password.
_dummy_hash = _passwords.hash(secrets.token_urlsafe(32))


def hash_password(password: str) -> str:
    return _passwords.hash(password)


def verify_password(password: str, stored_hash: str | None) -> bool:
    if stored_hash is None:
        _passwords.verify(password, _dummy_hash)
        return False
    try:
        return _passwords.verify(password, stored_hash)
    except (UnknownHashError, ValueError):
        # Existing seed.sql deliberately uses non-password placeholders.
        _passwords.verify(password, _dummy_hash)
        return False


def new_token() -> str:
    return secrets.token_urlsafe(32)


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
