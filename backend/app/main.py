from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.database import SessionLocal, engine, Base
from backend.app import models
from backend.app.auth import authenticate_user, create_access_token, get_current_user
from backend.init_db import create_initial_user

app = FastAPI()

# BORRAR Y RECREAR TABLAS EN CADA ARRANQUE (AHORA MISMO ESTAMOS EN FASE DE RECONSTRUCCIÓN)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    create_initial_user()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
def root():
    return {"mensaje": "API funcionando"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/polizas")
def obtener_polizas(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(models.Poliza).all()
