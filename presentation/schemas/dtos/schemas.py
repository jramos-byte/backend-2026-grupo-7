from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from infrastructure.models.models import EstadoConsulta

class EstudianteBase(BaseModel):
    rut: str = Field(..., min_length=9, max_length=12)
    nombre_completo: str = Field(..., min_length=3, max_length=100)
    correo: EmailStr
    anio_ingreso: int = Field(..., ge=2010, le=2026)

class EstudianteCreate(EstudianteBase):
    pass

class EstudianteResponse(EstudianteBase):
    id: int

    class Config:
        from_attributes = True

class ConsultaBase(BaseModel):
    fecha_hora: datetime
    motivo: str = Field(..., min_length=10, max_length=255)
    diagnostico: Optional[str] = Field(None, max_length=255)
    estado: EstadoConsulta = EstadoConsulta.PENDIENTE
    mascota_id: int
    estudiante_id: int

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaResponse(ConsultaBase):
    id: int

    class Config:
        from_attributes = True