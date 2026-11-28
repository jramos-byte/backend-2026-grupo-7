import os
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(
    os.getenv("ACCESS_TOKEN_MINUTES", "15")
)

if not JWT_SECRET or len(JWT_SECRET.encode()) < 32:
    raise RuntimeError("JWT_SECRET no configurado o insuficiente")


def create_access_token(
    user_id: int,
    token_version: int = 0
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
        "jti": str(uuid4()),
        "version": token_version,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def verify_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        options={
            "require": [
                "sub", "type", "iat",
                "exp", "jti", "version"
            ]
        }
    )

    if payload["type"] != "access":
        raise jwt.InvalidTokenError(
            "Proposito del token invalido"
        )

    if not payload["sub"].isdigit():
        raise jwt.InvalidTokenError(
            "Usuario invalido"
        )

    return payload
