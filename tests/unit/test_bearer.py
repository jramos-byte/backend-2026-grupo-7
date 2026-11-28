import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

@pytest.fixture
def auth(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "clave-de-pruebas-bearer-" * 2)

    from infrastructure.security import jwt as jwt_security

    monkeypatch.setattr(
        jwt_security,
        "JWT_SECRET",
        "clave-de-pruebas-bearer-" * 2,
    )

    from presentation.dependencies import get_token_payload

    return get_token_payload, jwt_security.create_access_token


def test_bearer_sin_credenciales(auth):
    get_token_payload, _ = auth

    with pytest.raises(HTTPException) as exc:
        get_token_payload(None)

    assert exc.value.status_code == 401


def test_bearer_token_invalido(auth):
    get_token_payload, _ = auth

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="token.invalido.falso",
    )

    with pytest.raises(HTTPException) as exc:
        get_token_payload(credentials)

    assert exc.value.status_code == 401


def test_bearer_token_valido(auth):
    get_token_payload, create_access_token = auth

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=create_access_token(1),
    )

    payload = get_token_payload(credentials)

    assert payload["sub"] == "1"
    assert payload["type"] == "access"
