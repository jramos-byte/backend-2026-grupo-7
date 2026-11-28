
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError, VerificationError


hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)

def validar_password(password: str) -> None:
    if len(password) < 12:
        raise ValueError(
            "La contraseña debe tener al menos 12 caracteres."
        )

    if len(password) > 128:
        raise ValueError(
            "La contraseña no puede superar los 128 caracteres."
        )


def hash_password(password: str) -> str:
    validar_password(password)
    return hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False
