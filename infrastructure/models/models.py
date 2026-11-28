from datetime import datetime
import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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


class Rol(Base):
    __tablename__ = "rol"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    usuarios = relationship("Usuario", back_populates="role")


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("rol.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    role = relationship("Rol", back_populates="usuarios")
    sessions = relationship("SessionUsuario", back_populates="usuario", cascade="all, delete-orphan")
    recovery_tokens = relationship("RecuperacionContrasena", back_populates="usuario", cascade="all, delete-orphan")


class SessionUsuario(Base):
    __tablename__ = "sesiones_de_usuario"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    refresh_token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="sessions")


class RecuperacionContrasena(Base):
    __tablename__ = "recuperacion_contrasena"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    usuario = relationship("Usuario", back_populates="recovery_tokens")
