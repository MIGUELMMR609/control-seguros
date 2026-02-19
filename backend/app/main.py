from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import date
from typing import Optional, List

from backend.app.database import SessionLocal, engine, Base
from backend.app import models
from backend.app.auth import authenticate_user, create_access_token, get_current_user
from backend.init_db import init


app = FastAPI()

# 🔴 SOLO ESTE DEPLOY: reconstruir base completa
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    init()


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"mensaje": "API funcionando"}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# =========================
# POLIZAS
# =========================

class PolizaCreate(BaseModel):
    compania_id: Optional[int] = None
    tipo_id: Optional[int] = None
    contacto_compania: Optional[str] = None
    telefono_compania: Optional[str] = None
    bien: str
    numero_poliza: str
    prima: float
    fecha_inicio: date
    fecha_vencimiento: date
    estado: str = "activa"


@app.post("/polizas")
def crear_poliza(
    poliza: PolizaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    nueva_poliza = models.Poliza(**poliza.dict())
    db.add(nueva_poliza)
    db.commit()
    db.refresh(nueva_poliza)
    return nueva_poliza


@app.get("/polizas")
def obtener_polizas(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    polizas = db.query(models.Poliza).all()
    resultado = []

    for p in polizas:
        dias_restantes = (p.fecha_vencimiento - date.today()).days

        resultado.append({
            "id": p.id,
            "compania_id": p.compania_id,
            "tipo_id": p.tipo_id,
            "contacto_compania": p.contacto_compania,
            "telefono_compania": p.telefono_compania,
            "bien": p.bien,
            "numero_poliza": p.numero_poliza,
            "prima": p.prima,
            "fecha_inicio": p.fecha_inicio,
            "fecha_vencimiento": p.fecha_vencimiento,
            "estado": p.estado,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "dias_restantes": dias_restantes
        })

    return resultado


# =========================
# RENOVACIONES
# =========================

class RenovacionCreate(BaseModel):
    poliza_id: int
    anio: int
    prima: float
    fecha_renovacion: date


@app.post("/renovaciones")
def crear_renovacion(
    renovacion: RenovacionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Validar que exista la póliza
    poliza = db.query(models.Poliza).filter(models.Poliza.id == renovacion.poliza_id).first()

    if not poliza:
        raise HTTPException(status_code=404, detail="Poliza no encontrada")

    nueva_renovacion = models.Renovacion(**renovacion.dict())

    db.add(nueva_renovacion)
    db.commit()
    db.refresh(nueva_renovacion)

    return nueva_renovacion


@app.get("/renovaciones/{poliza_id}")
def obtener_renovaciones(
    poliza_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    renovaciones = db.query(models.Renovacion).filter(
        models.Renovacion.poliza_id == poliza_id
    ).all()

    return renovaciones
