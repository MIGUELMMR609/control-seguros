from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta, date, datetime
from .database import SessionLocal, engine
from .models import Base, Poliza
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
import smtplib
from email.message import EmailMessage
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
def ejecutar_verificacion_automatica():
    verificar_vencimientos_30_dias()

# 🔐 CORS PROFESIONAL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://control-seguros-web.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- LOGIN --------

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


# -------- EMAIL --------

def enviar_email(poliza):
    msg = EmailMessage()
    msg["Subject"] = f"Recordatorio póliza {poliza.numero_poliza}"
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = os.getenv("EMAIL_USER")

    msg.set_content(
        f"La póliza {poliza.numero_poliza} del bien '{poliza.bien}' vence el {poliza.fecha_vencimiento}"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(
            os.getenv("EMAIL_USER"),
            os.getenv("EMAIL_PASSWORD"),
        )
        server.send_message(msg)

# -------- VERIFICAR VENCIMIENTOS 30 DÍAS --------

def verificar_vencimientos_30_dias():
    db = SessionLocal()
    hoy = date.today()

    polizas = db.query(Poliza).filter(
        Poliza.aviso_enviado == False
    ).all()

    for poliza in polizas:
        dias_restantes = (poliza.fecha_vencimiento - hoy).days

        if dias_restantes == 30:
            enviar_email(poliza)
            poliza.aviso_enviado = True
            poliza.fecha_aviso_enviado = datetime.utcnow()
            db.commit()

    db.close()

# -------- CRUD --------

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


@app.post("/enviar-recordatorio/{poliza_id}")
def enviar_recordatorio_manual(poliza_id: int, user: str = Depends(get_current_user)):
    db = SessionLocal()
    poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()

    if not poliza:
        db.close()
        raise HTTPException(status_code=404, detail="Póliza no encontrada")

    enviar_email(poliza)
    db.close()

    return {"mensaje": "Recordatorio enviado correctamente"}


# -------- DEBUG COLUMNAS (TEMPORAL) --------

@app.get("/debug-columnas")
def ver_columnas():
    db = SessionLocal()
    resultado = db.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'polizas'
    """)).fetchall()
    db.close()
    return {"columnas": [r[0] for r in resultado]}
@app.get("/debug-crear-columna")
def crear_columna():
    db = SessionLocal()
    db.execute(text("""
        ALTER TABLE polizas
        ADD COLUMN IF NOT EXISTS fecha_aviso_enviado TIMESTAMP NULL;
    """))
    db.commit()
    db.close()
    return {"mensaje": "Columna creada si no existía"}
@app.get("/debug-dias/{poliza_id}")
def debug_dias(poliza_id: int):
    db = SessionLocal()
    poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()

    if not poliza:
        db.close()
        return {"error": "No encontrada"}

    hoy = date.today()
    dias = (poliza.fecha_vencimiento - hoy).days

    db.close()

    return {
        "hoy_backend": str(hoy),
        "fecha_vencimiento": str(poliza.fecha_vencimiento),
        "dias_restantes_backend": dias
    }
@app.get("/debug-poliza/{poliza_id}")
def debug_poliza(poliza_id: int):
    db = SessionLocal()
    poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()

    if not poliza:
        db.close()
        return {"error": "No encontrada"}

    resultado = {
        "id": poliza.id,
        "aviso_enviado": poliza.aviso_enviado,
        "fecha_aviso_enviado": str(poliza.fecha_aviso_enviado)
    }

    db.close()
    return resultado
