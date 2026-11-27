"""Repositorio SQLAlchemy de recuperación.

ASUNCIONES sobre modelos de A/B (ajustar nombres si difieren):
  Usuario:       id, correo, password_hash, password_changed_at, activo
  SesionRefresh: usuario_id, revoked_at   (refresh tokens persistidos por B)
Invalidación de ACCESS tokens: B debe rechazar todo access JWT con `iat` anterior a
Usuario.password_changed_at (aquí se actualiza al cambiar la clave).
"""
from datetime import datetime

from sqlalchemy import update, select
from sqlalchemy.orm import Session

from infrastructure.models.password_reset import PasswordResetToken
from infrastructure.models.models import Usuario, SesionRefresh  # definidos por A/B


class SqlAlchemyPasswordResetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, correo: str):
        return self.db.execute(select(Usuario).where(Usuario.correo == correo)).scalar_one_or_none()

    def get_user_by_id(self, user_id: int):
        return self.db.get(Usuario, user_id)

    def invalidate_pending_tokens(self, user_id: int, now: datetime) -> None:
        self.db.execute(update(PasswordResetToken)
                        .where(PasswordResetToken.usuario_id == user_id, PasswordResetToken.used_at.is_(None))
                        .values(used_at=now))

    def add_token(self, jti, user_id, created_at, expires_at) -> None:
        self.db.add(PasswordResetToken(jti=jti, usuario_id=user_id, created_at=created_at, expires_at=expires_at))
        self.db.flush()

    def get_token(self, jti: str):
        return self.db.execute(select(PasswordResetToken).where(PasswordResetToken.jti == jti)).scalar_one_or_none()

    def consume_token(self, jti: str, now: datetime) -> bool:
        res = self.db.execute(update(PasswordResetToken)
                              .where(PasswordResetToken.jti == jti, PasswordResetToken.used_at.is_(None),
                                     PasswordResetToken.expires_at > now)
                              .values(used_at=now))
        return res.rowcount == 1

    def update_password(self, user_id: int, password_hash: str, now: datetime) -> None:
        self.db.execute(update(Usuario).where(Usuario.id == user_id)
                        .values(password_hash=password_hash, password_changed_at=now))

    def revoke_all_sessions(self, user_id: int, now: datetime) -> None:
        self.db.execute(update(SesionRefresh)
                        .where(SesionRefresh.usuario_id == user_id, SesionRefresh.revoked_at.is_(None))
                        .values(revoked_at=now))

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
