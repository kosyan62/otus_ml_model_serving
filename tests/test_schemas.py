import pytest
from pydantic import ValidationError
from app.schemas import UserCreate, LoginRequest, UserResponse, TokenResponse


def test_user_create_valid():
    u = UserCreate(username="alice", password="secret123")
    assert u.username == "alice"
    assert u.password == "secret123"


def test_user_create_missing_field():
    with pytest.raises(ValidationError):
        UserCreate(username="alice")


def test_user_create_password_too_short():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", password="short")


def test_login_request_valid():
    req = LoginRequest(username="alice", password="secret")
    assert req.username == "alice"


def test_user_response_from_orm():
    class FakeUser:
        id = 1
        username = "alice"
    resp = UserResponse.model_validate(FakeUser())
    assert resp.id == 1
    assert resp.username == "alice"


def test_token_response_default_type():
    t = TokenResponse(access_token="abc123")
    assert t.token_type == "bearer"