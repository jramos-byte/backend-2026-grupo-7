import pytest
from fastapi import Request, HTTPException
from presentation.security import csrf

@pytest.fixture
def allowed_origins(monkeypatch):
    monkeypatch.setattr(
        csrf,
        "ALLOWED_ORIGINS",
        ["http://localhost:8000"],
    )


def crear_request(origin=None):
    headers = []

    if origin is not None:
        headers.append(
            (b"origin", origin.encode())
        )

    return Request({
        "type": "http",
        "headers": headers,
    })


def test_origen_permitido(allowed_origins):
    request = crear_request("http://localhost:8000")

    assert csrf.validate_origin(request) is None


def test_origen_no_permitido(allowed_origins):
    request = crear_request("https://example.com")

    with pytest.raises(HTTPException) as exc:
        csrf.validate_origin(request)

    assert exc.value.status_code == 403


def test_solicitud_sin_origen(allowed_origins):
    request = crear_request()

    with pytest.raises(HTTPException) as exc:
        csrf.validate_origin(request)

    assert exc.value.status_code == 403


def test_origen_similar_no_permitido(allowed_origins):
    request = crear_request("http://localhost:8001")

    with pytest.raises(HTTPException) as exc:
        csrf.validate_origin(request)

    assert exc.value.status_code == 403
