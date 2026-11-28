import hashlib
import secrets
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

REFRESH_TOKEN_DAYS = int(
    os.getenv("REFRESH_TOKEN_DAYS", "7")
)

if REFRESH_TOKEN_DAYS <= 0:
    raise ValueError("Duracion del refresh token invalida")


def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_refresh_expiration() -> datetime:
    return datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_DAYS
    )
