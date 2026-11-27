"""JWT de recuperación de contraseña: propósito específico, caducidad e id único."""
import os
import uuid
from dataclasses import dataclass

import jwt

PURPOSE = "password_reset"
ALGORITHM = "HS256"
ISSUER = "clinica-veterinaria-api"


class ResetTokenError(Exception):
    """Token ilegible, con firma inválida, expirado o de otro propósito."""


@dataclass(frozen=True)
class ResetClaims:
    user_id: int
    jti: str
    exp: int


def get_secret() -> str:
    # Secreto DISTINTO al del Access JWT: un access token nunca valida como reset.
    secret = os.getenv("RESET_JWT_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("RESET_JWT_SECRET debe definirse con al menos 32 caracteres.")
    return secret


def get_ttl_seconds() -> int:
    return int(os.getenv("RESET_TOKEN_TTL_MINUTES", "15")) * 60


def create_reset_token(user_id: int, now_ts: int, ttl_seconds: int | None = None,
                       secret: str | None = None, jti: str | None = None) -> tuple[str, str, int]:
    """Devuelve (token, jti, exp_ts)."""
    jti = jti or uuid.uuid4().hex
    exp = now_ts + (ttl_seconds if ttl_seconds is not None else get_ttl_seconds())
    payload = {"sub": str(user_id), "purpose": PURPOSE, "jti": jti,
               "iat": now_ts, "exp": exp, "iss": ISSUER}
    return jwt.encode(payload, secret or get_secret(), algorithm=ALGORITHM), jti, exp


def decode_reset_token(token: str, secret: str | None = None) -> ResetClaims:
    try:
        data = jwt.decode(
            token, secret or get_secret(),
            algorithms=[ALGORITHM],  # lista fija: rechaza alg=none y otros algoritmos
            issuer=ISSUER,
            options={"require": ["exp", "iat", "sub", "jti", "purpose"]},
        )
        if data["purpose"] != PURPOSE:
            raise ResetTokenError("propósito inválido")
        return ResetClaims(user_id=int(data["sub"]), jti=str(data["jti"]), exp=int(data["exp"]))
    except ResetTokenError:
        raise
    except (jwt.PyJWTError, ValueError, TypeError) as exc:
        raise ResetTokenError(str(exc)) from exc
