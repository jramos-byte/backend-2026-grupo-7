from datetime import datetime, timezone
from infrastructure.security.refresh import (
    create_refresh_token,
    hash_refresh_token,
    get_refresh_expiration,
    REFRESH_TOKEN_DAYS,
)


def test_refresh_token_generado():
    token = create_refresh_token()

    assert isinstance(token, str)
    assert len(token) >= 43


def test_refresh_tokens_diferentes():
    token1 = create_refresh_token()
    token2 = create_refresh_token()

    assert token1 != token2


def test_hash_refresh_token():
    token = create_refresh_token()
    token_hash = hash_refresh_token(token)

    assert token_hash != token
    assert len(token_hash) == 64


def test_hash_consistente():
    token = create_refresh_token()

    assert hash_refresh_token(token) == hash_refresh_token(token)


def test_hash_tokens_diferentes():
    token1 = create_refresh_token()
    token2 = create_refresh_token()

    assert hash_refresh_token(token1) != hash_refresh_token(token2)


def test_expiracion_refresh():
    ahora = datetime.now(timezone.utc)
    expiracion = get_refresh_expiration()

    diferencia = (expiracion - ahora).total_seconds()
    esperado = REFRESH_TOKEN_DAYS * 86400

    assert abs(diferencia - esperado) < 1
