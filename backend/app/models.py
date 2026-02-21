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

    compania_id = Column(Integer, ForeignKey("companias.id"), nullable=True)
    tipo_id = Column(Integer, ForeignKey("tipos.id"), nullable=True)

    contacto_compania = Column(String, nullable=True)
    telefono_compania = Column(String, nullable=True)

    bien = Column(String, nullable=False)
    numero_poliza = Column(String, nullable=False, unique=True)
    prima = Column(Float, nullable=False)

    fecha_inicio = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)

    estado = Column(String, default="activa")

    # ---- V4 CONFIGURACIÓN DINÁMICA ----
    aviso_30 = Column(Boolean, default=True)
    aviso_15 = Column(Boolean, default=True)
    aviso_7  = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    compania = relationship("Compania")
    tipo = relationship("Tipo")
    avisos = relationship("AvisoEnviado", back_populates="poliza")


# =========================
# AVISOS ENVIADOS
# =========================

class AvisoEnviado(Base):
    __tablename__ = "avisos_enviados"

    id = Column(Integer, primary_key=True, index=True)
    poliza_id = Column(Integer, ForeignKey("polizas.id"))
    tipo_aviso = Column(Integer, nullable=False)
    fecha_envio = Column(DateTime, default=datetime.utcnow)

    poliza = relationship("Poliza", back_populates="avisos")


# =========================
# RENOVACIONES
# =========================

class Renovacion(Base):
    __tablename__ = "renovaciones"

    id = Column(Integer, primary_key=True, index=True)
    poliza_id = Column(Integer, ForeignKey("polizas.id"))
    anio = Column(Integer, nullable=False)
    prima = Column(Float, nullable=False)
    fecha_renovacion = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# SINIESTROS
# =========================

class Siniestro(Base):
    __tablename__ = "siniestros"

    id = Column(Integer, primary_key=True, index=True)
    poliza_id = Column(Integer, ForeignKey("polizas.id"))
    fecha = Column(Date, nullable=False)
    comunicado_compania = Column(Boolean, default=False)
    num_parte = Column(String, nullable=True)
    descripcion = Column(String, nullable=True)
    acciones = Column(String, nullable=True)
    finalizado = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)∫
