from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
import os

from .database import SessionLocal, engine
from .models import Base, Poliza
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Control Seguros API",
    version="1.2",
)

origins = [
    "http://localhost:5173",
    "https://control-seguros-web.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"mensaje": "Backend funcionando"}

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

# ---------------- CRUD ----------------

@app.get("/polizas")
def listar_polizas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Poliza).all()

@app.post("/polizas")
def crear_poliza(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    nueva = Poliza(
        numero_poliza=data["numero_poliza"],
        bien=data["bien"],
        prima=float(data["prima"]),
        fecha_inicio=datetime.strptime(data["fecha_inicio"], "%Y-%m-%d").date(),
        fecha_vencimiento=datetime.strptime(data["fecha_vencimiento"], "%Y-%m-%d").date(),
        estado=data.get("estado", "Activa"),
        aviso_enviado=False
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return nueva

@app.put("/polizas/{poliza_id}")
def actualizar_poliza(
    poliza_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()

    if not poliza:
        raise HTTPException(status_code=404, detail="Póliza no encontrada")

    poliza.numero_poliza = data["numero_poliza"]
    poliza.bien = data["bien"]
    poliza.prima = float(data["prima"])
    poliza.fecha_inicio = datetime.strptime(data["fecha_inicio"], "%Y-%m-%d").date()
    poliza.fecha_vencimiento = datetime.strptime(data["fecha_vencimiento"], "%Y-%m-%d").date()

    db.commit()
    db.refresh(poliza)

    return poliza

@app.delete("/polizas/{poliza_id}")
def eliminar_poliza(
    poliza_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()

    if not poliza:
        raise HTTPException(status_code=404, detail="Póliza no encontrada")

    db.delete(poliza)
    db.commit()

    return {"mensaje": "Póliza eliminada correctamente"}

# ---------------- CRON 30 DÍAS ----------------

@app.post("/revisar-vencimientos")
def revisar_vencimientos(
    db: Session = Depends(get_db),
    x_cron_key: str = Header(None)
):
    secret = os.getenv("CRON_SECRET_KEY")

    if not x_cron_key or x_cron_key != secret:
        raise HTTPException(status_code=403, detail="Acceso no autorizado")

    hoy = datetime.utcnow().date()
    fecha_objetivo = hoy + timedelta(days=30)

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
                f"La póliza {poliza.numero_poliza} vence el {poliza.fecha_vencimiento}"
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
