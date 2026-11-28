import os
from fastapi import Response
from dotenv import load_dotenv
from infrastructure.security.refresh import REFRESH_TOKEN_DAYS

load_dotenv()

COOKIE_NAME = "refresh_token"

COOKIE_SECURE = (
    os.getenv("COOKIE_SECURE", "true").lower() == "true"
)

COOKIE_SAMESITE = os.getenv(
    "COOKIE_SAMESITE", "lax"
).lower()

COOKIE_PATH = "/auth"

if COOKIE_SAMESITE not in ("strict", "lax", "none"):
    raise ValueError("Configuracion SameSite invalida")

if COOKIE_SAMESITE == "none" and not COOKIE_SECURE:
    raise ValueError("SameSite none requiere cookies seguras")


def set_refresh_cookie(
    response: Response,
    token: str
) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=REFRESH_TOKEN_DAYS * 86400,
        path=COOKIE_PATH,
    )


def delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=COOKIE_NAME,
        path=COOKIE_PATH,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
    )
