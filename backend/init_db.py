from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_initial_user():
    db: Session = SessionLocal()

    user = db.query(User).filter(User.username == "miguel").first()

    if not user:
        hashed_password = pwd_context.hash("1234")

        new_user = User(
            username="miguel",
            password=hashed_password
        )

        db.add(new_user)
        db.commit()
        print("Usuario inicial creado.")
    else:
        print("Usuario ya existe.")

    db.close()
