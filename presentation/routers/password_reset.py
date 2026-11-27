import os

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from application.services.password_reset_service import (
    InvalidResetToken, PasswordResetService, RateLimitExceeded, WeakPassword,
)
from infrastructure.repositories.password_reset_repository import SqlAlchemyPasswordResetRepository
from infrastructure.security.email_sender import build_link, delivery_mode, get_email_sender
from infrastructure.security.password_policy import hash_password, validate_password
from infrastructure.security.rate_limiter import RateLimiter
from presentation.dependencies import get_db
from presentation.schemas.dtos.password_reset import (
    PasswordResetConfirmDTO, PasswordResetConfirmResponse,
    PasswordResetRequestDTO, PasswordResetRequestResponse,
)

router = APIRouter(prefix="/auth/password-reset", tags=["Recuperación de contraseña"])

# 5 intentos por ventana de 15 min (configurable).
_limiter = RateLimiter(int(os.getenv("RESET_MAX_ATTEMPTS", "5")), int(os.getenv("RESET_WINDOW_SECONDS", "900")))


def get_limiter() -> RateLimiter:
    return _limiter


def get_service(db: Session = Depends(get_db), limiter: RateLimiter = Depends(get_limiter)) -> PasswordResetService:
    return PasswordResetService(
        repo=SqlAlchemyPasswordResetRepository(db), email_sender=get_email_sender(), limiter=limiter,
        hash_password=hash_password, validate_password=validate_password, build_link=build_link,
        expose_link=delivery_mode() == "json",
    )


def _ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/request", response_model=PasswordResetRequestResponse, status_code=202)
def request_reset(data: PasswordResetRequestDTO, request: Request,
                  service: PasswordResetService = Depends(get_service)):
    try:
        result = service.request_reset(data.correo, _ip(request))
    except RateLimitExceeded:
        raise HTTPException(429, "Demasiados intentos. Intenta más tarde.", headers={"Retry-After": "900"})
    return PasswordResetRequestResponse(message=result.message, reset_link=result.reset_link)


@router.post("/confirm", response_model=PasswordResetConfirmResponse)
def confirm_reset(data: PasswordResetConfirmDTO, request: Request,
                  service: PasswordResetService = Depends(get_service)):
    try:
        message = service.confirm_reset(data.token, data.nueva_password, _ip(request))
    except RateLimitExceeded:
        raise HTTPException(429, "Demasiados intentos. Intenta más tarde.", headers={"Retry-After": "900"})
    except InvalidResetToken:
        raise HTTPException(400, "El enlace de recuperación no es válido o ya expiró.")
    except WeakPassword as exc:
        raise HTTPException(400, str(exc))
    return PasswordResetConfirmResponse(message=message)
