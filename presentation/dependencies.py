import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from infrastructure.database import SessionLocal
from infrastructure.security.jwt import verify_access_token

bearer_scheme = HTTPBearer(auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Credenciales requeridas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return verify_access_token(credentials.credentials)

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None