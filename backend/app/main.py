from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

from .database import SessionLocal, engine
from . import models
from .auth import authenticate_user, create_access_token, get_current_user
from .scheduler import iniciar_scheduler


# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Iniciar scheduler automático
iniciar_scheduler()


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependencia DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ROOT
@app.get("/")
def root():
    return {"mensaje": "API funcionando correctamente"}


# LOGIN
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# GET POLIZAS
@app.get("/polizas")
def obtener_polizas(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    resultado = []
    polizas = db.query(models.Poliza).all()

    for p in polizas:
        dias_restantes = (p.fecha_vencimiento - datetime.utcnow().date()).days

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


# POST POLIZA
@app.post("/polizas")
def crear_poliza(
    poliza: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    nueva_poliza = models.Poliza(
        compania_id=poliza.get("compania_id"),
        tipo_id=poliza.get("tipo_id"),
        contacto_compania=poliza.get("contacto_compania"),
        telefono_compania=poliza.get("telefono_compania"),
        bien=poliza.get("bien"),
        numero_poliza=poliza.get("numero_poliza"),
        prima=poliza.get("prima"),
        fecha_inicio=poliza.get("fecha_inicio"),
        fecha_vencimiento=poliza.get("fecha_vencimiento"),
        estado=poliza.get("estado", "activa")
    )

    db.add(nueva_poliza)
    db.commit()
    db.refresh(nueva_poliza)

    return nueva_poliza


# POST RENOVACION
@app.post("/renovaciones")
def crear_renovacion(
    renovacion: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    nueva_renovacion = models.Renovacion(
        poliza_id=renovacion.get("poliza_id"),
        anio=renovacion.get("anio"),
        prima=renovacion.get("prima"),
        fecha_renovacion=renovacion.get("fecha_renovacion")
    )

    db.add(nueva_renovacion)
    db.commit()
    db.refresh(nueva_renovacion)

    return nueva_renovacion


# GET RENOVACIONES POR POLIZA
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
