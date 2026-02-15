from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas
from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm
from .auth import authenticate_user, create_access_token, get_current_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ---------------- CORS CONFIG CORRECTA ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://control-seguros-web.onrender.com",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------

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
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/polizas")
def obtener_polizas(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(models.Poliza).all()

@app.post("/polizas")
def crear_poliza(poliza: schemas.PolizaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    nueva = models.Poliza(**poliza.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.put("/polizas/{poliza_id}")
def actualizar_poliza(poliza_id: int, poliza: schemas.PolizaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_poliza = db.query(models.Poliza).filter(models.Poliza.id == poliza_id).first()
    if not db_poliza:
        raise HTTPException(status_code=404, detail="No encontrada")
    for key, value in poliza.dict().items():
        setattr(db_poliza, key, value)
    db.commit()
    return db_poliza

@app.delete("/polizas/{poliza_id}")
def eliminar_poliza(poliza_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_poliza = db.query(models.Poliza).filter(models.Poliza.id == poliza_id).first()
    if not db_poliza:
        raise HTTPException(status_code=404, detail="No encontrada")
    db.delete(db_poliza)
    db.commit()
    return {"mensaje": "Eliminada"}
