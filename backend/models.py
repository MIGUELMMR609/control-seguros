from sqlalchemy import Column, Integer, String, Float, Boolean, Date
from backend.database import Base


class Poliza(Base):
    __tablename__ = "polizas"

    id = Column(Integer, primary_key=True, index=True)
    compania = Column(String, nullable=False)
    bien = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    email_contacto = Column(String, nullable=False)
    notificacion_enviada = Column(Boolean, default=False)
