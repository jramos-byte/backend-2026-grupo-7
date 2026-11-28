import pytest
from infrastructure.security.password import (
    hash_password,
    verify_password,
    validar_password,
)


PASSWORD = "Veterinaria123"


def test_hash_argon2id():
    password_hash = hash_password(PASSWORD)

    assert password_hash.startswith("$argon2id$")
    assert password_hash != PASSWORD


def test_password_correcta():
    password_hash = hash_password(PASSWORD)

    assert verify_password(PASSWORD, password_hash) is True


def test_password_incorrecta():
    password_hash = hash_password(PASSWORD)

    assert verify_password("incorrecta", password_hash) is False


def test_password_corta():
    with pytest.raises(ValueError):
        hash_password("1234")


def test_password_longitud_minima():
    assert validar_password("123456789012") is None


def test_salt_aleatorio():
    hash1 = hash_password(PASSWORD)
    hash2 = hash_password(PASSWORD)

    assert hash1 != hash2

def test_password_longitud_maxima():
    assert validar_password("a" * 128) is None


def test_password_demasiado_larga():
    with pytest.raises(ValueError):
        validar_password("a" * 129)
