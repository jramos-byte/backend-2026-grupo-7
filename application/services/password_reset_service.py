"""Caso de uso: recuperación de contraseña. Sin dependencias de FastAPI ni SQLAlchemy."""
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional, Protocol

from infrastructure.security.reset_token import (
    ResetTokenError, create_reset_token, decode_reset_token,
)

GENERIC_REQUEST_MESSAGE = "Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña."
CONFIRM_OK_MESSAGE = "Contraseña actualizada. Inicia sesión nuevamente."


class RateLimitExceeded(Exception):
    pass


class InvalidResetToken(Exception):
    """Token inválido, expirado, usado o invalidado (mensaje único para no filtrar el motivo)."""


class WeakPassword(Exception):
    pass


class PasswordResetRepository(Protocol):
    def get_user_by_email(self, correo: str): ...
    def get_user_by_id(self, user_id: int): ...
    def invalidate_pending_tokens(self, user_id: int, now: datetime) -> None: ...
    def add_token(self, jti: str, user_id: int, created_at: datetime, expires_at: datetime) -> None: ...
    def get_token(self, jti: str): ...
    def consume_token(self, jti: str, now: datetime) -> bool: ...
    def update_password(self, user_id: int, password_hash: str, now: datetime) -> None: ...
    def revoke_all_sessions(self, user_id: int, now: datetime) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


@dataclass
class RequestResult:
    message: str
    reset_link: Optional[str] = None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PasswordResetService:
    def __init__(self, repo: PasswordResetRepository, email_sender, limiter,
                 hash_password: Callable[[str], str], validate_password: Callable[[str], None],
                 build_link: Callable[[str], str], expose_link: bool = False,
                 clock: Callable[[], datetime] = _utcnow):
        self.repo, self.email_sender, self.limiter = repo, email_sender, limiter
        self.hash_password, self.validate_password = hash_password, validate_password
        self.build_link, self.expose_link, self.clock = build_link, expose_link, clock

    # -- Solicitud --------------------------------------------------------
    def request_reset(self, correo: str, client_ip: str = "unknown") -> RequestResult:
        correo = correo.strip().lower()
        # El límite se aplica exista o no la cuenta: no revela qué correos están registrados.
        if not (self.limiter.allow(f"email:{correo}") and self.limiter.allow(f"ip:{client_ip}")):
            raise RateLimitExceeded()

        user = self.repo.get_user_by_email(correo)
        link = None
        if user is not None and getattr(user, "activo", True):
            now = self.clock()
            now_ts = int(now.replace(tzinfo=timezone.utc).timestamp())
            self.repo.invalidate_pending_tokens(user.id, now)  # solo el último enlace sirve
            token, jti, exp_ts = create_reset_token(user.id, now_ts)
            expires_at = datetime.fromtimestamp(exp_ts, timezone.utc).replace(tzinfo=None)
            self.repo.add_token(jti, user.id, now, expires_at)
            self.repo.commit()
            link = self.build_link(token)
            self.email_sender.send_reset_link(user.correo, link)
        return RequestResult(GENERIC_REQUEST_MESSAGE, link if self.expose_link else None)

    # -- Confirmación -----------------------------------------------------
    def confirm_reset(self, token: str, new_password: str, client_ip: str = "unknown") -> str:
        if not self.limiter.allow(f"confirm-ip:{client_ip}"):
            raise RateLimitExceeded()
        try:
            claims = decode_reset_token(token)
        except ResetTokenError:
            raise InvalidResetToken()

        now = self.clock()
        record = self.repo.get_token(claims.jti)
        # El usuario sale del token firmado Y del registro; deben coincidir (no se acepta
        # ningún id desde el cliente, así no se puede cambiar la clave de otra cuenta).
        if (record is None or record.usuario_id != claims.user_id
                or record.used_at is not None or record.expires_at <= now):
            raise InvalidResetToken()
        user = self.repo.get_user_by_id(claims.user_id)
        if user is None or not getattr(user, "activo", True):
            raise InvalidResetToken()

        # Se valida la política ANTES de consumir: una clave débil no quema el enlace.
        try:
            self.validate_password(new_password)
        except ValueError as exc:
            raise WeakPassword(str(exc))

        new_hash = self.hash_password(new_password)
        try:
            # Consumo atómico (UPDATE ... WHERE used_at IS NULL): dos usos simultáneos
            # no pueden ganar ambos.
            if not self.repo.consume_token(claims.jti, now):
                self.repo.rollback()
                raise InvalidResetToken()
            self.repo.update_password(user.id, new_hash, now)
            self.repo.invalidate_pending_tokens(user.id, now)   # otros permisos de recuperación
            self.repo.revoke_all_sessions(user.id, now)          # refresh tokens
            self.repo.commit()
        except InvalidResetToken:
            raise
        except Exception:
            self.repo.rollback()
            raise
        return CONFIRM_OK_MESSAGE
