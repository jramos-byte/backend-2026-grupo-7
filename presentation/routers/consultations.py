from fastapi import APIRouter, Depends, Query, Response, status

from application.services.consultation_service import ConsultationServicio
from infrastructure.models.models import EstadoConsulta
from presentation.dependencies import get_consultation_service
from presentation.schemas.dtos.schemas import ConsultaCreate, ConsultaResponse, ConsultaUpdate, Page

router = APIRouter(prefix="/consultations", tags=["Consultas"])


@router.post("", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED)
def create_consultation(
    payload: ConsultaCreate,
    consultation_service: ConsultationServicio = Depends(get_consultation_service),
):
    return consultation_service.crear_consultation(payload)


@router.get("", response_model=Page[ConsultaResponse])
def list_consultations(
    estado: EstadoConsulta | None = None,
    mascota_id: int | None = None,
    estudiante_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    consultation_service: ConsultationServicio = Depends(get_consultation_service),
):
    return consultation_service.lista_consultations(
        estado=estado,
        mascota_id=mascota_id,
        estudiante_id=estudiante_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{consultation_id}", response_model=ConsultaResponse)
def get_consultation(
    consultation_id: int,
    consultation_service: ConsultationServicio = Depends(get_consultation_service),
):
    return consultation_service.obtener_consultation(consultation_id)


@router.patch("/{consultation_id}", response_model=ConsultaResponse)
def update_consultation(
    consultation_id: int,
    payload: ConsultaUpdate,
    consultation_service: ConsultationServicio = Depends(get_consultation_service),
):
    return consultation_service.actualizar_consultation(consultation_id, payload)


@router.delete("/{consultation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consultation(
    consultation_id: int,
    consultation_service: ConsultationServicio = Depends(get_consultation_service),
):
    consultation_service.eliminar_consultation(consultation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
