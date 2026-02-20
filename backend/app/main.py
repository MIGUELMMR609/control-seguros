from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
import os

from .database import SessionLocal, engine
from .models import Base, Poliza

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"mensaje": "Backend funcionando"}

@app.post("/polizas")
def crear_poliza(data: dict, db: Session = Depends(get_db)):

    poliza_existente = db.query(Poliza).filter(
        Poliza.numero_poliza == data["numero_poliza"]
    ).first()

    if poliza_existente:
        raise HTTPException(status_code=400, detail="Número de póliza ya existe")

    nueva = Poliza(
        numero_poliza=data["numero_poliza"],
        bien=data["bien"],
        prima=data["prima"],
        fecha_inicio=datetime.strptime(data["fecha_inicio"], "%Y-%m-%d"),
        fecha_vencimiento=datetime.strptime(data["fecha_vencimiento"], "%Y-%m-%d"),
        estado=data.get("estado", "Activa"),
        aviso_enviado=False
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return {"mensaje": "Póliza creada correctamente", "id": nueva.id}

@app.get("/polizas")
def listar_polizas(db: Session = Depends(get_db)):
    polizas = db.query(Poliza).all()

    return [
        {
            "id": p.id,
            "numero_poliza": p.numero_poliza,
            "bien": p.bien,
            "prima": p.prima,
            "fecha_inicio": p.fecha_inicio.date(),
            "fecha_vencimiento": p.fecha_vencimiento.date(),
            "estado": p.estado,
            "aviso_enviado": p.aviso_enviado,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
        for p in polizas
    ]

@app.get("/polizas/{poliza_id}")
def obtener_poliza(poliza_id: int, db: Session = Depends(get_db)):
    poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()

    if not poliza:
        raise HTTPException(status_code=404, detail="Póliza no encontrada")

    return {
        "id": poliza.id,
        "numero_poliza": poliza.numero_poliza,
        "bien": poliza.bien,
        "prima": poliza.prima,
        "fecha_inicio": poliza.fecha_inicio.date(),
        "fecha_vencimiento": poliza.fecha_vencimiento.date(),
        "estado": poliza.estado,
        "aviso_enviado": poliza.aviso_enviado,
        "created_at": poliza.created_at,
        "updated_at": poliza.updated_at,
    }

@app.put("/polizas/{poliza_id}")
def actualizar_poliza(poliza_id: int, data: dict, db: Session = Depends(get_db)):

    poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()

    if not poliza:
        raise HTTPException(status_code=404, detail="Póliza no encontrada")

    if "bien" in data:
        poliza.bien = data["bien"]

    if "prima" in data:
        poliza.prima = data["prima"]

    if "fecha_vencimiento" in data:
        poliza.fecha_vencimiento = datetime.strptime(
            data["fecha_vencimiento"], "%Y-%m-%d"
        )

    if "estado" in data:
        poliza.estado = data["estado"]

    db.commit()

    return {"mensaje": "Póliza actualizada correctamente"}

@app.delete("/polizas/{poliza_id}")
def eliminar_poliza(poliza_id: int, db: Session = Depends(get_db)):

    poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()

    if not poliza:
        raise HTTPException(status_code=404, detail="Póliza no encontrada")

    db.delete(poliza)
    db.commit()

    return {"mensaje": "Póliza eliminada correctamente"}

@app.post("/revisar-vencimientos")
def revisar_vencimientos(db: Session = Depends(get_db)):

    hoy = datetime.utcnow().date()
    fecha_objetivo = hoy + timedelta(days=15)

    polizas = db.query(Poliza).filter(
        Poliza.fecha_vencimiento == fecha_objetivo,
        Poliza.aviso_enviado == False
    ).all()

    enviados = 0

    for poliza in polizas:
        try:
            msg = EmailMessage()
            msg["Subject"] = f"Vencimiento póliza {poliza.numero_poliza}"
            msg["From"] = os.getenv("EMAIL_USER")
            msg["To"] = os.getenv("EMAIL_USER")
            msg.set_content(
                f"La póliza {poliza.numero_poliza} vence el {poliza.fecha_vencimiento.date()}"
            )

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(
                    os.getenv("EMAIL_USER"),
                    os.getenv("EMAIL_PASSWORD")
                )
                server.send_message(msg)

            poliza.aviso_enviado = True
            enviados += 1

        except Exception as e:
            print("Error enviando email:", e)

    db.commit()

    return {"polizas_revisadas": enviados}
