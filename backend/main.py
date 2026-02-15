from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from jose import jwt

from . import models, schemas
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- AUTH ----------------

SECRET_KEY = "mi_clave_super_secreta"
ALGORITHM = "HS256"

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Token inválido")

# ---------------- DEPENDENCIA DB ----------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- RUTA TEST ----------------

@app.get("/")
def home():
    return {"mensaje": "API funcionando"}

# ---------------- LOGIN ----------------

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "miguel" and form_data.password == "1234":
        token = jwt.encode({"sub": form_data.username}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Credenciales incorrectas")

# ---------------- CREAR POLIZA ----------------

@app.post("/polizas", response_model=schemas.Poliza)
def crear_poliza(poliza: schemas.PolizaCreate, db: Session = Depends(get_db), token: str = Depends(verificar_token)):
    fecha = datetime.strptime(poliza.fecha_vencimiento, "%Y-%m-%d").date()

    nueva = models.Poliza(
        compania=poliza.compania,
        bien=poliza.bien,
        precio=poliza.precio,
        fecha_vencimiento=fecha,
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# ---------------- LISTAR POLIZAS ----------------

@app.get("/polizas", response_model=list[schemas.Poliza])
def listar_polizas(db: Session = Depends(get_db), token: str = Depends(verificar_token)):
    return db.query(models.Poliza).all()

# ---------------- ELIMINAR POLIZA ----------------

@app.delete("/polizas/{poliza_id}")
def eliminar_poliza(poliza_id: int, db: Session = Depends(get_db), token: str = Depends(verificar_token)):
    poliza = db.query(models.Poliza).filter(models.Poliza.id == poliza_id).first()
    if not poliza:
        raise HTTPException(status_code=404, detail="No encontrada")

    db.delete(poliza)
    db.commit()
    return {"mensaje": "Eliminada correctamente"}

# ---------------- EDITAR POLIZA ----------------

@app.put("/polizas/{poliza_id}", response_model=schemas.Poliza)
def editar_poliza(poliza_id: int, datos: schemas.PolizaCreate, db: Session = Depends(get_db), token: str = Depends(verificar_token)):
    poliza = db.query(models.Poliza).filter(models.Poliza.id == poliza_id).first()

    if not poliza:
        raise HTTPException(status_code=404, detail="No encontrada")

    poliza.compania = datos.compania
    poliza.bien = datos.bien
    poliza.precio = datos.precio
    poliza.fecha_vencimiento = datetime.strptime(datos.fecha_vencimiento, "%Y-%m-%d").date()

    db.commit()
    db.refresh(poliza)
    return poliza
