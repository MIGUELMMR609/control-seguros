from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from backend.database import SessionLocal
from backend.models import Poliza
from backend.email_utils import enviar_email


def comprobar_vencimientos():
    db = SessionLocal()
    hoy = datetime.now().date()

    polizas = db.query(Poliza).all()

    for poliza in polizas:
        if poliza.fecha_vencimiento:
            dias = (poliza.fecha_vencimiento - hoy).days
            if dias == 15:
                enviar_email(
                    poliza.email_contacto,
                    "Aviso vencimiento póliza",
                    f"La póliza {poliza.compania} vence en 15 días."
                )

    db.close()


def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(comprobar_vencimientos, "interval", days=1)
    scheduler.start()
