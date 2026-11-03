from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from presentation.routers.consultations import router as consultations_router
from presentation.routers.owners import router as owners_router
from presentation.routers.pets import router as pets_router
from presentation.routers.students import router as students_router

app = FastAPI(
    title="API Clínica Veterinaria",
    description=(
        "API para administrar estudiantes veterinarios, dueños, mascotas y "
        "consultas. Incluye validaciones y reglas de negocio."
    ),
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": "Los datos enviados no son válidos.", "details": jsonable_encoder(exc.errors())}},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    messages = {400: "BUSINESS_RULE_VIOLATION", 404: "NOT_FOUND", 409: "CONFLICT"}
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={"error": {"code": messages.get(exc.status_code, "HTTP_ERROR"), "message": str(exc.detail), "details": None}},
    )


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"error": {"code": "INTEGRITY_CONFLICT", "message": "El registro entra en conflicto con datos existentes o relaciones requeridas.", "details": None}},
    )


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok", "service": "API Clínica Veterinaria"}


app.include_router(students_router, prefix="/api/v1")
app.include_router(owners_router, prefix="/api/v1")
app.include_router(pets_router, prefix="/api/v1")
app.include_router(consultations_router, prefix="/api/v1")
