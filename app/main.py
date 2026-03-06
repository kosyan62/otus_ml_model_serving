import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Security
from passlib.context import CryptContext

from app.auth import JWTAuthBackend, doc_bearer, get_current_user, on_auth_error
from starlette.middleware.authentication import AuthenticationMiddleware
from app.database import Base, SessionLocal, engine
from app.models import User
from app.routers import admin, auth, predict
from app.schemas import UserResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    app.state.start_time = time.time()

    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@localhost")
    if admin_username and admin_password:
        db = SessionLocal()
        try:
            username_taken = db.query(User).filter(User.username == admin_username).first()
            email_taken = db.query(User).filter(User.email == admin_email).first()
            if not username_taken and not email_taken:
                db.add(User(
                    username=admin_username,
                    email=admin_email,
                    hashed_password=_pwd_context.hash(admin_password),
                    role="admin",
                ))
                db.commit()
                logging.getLogger(__name__).info("Admin user seeded: %s", admin_username)
        finally:
            db.close()

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend(), on_error=on_auth_error)

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Hello from a unique FastAPI app!"}


@app.get("/me", response_model=UserResponse, dependencies=[Security(doc_bearer)])
def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/secure", dependencies=[Security(doc_bearer)])
def secure_area(current_user: User = Depends(get_current_user)):
    return {"message": f"Welcome {current_user.username}, you passed the authentication!"}
