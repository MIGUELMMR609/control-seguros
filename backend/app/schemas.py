from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


# =========================
# POLIZA
# =========================

class PolizaBase(BaseModel):
    compania_id: Optional[int] = None
    tipo_id: Optional[int] = None
    contacto_compania: Optional[str] = None
    telefono_compania: Optional[str] = None
    bien: str
    numero_poliza: str
    prima: float
    fecha_inicio: date
    fecha_vencimiento: date
    estado: str = "activa"


class PolizaCreate(PolizaBase):
    pass


class PolizaResponse(PolizaBase):
    id: int
    aviso_enviado: bool
    created_at: datetime
    updated_at: datetime
    dias_restantes: Optional[int] = None

    class Config:
        from_attributes = True


# =========================
# RENOVACION
# =========================

class RenovacionBase(BaseModel):
    poliza_id: int
    anio: int
    prima: float
    fecha_renovacion: date


class RenovacionCreate(RenovacionBase):
    pass


class RenovacionResponse(RenovacionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# SINIESTRO
# =========================

class SiniestroBase(BaseModel):
    poliza_id: int
    fecha: date
    comunicado_compania: bool = False
    num_parte: Optional[str] = None
    descripcion: Optional[str] = None
    acciones: Optional[str] = None
    finalizado: bool = False


class SiniestroCreate(SiniestroBase):
    pass


class SiniestroResponse(SiniestroBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
