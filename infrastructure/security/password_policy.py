"""Política de contraseñas y hashing (Argon2id).

COMPARTIDO con el integrante B: registro y recuperación deben usar exactamente
esta política y este hashing. Si B ya tiene su versión en infrastructure/security/,
conservar una sola y borrar la otra.
"""
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128


class PasswordPolicyError(ValueError):
    pass


def validate_password(password: str) -> None:
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise PasswordPolicyError(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres.")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise PasswordPolicyError(f"La contraseña no puede superar {MAX_PASSWORD_LENGTH} caracteres.")


def hash_password(password: str) -> str:
    from argon2 import PasswordHasher  # argon2-cffi usa Argon2id por defecto

    return PasswordHasher().hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerificationError

    try:
        return PasswordHasher().verify(password_hash, password)
    except VerificationError:
        return False
