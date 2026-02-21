from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, date, datetime
from .database import SessionLocal, engine
from .models import Base, Poliza, AvisoEnviado
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

# ---------------- CORS ----------------

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


# ---------------- EMAIL ----------------

def enviar_email(poliza, dias):
    msg = EmailMessage()
    msg["Subject"] = f"Aviso {dias} días - póliza {poliza.numero_poliza}"
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = os.getenv("EMAIL_USER")

    msg.set_content(
        f"La póliza {poliza.numero_poliza} del bien '{poliza.bien}' vence en {dias} días ({poliza.fecha_vencimiento})."
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(
            os.getenv("EMAIL_USER"),
            os.getenv("EMAIL_PASSWORD"),
        )
        server.send_message(msg)


# ---------------- VERIFICACIÓN MULTIAVISO V3 ----------------

def verificar_vencimientos():
    db = SessionLocal()
    hoy = date.today()

    polizas = db.query(Poliza).all()

    for poliza in polizas:
        dias_restantes = (poliza.fecha_vencimiento - hoy).days

        if dias_restantes in [30, 15, 7]:

            ya_enviado = db.query(AvisoEnviado).filter(
                AvisoEnviado.poliza_id == poliza.id,
                AvisoEnviado.tipo_aviso == dias_restantes
            ).first()

            if not ya_enviado:
                try:
                    enviar_email(poliza, dias_restantes)

                    nuevo_aviso = AvisoEnviado(
                        poliza_id=poliza.id,
                        tipo_aviso=dias_restantes,
                        fecha_envio=datetime.utcnow()
                    )

                    db.add(nuevo_aviso)
                    db.commit()

                except Exception as e:
                    print("Error enviando email:", e)

    db.close()


# ---------------- CRON SEGURO ----------------

CRON_SECRET = "8fj39fk39fKJH34kjh23498sd9fKJH"

@app.post("/revisar-vencimientos")
def revisar_vencimientos(request: Request):
    cron_key = request.headers.get("X-CRON-KEY")

    if cron_key != CRON_SECRET:
        return {"error": "No autorizado"}

    verificar_vencimientos()

    return {"mensaje": "Revisión ejecutada correctamente"}


# ---------------- ENDPOINT HISTÓRICO AVISOS ----------------

@app.get("/polizas/{poliza_id}/avisos")
def obtener_avisos(poliza_id: int, user: str = Depends(get_current_user)):
    db = SessionLocal()

    avisos = db.query(AvisoEnviado).filter(
        AvisoEnviado.poliza_id == poliza_id
    ).all()

    resultado = [
        {
            "id": a.id,
            "tipo_aviso": a.tipo_aviso,
            "fecha_envio": a.fecha_envio
        }
        for a in avisos
    ]

    db.close()
    return resultado


# ---------------- CRUD POLIZAS ----------------

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

    enviar_email(poliza, 0)

    db.close()

    return {"mensaje": "Recordatorio enviado correctamente"}
