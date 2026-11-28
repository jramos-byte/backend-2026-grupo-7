from fastapi import APIRouter, Depends, Query, Response, status

from application.services.student_service import StudentServicio
from presentation.dependencies import get_student_service
from presentation.schemas.dtos.schemas import EstudianteCreate, EstudianteResponse, Page

router = APIRouter(prefix="/students", tags=["Estudiantes"])


@router.post("", response_model=EstudianteResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    payload: EstudianteCreate,
    student_service: StudentServicio = Depends(get_student_service),
):
    return student_service.crear_student(payload)


@router.get("", response_model=Page[EstudianteResponse])
def list_students(
    q: str | None = Query(None, description="Busca por nombre, RUT o correo"),
    anio_ingreso: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    student_service: StudentServicio = Depends(get_student_service),
):
    return student_service.lista_students(q=q, anio_ingreso=anio_ingreso, skip=skip, limit=limit)


@router.get("/{student_id}", response_model=EstudianteResponse)
def get_student(
    student_id: int,
    student_service: StudentServicio = Depends(get_student_service),
):
    return student_service.obtener_student(student_id)


@router.put("/{student_id}", response_model=EstudianteResponse)
def update_student(
    student_id: int,
    payload: EstudianteCreate,
    student_service: StudentServicio = Depends(get_student_service),
):
    return student_service.actualizar_student(student_id, payload)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    student_service: StudentServicio = Depends(get_student_service),
):
    student_service.eliminar_student(student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
