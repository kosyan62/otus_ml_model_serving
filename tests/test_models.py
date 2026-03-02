from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def test_user_model_create():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    user = User(username="alice", hashed_password="fakehash")
    db.add(user)
    db.commit()
    db.refresh(user)
    assert user.id is not None
    assert user.username == "alice"
    db.close()
    Base.metadata.drop_all(bind=engine)