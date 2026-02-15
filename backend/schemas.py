from pydantic import BaseModel
from datetime import date

class PolizaBase(BaseModel):
    compania: str
    bien: str
    precio: float
    fecha_vencimiento: date
    email_contacto: str

class PolizaCreate(PolizaBase):
    pass

class Poliza(PolizaBase):
    id: int
    notificacion_enviada: bool

    class Config:
        from_attributes = True
