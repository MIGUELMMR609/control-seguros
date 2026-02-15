import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def enviar_email(destinatario: str, asunto: str, mensaje: str):
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_USER
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg.set_content(mensaje)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"Email enviado correctamente a {destinatario}")

    except Exception as e:
        print("Error enviando email:", e)
