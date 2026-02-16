from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


# =========================
# USER
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)


# =========================
# COMPANIAS
# =========================

class Compania(Base):
    __tablename__ = "companias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)


# =========================
# TIPOS
# =========================

class Tipo(Base):
    __tablename__ = "tipos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)


# =========================
# POLIZA
# =========================

class Poliza(Base):
    __tablename__ = "polizas"

    id = Column(Integer, primary_key=True, index=True)

    compania_id = Column(Integer, ForeignKey("companias.id"))
    tipo_id = Column(Integer, ForeignKey("tipos.id"))

    contacto_compania = Column(String, nullable=True)
    telefono_compania = Column(String, nullable=True)

    bien = Column(String, nullable=False)
    numero_poliza = Column(String, nullable=False, unique=True)
    prima = Column(Float, nullable=False)

    fecha_inicio = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)

    estado = Column(String, default="activa")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    compania = relationship("Compania")
    tipo = relationship("Tipo")
