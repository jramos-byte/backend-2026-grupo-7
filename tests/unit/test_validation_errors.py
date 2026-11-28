import asyncio
import json
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from app.main import validation_exception_handler


def test_error_no_expone_password():
    password = "password_de_prueba"

    exc = RequestValidationError([
        {
            "type": "string_too_short",
            "loc": ("body", "password"),
            "msg": "Contrasena invalida",
            "input": password,
        }
    ])

    request = Request({
        "type": "http",
        "headers": [],
    })

    response = asyncio.run(
        validation_exception_handler(request, exc)
    )

    datos = json.loads(response.body)

    assert response.status_code == 422
    assert password not in response.body.decode()
    assert datos["error"]["code"] == "VALIDATION_ERROR"
    assert "input" not in datos["error"]["details"][0]
