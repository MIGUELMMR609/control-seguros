from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base


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

    compania_id = Column(Integer, ForeignKey("companias.id"), nullable=False)
    tipo_id = Column(Integer, ForeignKey("tipos.id"), nullable=False)

    contacto_compania = Column(String)
    telefono_compania = Column(String)

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

    renovaciones = relationship("Renovacion", back_populates="poliza", cascade="all, delete")
    siniestros = relationship("Siniestro", back_populates="poliza", cascade="all, delete")


# =========================
# RENOVACIONES
# =========================

class Renovacion(Base):
    __tablename__ = "renovaciones"

    id = Column(Integer, primary_key=True, index=True)
    poliza_id = Column(Integer, ForeignKey("polizas.id"), nullable=False)

    anio = Column(Integer, nullable=False)
    prima = Column(Float, nullable=False)
    fecha_renovacion = Column(Date, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    poliza = relationship("Poliza", back_populates="renovaciones")


# =========================
# SINIESTROS
# =========================

class Siniestro(Base):
    __tablename__ = "siniestros"

    id = Column(Integer, primary_key=True, index=True)
    poliza_id = Column(Integer, ForeignKey("polizas.id"), nullable=False)

    fecha = Column(Date, nullable=False)
    comunicado_compania = Column(Boolean, default=False)
    numero_parte = Column(String)

    descripcion = Column(String, nullable=False)
    acciones_realizadas = Column(String)

    finalizado = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    poliza = relationship("Poliza", back_populates="siniestros")
