import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.auth import get_current_user
from app.database import Base, engine
from app.models import User
from app.routers import predict, users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(predict.router)


@app.get("/")
def root():
    return {"message": "Hello from a unique FastAPI app!"}


@app.get("/secure")
def secure_area(current_user: User = Depends(get_current_user)):
    return {"message": f"Welcome {current_user.username}, you passed the authentication!"}
