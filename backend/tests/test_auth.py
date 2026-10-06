import pytest
from app.security.password import hash_password, verify_password
from app.security.jwt import create_access_token, decode_access_token


def test_password_hashing():
    raw = "MySecurePassword123"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_generation():
    payload = {"sub": "12345", "role": "admin"}
    token = create_access_token(payload)
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "12345"
    assert decoded["role"] == "admin"
