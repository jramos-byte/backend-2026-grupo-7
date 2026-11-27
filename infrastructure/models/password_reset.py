"""Permisos de recuperación (un registro por JWT emitido). Migración: la crea A.

Depende de la tabla `usuarios` (A/B).
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from infrastructure.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    jti = Column(String(64), unique=True, nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)   # UTC naive
    expires_at = Column(DateTime, nullable=False)   # UTC naive
    used_at = Column(DateTime, nullable=True)       # uso o invalidación (NULL = vigente)
