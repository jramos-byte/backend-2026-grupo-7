from fastapi import APIRouter, Depends, Query, Response, status

from application.services.pet_service import PetServicio
from presentation.dependencies import get_pet_service
from presentation.schemas.dtos.schemas import MascotaCreate, MascotaResponse, Page

router = APIRouter(prefix="/pets", tags=["Mascotas"])


@router.post("", response_model=MascotaResponse, status_code=status.HTTP_201_CREATED)
def create_pet(
    payload: MascotaCreate,
    pet_service: PetServicio = Depends(get_pet_service),
):
    return pet_service.crear_pet(payload)


@router.get("", response_model=Page[MascotaResponse])
def list_pets(
    especie: str | None = None,
    q: str | None = Query(None, description="Busca por nombre o raza"),
    sort_by: str = Query("id", pattern="^(id|nombre|especie|raza|peso_kg)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    pet_service: PetServicio = Depends(get_pet_service),
):
    return pet_service.lista_pets(
        especie=especie, q=q, sort_by=sort_by, order=order, skip=skip, limit=limit
    )


@router.get("/{pet_id}", response_model=MascotaResponse)
def get_pet(
    pet_id: int,
    pet_service: PetServicio = Depends(get_pet_service),
):
    return pet_service.obtener_pet(pet_id)


@router.put("/{pet_id}", response_model=MascotaResponse)
def update_pet(
    pet_id: int,
    payload: MascotaCreate,
    pet_service: PetServicio = Depends(get_pet_service),
):
    return pet_service.actualizar_pet(pet_id, payload)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(
    pet_id: int,
    pet_service: PetServicio = Depends(get_pet_service),
):
    pet_service.eliminar_pet(pet_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
