from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, date
from .database import SessionLocal, engine
from .models import Base, Poliza, AvisoEnviado
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS PRODUCCIÓN
origins = [
    "http://localhost:5173",
    "https://control-seguros-web.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- LOGIN ----------------

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ---------------- CRUD ----------------

@app.get("/polizas")
def listar_polizas(user: str = Depends(get_current_user)):
    db = SessionLocal()
    polizas = db.query(Poliza).all()
    db.close()
    return polizas


@app.post("/polizas")
def crear_poliza(data: dict, user: str = Depends(get_current_user)):
    db = SessionLocal()
    nueva = Poliza(**data)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    db.close()
    return nueva


@app.put("/polizas/{poliza_id}")
def actualizar_poliza(poliza_id: int, data: dict, user: str = Depends(get_current_user)):
    db = SessionLocal()
    poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()

    if not poliza:
        db.close()
        raise HTTPException(status_code=404, detail="No encontrada")

    for key, value in data.items():
        setattr(poliza, key, value)

    db.commit()
    db.refresh(poliza)
    db.close()
    return poliza


@app.delete("/polizas/{poliza_id}")
def eliminar_poliza(poliza_id: int, user: str = Depends(get_current_user)):
    db = SessionLocal()
    poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()

    if not poliza:
        db.close()
        raise HTTPException(status_code=404, detail="No encontrada")

    db.delete(poliza)
    db.commit()
    db.close()
    return {"mensaje": "Eliminada correctamente"}


# ---------------- REVISIÓN AUTOMÁTICA ----------------

@app.post("/revisar-vencimientos")
def revisar_vencimientos():
    db = SessionLocal()
    hoy = date.today()
    polizas = db.query(Poliza).all()

    for poliza in polizas:
        dias_restantes = (poliza.fecha_vencimiento - hoy).days

        # 30 DÍAS
        if dias_restantes == 30 and not poliza.aviso_30:
            poliza.aviso_30 = True

            nuevo_aviso = AvisoEnviado(
                poliza_id=poliza.id,
                tipo_aviso=30
            )
            db.add(nuevo_aviso)

        # 15 DÍAS
        if dias_restantes == 15 and not poliza.aviso_15:
            poliza.aviso_15 = True

            nuevo_aviso = AvisoEnviado(
                poliza_id=poliza.id,
                tipo_aviso=15
            )
            db.add(nuevo_aviso)

        # 7 DÍAS
        if dias_restantes == 7 and not poliza.aviso_7:
            poliza.aviso_7 = True

            nuevo_aviso = AvisoEnviado(
                poliza_id=poliza.id,
                tipo_aviso=7
            )
            db.add(nuevo_aviso)

    db.commit()
    db.close()

    return {"mensaje": "Revisión ejecutada correctamente"}
