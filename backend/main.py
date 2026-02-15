from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ========================
# SEGURIDAD
# ========================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

fake_user = {
    "username": "miguel",
    "password": "1234"
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != fake_user["username"] or form_data.password != fake_user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    return {"access_token": "token_seguro", "token_type": "bearer"}

def verificar_token(token: str = Depends(oauth2_scheme)):
    if token != "token_seguro":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    return token

# ========================
# RUTAS
# ========================

@app.get("/")
def read_root():
    return {"mensaje": "API funcionando"}

@app.get("/polizas", response_model=list[schemas.Poliza])
def obtener_polizas(
    db: Session = Depends(get_db),
    token: str = Depends(verificar_token)
):
    return db.query(models.Poliza).all()

@app.post("/polizas", response_model=schemas.Poliza)
def crear_poliza(
    poliza: schemas.PolizaCreate,
    db: Session = Depends(get_db),
    token: str = Depends(verificar_token)
):
    nueva_poliza = models.Poliza(
        compania=poliza.compania,
        bien=poliza.bien,
        precio=poliza.precio,
        fecha_vencimiento=poliza.fecha_vencimiento,
        email_contacto=poliza.email_contacto
    )

    db.add(nueva_poliza)
    db.commit()
    db.refresh(nueva_poliza)
    return nueva_poliza
