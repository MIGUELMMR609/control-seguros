import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from .database import SessionLocal
from . import models
import smtplib
from email.mime.text import MIMEText


# =========================
# EMAIL ENVÍO
# =========================

def enviar_email(destinatario: str, asunto: str, mensaje: str):
    gmail_user = os.getenv("EMAIL_USER")
    gmail_password = os.getenv("EMAIL_PASSWORD")

    if not gmail_user or not gmail_password:
        print("EMAIL_USER o EMAIL_PASSWORD no configurado")
        return

    msg = MIMEText(mensaje)
    msg["Subject"] = asunto
    msg["From"] = gmail_user
    msg["To"] = destinatario

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, destinatario, msg.as_string())
        print("Email enviado correctamente")
    except Exception as e:
        print("Error enviando email:", e)


# =========================
# REVISIÓN VENCIMIENTOS
# =========================

def revisar_vencimientos():
    print("Revisando vencimientos...")
    db: Session = SessionLocal()

    hoy = datetime.utcnow().date()
    fecha_objetivo = hoy + timedelta(days=15)

    polizas = db.query(models.Poliza).all()

    for poliza in polizas:
        if (
            poliza.fecha_vencimiento == fecha_objetivo
            and poliza.aviso_enviado is False
        ):

            asunto = "Aviso de vencimiento de póliza"
            mensaje = f"""
La póliza {poliza.numero_poliza}
del bien {poliza.bien}
vence el {poliza.fecha_vencimiento}.
"""

            enviar_email(
                destinatario=os.getenv("EMAIL_USER"),
                asunto=asunto,
                mensaje=mensaje
            )

            poliza.aviso_enviado = True
            db.commit()

    db.close()


# =========================
# SCHEDULER
# =========================

def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(revisar_vencimientos, "interval", minutes=1)
    scheduler.start()
    print("Scheduler iniciado en modo test (1 minuto)")
