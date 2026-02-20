from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import engine, SessionLocal
from . import models
import smtplib
import os
from email.mime.text import MIMEText

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


def enviar_email(destinatario, asunto, mensaje):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 465
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")

        msg = MIMEText(mensaje)
        msg["Subject"] = asunto
        msg["From"] = email_user
        msg["To"] = destinatario

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_user, email_password)
            server.send_message(msg)

        print("EMAIL ENVIADO CORRECTAMENTE")

    except Exception as e:
        print("ERROR ENVIANDO EMAIL:", e)


@app.get("/")
def root():
    return {"mensaje": "Backend funcionando"}


@app.post("/polizas")
def crear_poliza(data: dict):
    db: Session = SessionLocal()

    nueva = models.Poliza(
        numero_poliza=data["numero_poliza"],
        bien=data["bien"],
        prima=data["prima"],
        fecha_inicio=data["fecha_inicio"],
        fecha_vencimiento=data["fecha_vencimiento"],
        estado=data["estado"],
        aviso_enviado=False
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    db.close()

    return nueva


@app.get("/ver-polizas")
def ver_polizas():
    db: Session = SessionLocal()
    polizas = db.query(models.Poliza).all()
    resultado = []

    for p in polizas:
        resultado.append({
            "id": p.id,
            "numero_poliza": p.numero_poliza,
            "fecha_vencimiento": p.fecha_vencimiento,
            "aviso_enviado": p.aviso_enviado
        })

    db.close()
    return resultado


@app.post("/revisar-vencimientos")
def revisar_vencimientos():
    db: Session = SessionLocal()
    hoy = datetime.utcnow().date()
    fecha_objetivo = hoy + timedelta(days=15)

    polizas = db.query(models.Poliza).filter(
        models.Poliza.fecha_vencimiento == fecha_objetivo,
        models.Poliza.aviso_enviado == False
    ).all()

    for poliza in polizas:
        asunto = "Aviso: Vencimiento en 15 días"
        mensaje = f"""
La póliza {poliza.numero_poliza}
vence el día {poliza.fecha_vencimiento}.
"""

        enviar_email(
            os.getenv("EMAIL_USER"),
            asunto,
            mensaje
        )

        poliza.aviso_enviado = True
        db.commit()

    db.close()
    return {"polizas_revisadas": len(polizas)}
