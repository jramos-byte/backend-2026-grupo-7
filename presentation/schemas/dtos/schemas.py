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

#----Esquema para los dueños-----

class DuenoBase(BaseModel):
    rut: str = Field(..., min_length=9, max_length=12)
    nombre_completo: str = Field(..., min_length=3, max_length=100)
    telefono: str = Field(..., min_length=7, max_length=20)
    direccion: str = Field(..., min_length=5, max_length=200)

class DuenoCreate(DuenoBase):
    pass

class DuenoResponse(DuenoBase):
    id: int

    class Config:
        from_attributes = True

#----Esquema para las mascotas-----

class MascotaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    especie: str = Field(..., min_length=2, max_length=50)
    raza: str = Field(..., min_length=2, max_length=50)
    peso_kg: float = Field(..., gt=0)
    dueño_id: int

class MascotaCreate(MascotaBase):
    pass

class MascotaResponse(MascotaBase):
    id: int

    class Config:
        from_attributes = True