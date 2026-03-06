import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
from sqlalchemy.orm import Session

from app.auth import doc_bearer, require_role
from app.database import get_db
from app.models import User
from app.schemas import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Security(doc_bearer), require_role("admin")],
)


@router.get("/metrics")
def metrics(request: Request):
    return {
        "uptime_seconds": round(time.time() - request.app.state.start_time),
        "status": "ok",
    }


@router.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user: User | None = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    logger.info("User deleted by admin: id=%d", user_id)
    return user
