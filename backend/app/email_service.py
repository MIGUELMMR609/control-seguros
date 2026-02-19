import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from sqlalchemy.orm import Session
from backend.app import models
from backend.app.database import SessionLocal


EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def enviar_email(destinatario: str, asunto: str, mensaje: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = destinatario
        msg["Subject"] = asunto

        msg.attach(MIMEText(mensaje, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, destinatario, msg.as_string())
        server.quit()

        print("Email enviado correctamente")

    except Exception as e:
        print("Error enviando email:", e)


def comprobar_vencimientos():
    db: Session = SessionLocal()

    hoy = date.today()

    polizas = db.query(models.Poliza).all()

    for poliza in polizas:
        dias_restantes = (poliza.fecha_vencimiento - hoy).days

        if dias_restantes == 15:
            asunto = f"⚠️ Aviso vencimiento póliza {poliza.numero_poliza}"
            mensaje = f"""
Hola Miguel,

La póliza {poliza.numero_poliza} vence el {poliza.fecha_vencimiento}.

Faltan exactamente 15 días para su vencimiento.

Revisa renovación o negociación de prima.

Sistema Control Seguros
"""
            enviar_email(EMAIL_USER, asunto, mensaje)

    db.close()
