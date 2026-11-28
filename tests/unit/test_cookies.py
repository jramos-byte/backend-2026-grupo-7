from fastapi import Response
from presentation.security import cookies

def test_crear_refresh_cookie():
    response = Response()

    cookies.set_refresh_cookie(response, "token_prueba")

    header = response.headers["set-cookie"]

    assert "refresh_token=token_prueba" in header


def test_cookie_httponly():
    response = Response()

    cookies.set_refresh_cookie(response, "token_prueba")

    assert "HttpOnly" in response.headers["set-cookie"]


def test_cookie_secure(monkeypatch):
    monkeypatch.setattr(cookies, "COOKIE_SECURE", True)

    response = Response()
    cookies.set_refresh_cookie(response, "token_prueba")

    assert "Secure" in response.headers["set-cookie"]


def test_cookie_samesite(monkeypatch):
    monkeypatch.setattr(cookies, "COOKIE_SAMESITE", "lax")

    response = Response()
    cookies.set_refresh_cookie(response, "token_prueba")

    assert "samesite=lax" in response.headers["set-cookie"].lower()


def test_cookie_path():
    response = Response()

    cookies.set_refresh_cookie(response, "token_prueba")

    assert "Path=/auth" in response.headers["set-cookie"]


def test_cookie_expiracion():
    response = Response()

    cookies.set_refresh_cookie(response, "token_prueba")

    segundos = cookies.REFRESH_TOKEN_DAYS * 86400

    assert f"Max-Age={segundos}" in response.headers["set-cookie"]


def test_eliminar_cookie():
    response = Response()

    cookies.delete_refresh_cookie(response)

    assert "Max-Age=0" in response.headers["set-cookie"]
