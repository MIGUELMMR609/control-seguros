from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import SessionLocal
from .models import Poliza
import smtplib
import os
from email.mime.text import MIMEText


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


def revisar_vencimientos():
    db: Session = SessionLocal()

    try:
        hoy = datetime.utcnow().date()
        fecha_objetivo = hoy + timedelta(days=15)

        polizas = db.query(Poliza).filter(
            Poliza.fecha_vencimiento == fecha_objetivo,
            Poliza.aviso_enviado == False
        ).all()

        for poliza in polizas:
            asunto = "PRUEBA - Vencimiento en 15 días"
            mensaje = f"""
PRUEBA DE SISTEMA

La póliza número: {poliza.numero_poliza}
Bien asegurado: {poliza.bien}
Fecha de vencimiento: {poliza.fecha_vencimiento}

Faltan 15 días para su vencimiento.
"""

            enviar_email(
                os.getenv("EMAIL_USER"),
                asunto,
                mensaje
            )

            poliza.aviso_enviado = True
            db.commit()

    except Exception as e:
        print("ERROR EN REVISIÓN:", e)

    finally:
        db.close()


def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(revisar_vencimientos, "interval", minutes=1)
    scheduler.start()
