import pytest
from pydantic import ValidationError
from app.schemas import UserCreate, LoginRequest, UserResponse, TokenResponse


def test_user_create_valid():
    u = UserCreate(username="alice", email="alice@example.com", password="secret123")
    assert u.username == "alice"
    assert u.email == "alice@example.com"


def test_user_create_missing_email():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", password="secret123")


def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="not-an-email", password="secret123")


def test_user_create_missing_password():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="alice@example.com")


def test_user_create_password_too_short():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", email="alice@example.com", password="short")


def test_login_request_valid():
    req = LoginRequest(username="alice", password="secret")
    assert req.username == "alice"


def test_user_response_from_orm():
    class FakeUser:
        id = 1
        username = "alice"
        email = "alice@example.com"
        role = "user"
    resp = UserResponse.model_validate(FakeUser())
    assert resp.id == 1
    assert resp.username == "alice"
    assert resp.email == "alice@example.com"
    assert resp.role == "user"


def test_token_response_default_type():
    t = TokenResponse(access_token="abc123", expires_in=1800)
    assert t.token_type == "bearer"
    assert t.expires_in == 1800
