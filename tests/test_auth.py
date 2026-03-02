import pytest
from fastapi import HTTPException
from app.auth import create_access_token, decode_token


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "alice"})
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token_returns_username():
    token = create_access_token({"sub": "alice"})
    username = decode_token(token)
    assert username == "alice"


def test_decode_token_invalid_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        decode_token("not.a.valid.token")
    assert exc_info.value.status_code == 401
