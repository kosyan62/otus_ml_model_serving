import logging
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
    UnauthenticatedUser,
)
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from starlette.responses import JSONResponse

from app.database import get_db
from app.models import User

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

logger = logging.getLogger(__name__)

doc_bearer = HTTPBearer(auto_error=False)  # for OpenAPI docs only — auth is in middleware

# Admin scopes include user scopes — cumulative hierarchy
_ROLE_SCOPES: dict[str, list[str]] = {
    "user":  ["authenticated", "user"],
    "admin": ["authenticated", "user", "admin"],
}


class AuthenticatedUser(BaseUser):
    def __init__(self, username: str, role: str) -> None:
        self.username = username
        self.role = role

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username


class JWTAuthBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> tuple[AuthCredentials, AuthenticatedUser] | None:
        auth_header = conn.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None  # → request.user = UnauthenticatedUser()

        token = auth_header[len("Bearer "):]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise AuthenticationError("Invalid or expired token")

        username: str | None = payload.get("sub")
        role: str = payload.get("role", "user")
        if not username:
            raise AuthenticationError("Token missing subject")

        scopes = _ROLE_SCOPES.get(role, ["authenticated"])
        return AuthCredentials(scopes), AuthenticatedUser(username, role)


def on_auth_error(request: Request, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=401)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["iat"] = now
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def require_role(min_role: str):
    def checker(request: Request) -> None:
        if not request.user.is_authenticated:
            logger.warning("Access denied: unauthenticated request to %s", request.url.path)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        if min_role not in request.auth.scopes:
            logger.warning(
                "Access denied: user=%s role=%s required=%s path=%s",
                request.user.display_name,
                request.user.role,
                min_role,
                request.url.path,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return Depends(checker)


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    if not request.user.is_authenticated:
        logger.warning("Access denied: unauthenticated request to %s", request.url.path)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user: User | None = db.query(User).filter(
        User.username == request.user.username
    ).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
