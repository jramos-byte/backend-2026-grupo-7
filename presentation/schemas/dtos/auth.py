from pydantic import BaseModel, EmailStr, Field, ConfigDict

class RegistroRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    correo: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    correo: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    correo: EmailStr
    rol: str
    activo: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MensajeResponse(BaseModel):
    mensaje: str
