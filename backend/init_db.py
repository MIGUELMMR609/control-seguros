from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app import models
import hashlib


def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


def create_initial_user():
    db: Session = SessionLocal()

    existing_user = db.query(models.User).filter(models.User.username == "miguel").first()

    if not existing_user:
        user = models.User(
            username="miguel",
            password=hash_password("1234")
        )
        db.add(user)
        db.commit()
        print("Usuario inicial creado.")
    else:
        print("Usuario ya existe.")

    db.close()
