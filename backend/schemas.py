from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional


# =========================
# POLIZA BASE
# =========================

class PolizaBase(BaseModel):
    compania: str
    contacto_compania: Optional[str] = None
    telefono_compania: Optional[str] = None
    tipo: str
    bien: str
    numero_poliza: str
    prima: float
    fecha_inicio: date
    fecha_vencimiento: date
    estado: Optional[str] = "activa"


# =========================
# CREAR POLIZA
# =========================

class PolizaCreate(PolizaBase):
    pass


# =========================
# RENOVACION
# =========================

class RenovacionBase(BaseModel):
    anio: int
    prima: float
    fecha_renovacion: date


class RenovacionCreate(RenovacionBase):
    poliza_id: int


class Renovacion(RenovacionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# SINIESTRO
# =========================

class SiniestroBase(BaseModel):
    fecha: date
    comunicado_compania: Optional[bool] = False
    numero_parte: Optional[str] = None
    descripcion: str
    acciones_realizadas: Optional[str] = None
    finalizado: Optional[bool] = False


class SiniestroCreate(SiniestroBase):
    poliza_id: int


class Siniestro(SiniestroBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# POLIZA RESPONSE
# =========================

class Poliza(PolizaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    renovaciones: List[Renovacion] = []
    siniestros: List[Siniestro] = []

    class Config:
        from_attributes = True
