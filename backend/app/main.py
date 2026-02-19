from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import date
from typing import Optional

from backend.app.database import SessionLocal, engine, Base
from backend.app import models
from backend.app.auth import authenticate_user, create_access_token, get_current_user
from backend.init_db import init

app = FastAPI()

# RECREAR TABLAS (FASE CONSTRUCCIÓN)
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
# GET POLIZAS CON DIAS RESTANTES
# =========================

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
# POST POLIZAS
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
    nueva_poliza = models.Poliza(
        compania_id=poliza.compania_id,
        tipo_id=poliza.tipo_id,
        contacto_compania=poliza.contacto_compania,
        telefono_compania=poliza.telefono_compania,
        bien=poliza.bien,
        numero_poliza=poliza.numero_poliza,
        prima=poliza.prima,
        fecha_inicio=poliza.fecha_inicio,
        fecha_vencimiento=poliza.fecha_vencimiento,
        estado=poliza.estado
    )

    db.add(nueva_poliza)
    db.commit()
    db.refresh(nueva_poliza)

    return nueva_poliza
