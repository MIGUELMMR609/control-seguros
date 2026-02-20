from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime

from .database import SessionLocal, engine
from . import models, schemas
from .auth import authenticate_user, create_access_token, get_current_user
from .scheduler import iniciar_scheduler
from backend.init_db import create_initial_user


# =========================
# INICIALIZACIÓN
# =========================

models.Base.metadata.create_all(bind=engine)
create_initial_user()

app = FastAPI()

iniciar_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# DB DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# ROOT
# =========================

@app.get("/")
def root():
    return {"mensaje": "API funcionando"}


# =========================
# LOGIN
# =========================

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

@app.post("/polizas", response_model=schemas.PolizaResponse)
def crear_poliza(
    poliza: schemas.PolizaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    nueva = models.Poliza(
        **poliza.model_dump(),
        aviso_enviado=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


@app.get("/polizas", response_model=list[schemas.PolizaResponse])
def obtener_polizas(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    polizas = db.query(models.Poliza).all()
    resultado = []

    for p in polizas:
        dias_restantes = (p.fecha_vencimiento - datetime.utcnow().date()).days

        data = p.__dict__.copy()
        data["dias_restantes"] = dias_restantes

        resultado.append(data)

    return resultado


# =========================
# RENOVACIONES
# =========================

@app.post("/renovaciones", response_model=schemas.RenovacionResponse)
def crear_renovacion(
    renovacion: schemas.RenovacionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    nueva = models.Renovacion(**renovacion.model_dump())

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva


@app.get("/renovaciones/{poliza_id}", response_model=list[schemas.RenovacionResponse])
def obtener_renovaciones(
    poliza_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(models.Renovacion).filter(
        models.Renovacion.poliza_id == poliza_id
    ).all()


# =========================
# SINIESTROS
# =========================

@app.post("/siniestros", response_model=schemas.SiniestroResponse)
def crear_siniestro(
    siniestro: schemas.SiniestroCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    nuevo = models.Siniestro(**siniestro.model_dump())

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


@app.get("/siniestros/{poliza_id}", response_model=list[schemas.SiniestroResponse])
def obtener_siniestros(
    poliza_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(models.Siniestro).filter(
        models.Siniestro.poliza_id == poliza_id
    ).all()
