import importlib
import sys
import jwt
import pytest


@pytest.fixture
def jwt_module(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "clave-exclusiva-de-pruebas-" * 2)
    monkeypatch.setenv("ACCESS_TOKEN_MINUTES", "15")

    monkeypatch.delitem(
        sys.modules,
        "infrastructure.security.jwt",
        raising=False,
    )

    return importlib.import_module("infrastructure.security.jwt")


def test_create_access_token(jwt_module):
    token = jwt_module.create_access_token(1)

    assert isinstance(token, str)
    assert len(token.split(".")) == 3


def test_verify_access_token(jwt_module):
    token = jwt_module.create_access_token(1)
    payload = jwt_module.verify_access_token(token)

    assert payload["sub"] == "1"
    assert payload["type"] == "access"
    assert payload["version"] == 0


def test_token_expirado(jwt_module):
    payload = jwt_module.verify_access_token(
        jwt_module.create_access_token(1)
    )

    payload["iat"] = 1
    payload["exp"] = 2

    token = jwt.encode(
        payload,
        jwt_module.JWT_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt_module.verify_access_token(token)


def test_token_invalido(jwt_module):
    with pytest.raises(jwt.InvalidTokenError):
        jwt_module.verify_access_token("token.invalido.falso")


def test_proposito_incorrecto(jwt_module):
    payload = jwt_module.verify_access_token(
        jwt_module.create_access_token(1)
    )

    payload["type"] = "reset"

    token = jwt.encode(
        payload,
        jwt_module.JWT_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(jwt.InvalidTokenError):
        jwt_module.verify_access_token(token)


def test_firma_invalida(jwt_module):
    payload = jwt_module.verify_access_token(
        jwt_module.create_access_token(1)
    )

    token = jwt.encode(
        payload,
        "clave-incorrecta-exclusiva-de-pruebas",
        algorithm="HS256",
    )

    with pytest.raises(jwt.InvalidSignatureError):
        jwt_module.verify_access_token(token)


def test_version_token(jwt_module):
    token = jwt_module.create_access_token(1, token_version=3)
    payload = jwt_module.verify_access_token(token)

    assert payload["version"] == 3
