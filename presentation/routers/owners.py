from fastapi import APIRouter, Depends, Query, Response, status

from application.services.owner_service import OwnerServicio
from presentation.dependencies import get_owner_service
from presentation.schemas.dtos.schemas import DuenoCreate, DuenoResponse, Page

router = APIRouter(prefix="/owners", tags=["Duenos"])


@router.post("", response_model=DuenoResponse, status_code=status.HTTP_201_CREATED)
def create_owner(payload: DuenoCreate, owner_service: OwnerServicio = Depends(get_owner_service)):
    return owner_service.crear_owner(payload)


@router.get("", response_model=Page[DuenoResponse])
def list_owners(
    q: str | None = Query(None, description="Busca por nombre o RUT"),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    owner_service: OwnerServicio = Depends(get_owner_service),
):
    return owner_service.lista_owners(q=q, skip=skip, limit=limit)


@router.get("/{owner_id}", response_model=DuenoResponse)
def get_owner(owner_id: int, owner_service: OwnerServicio = Depends(get_owner_service)):
    return owner_service.obtener_owner(owner_id)


@router.put("/{owner_id}", response_model=DuenoResponse)
def update_owner(owner_id: int, payload: DuenoCreate, owner_service: OwnerServicio = Depends(get_owner_service)):
    return owner_service.actualizar_owner(owner_id, payload)


@router.delete("/{owner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_owner(owner_id: int, owner_service: OwnerServicio = Depends(get_owner_service)):
    owner_service.eliminar_owner(owner_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
