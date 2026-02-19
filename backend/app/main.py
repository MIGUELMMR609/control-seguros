from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime

from .database import SessionLocal, engine
from . import models
from .auth import authenticate_user, create_access_token, get_current_user
from .scheduler import iniciar_scheduler

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Iniciar sistema automático de revisión de vencimientos
iniciar_scheduler()

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
