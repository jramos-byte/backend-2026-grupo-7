from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from infrastructure.models.models import EstadoConsulta


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int


class EstudianteBase(BaseModel):
    rut: str = Field(..., min_length=9, max_length=12)
    nombre_completo: str = Field(..., min_length=3, max_length=100)
    correo: EmailStr = Field(..., max_length=100)
    anio_ingreso: int = Field(..., ge=2010)

    @field_validator("anio_ingreso")
    @classmethod
    def validate_entry_year(cls, value: int) -> int:
        if value > datetime.now().year:
            raise ValueError("El año de ingreso no puede estar en el futuro")
        return value


class EstudianteCreate(EstudianteBase):
    pass


class EstudianteResponse(EstudianteBase, ORMModel):
    id: int


class DuenoBase(BaseModel):
    rut: str = Field(..., min_length=9, max_length=12)
    nombre_completo: str = Field(..., min_length=3, max_length=100)
    telefono: str = Field(..., min_length=8, max_length=20)
    direccion: str = Field(..., min_length=5, max_length=200)


class DuenoCreate(DuenoBase):
    pass


class DuenoResponse(DuenoBase, ORMModel):
    id: int


class MascotaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    especie: str = Field(..., min_length=3, max_length=50)
    raza: str = Field(..., min_length=3, max_length=50)
    peso_kg: float = Field(..., gt=0.0)
    dueno_id: int = Field(..., gt=0)


class MascotaCreate(MascotaBase):
    pass


class MascotaResponse(MascotaBase, ORMModel):
    id: int


class ConsultaBase(BaseModel):
    fecha_hora: datetime
    motivo: str = Field(..., min_length=10, max_length=255)
    diagnostico: str | None = Field(None, max_length=255)
    estado: EstadoConsulta = EstadoConsulta.PENDIENTE
    mascota_id: int = Field(..., gt=0)
    estudiante_id: int = Field(..., gt=0)


class ConsultaCreate(ConsultaBase):
    pass


class ConsultaUpdate(BaseModel):
    fecha_hora: datetime | None = None
    motivo: str | None = Field(None, min_length=10, max_length=255)
    diagnostico: str | None = Field(None, max_length=255)
    estado: EstadoConsulta | None = None
    mascota_id: int | None = Field(None, gt=0)
    estudiante_id: int | None = Field(None, gt=0)


class ConsultaResponse(ConsultaBase, ORMModel):
    id: int
