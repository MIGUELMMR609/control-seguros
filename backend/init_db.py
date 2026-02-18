from backend.app.database import SessionLocal, engine
from backend.app import models
from sqlalchemy.exc import IntegrityError


def init():
    # Crear tablas si no existen
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Crear usuario inicial si no existe
    existing_user = db.query(models.User).filter(
        models.User.username == "miguel"
    ).first()

    if not existing_user:
        user = models.User(username="miguel", password="1234")
        db.add(user)
        try:
            db.commit()
            print("Usuario inicial creado.")
        except IntegrityError:
            db.rollback()
    else:
        print("Usuario ya existe.")

    db.close()


if __name__ == "__main__":
    init()
