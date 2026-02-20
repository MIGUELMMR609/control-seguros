from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from .database import SessionLocal, engine
from .models import Base, Poliza
from .auth import get_current_user
import smtplib
from email.message import EmailMessage
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
