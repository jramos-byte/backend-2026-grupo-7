import pytest
from pydantic import ValidationError
from presentation.schemas.dtos.auth import (
    RegistroRequest,
    LoginRequest,
    UsuarioResponse,
)


def test_registro_valido():
    usuario = RegistroRequest(
        correo="test@example.com",
        password="Veterinaria123",
    )

    assert usuario.correo == "test@example.com"


def test_correo_invalido():
    with pytest.raises(ValidationError):
        RegistroRequest(
            correo="correo_invalido",
            password="Veterinaria123",
        )


def test_password_corta():
    with pytest.raises(ValidationError):
        RegistroRequest(
            correo="test@example.com",
            password="1234",
        )


def test_registro_no_permite_asignar_rol():
    with pytest.raises(ValidationError):
        RegistroRequest(
            correo="test@example.com",
            password="Veterinaria123",
            rol="admin",
        )


def test_login_valido():
    login = LoginRequest(
        correo="test@example.com",
        password="Veterinaria123",
    )

    assert login.correo == "test@example.com"


def test_login_password_vacia():
    with pytest.raises(ValidationError):
        LoginRequest(
            correo="test@example.com",
            password="",
        )


def test_usuario_no_expone_password():
    usuario = UsuarioResponse(
        id=1,
        correo="test@example.com",
        rol="usuario",
        activo=True,
        password_hash="hash_de_prueba",
    )

    datos = usuario.model_dump()

    assert "password" not in datos
    assert "password_hash" not in datos
