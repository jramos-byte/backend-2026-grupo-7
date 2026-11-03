from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from infrastructure.database import Base

class EstadoConsulta(enum.Enum):
    PENDIENTE = "pendiente"
    REALIZADA = "realizada"
    CANCELADA = "cancelada"

class Estudiante(Base):
    __tablename__ = "estudiantes"
    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(12), unique=True, nullable=False)
    nombre_completo = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    anio_ingreso = Column(Integer, nullable=False)
    consultas = relationship("Consulta", back_populates="estudiante")

class Dueno(Base):
    __tablename__ = "duenos"
    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(12), unique=True, nullable=False)
    nombre_completo = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=False)
    direccion = Column(String(200), nullable=False)
    mascotas = relationship("Mascota", back_populates="dueno")

class Mascota(Base):
    __tablename__ = "mascotas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    especie = Column(String(50), nullable=False)
    raza = Column(String(50), nullable=False)
    peso_kg = Column(Float, nullable=False)
    # El nombre de la columna se conserva para no romper la migración existente;
    # el atributo Python y el contrato HTTP usan ASCII.
    dueno_id = Column("dueño_id", Integer, ForeignKey("duenos.id"), nullable=False)
    dueno = relationship("Dueno", back_populates="mascotas")
    consultas = relationship("Consulta", back_populates="mascota")

class Consulta(Base):
    __tablename__ = "consultas"
    id = Column(Integer, primary_key=True, index=True)
    fecha_hora = Column(DateTime, nullable=False)
    motivo = Column(String(255), nullable=False)
    diagnostico = Column(String(255), nullable=True)
    estado = Column(Enum(EstadoConsulta), default=EstadoConsulta.PENDIENTE)
    mascota_id = Column(Integer, ForeignKey("mascotas.id"), nullable=False)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"), nullable=False)
    mascota = relationship("Mascota", back_populates="consultas")
    estudiante = relationship("Estudiante", back_populates="consultas")
