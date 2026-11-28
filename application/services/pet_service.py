from fastapi import HTTPException
from infrastructure.models.models import Mascota
from infrastructure.repositories.owner_repository import OwnerRepo
from infrastructure.repositories.pet_repository import PetRepo
from presentation.schemas.dtos.schemas import MascotaCreate


class PetServicio:
    def __init__(self, pet_repo: PetRepo, owner_repo: OwnerRepo):
        self.pet_repo = pet_repo
        self.owner_repo = owner_repo

    def crear_pet(self, payload: MascotaCreate) -> Mascota:
        if self.owner_repo.obtener_por_id(payload.dueno_id) is None:
            raise HTTPException(status_code=404, detail="Dueño asociado no encontrado")
        pet = Mascota(**payload.model_dump())
        return self.pet_repo.crear_pet(pet)

    def lista_pets(
        self,
        especie: str | None,
        q: str | None,
        sort_by: str,
        order: str,
        skip: int,
        limit: int,
    ) -> dict:
        items, total = self.pet_repo.lista_paginada(
            especie=especie, q=q, sort_by=sort_by, order=order, skip=skip, limit=limit
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}

    def obtener_pet(self, pet_id: int) -> Mascota:
        pet = self.pet_repo.obtener_por_id(pet_id)
        if pet is None:
            raise HTTPException(status_code=404, detail="Mascota no encontrada")
        return pet

    def actualizar_pet(self, pet_id: int, payload: MascotaCreate) -> Mascota:
        pet = self.obtener_pet(pet_id)
        if self.owner_repo.obtener_por_id(payload.dueno_id) is None:
            raise HTTPException(status_code=404, detail="Dueño asociado no encontrado")
        for key, value in payload.model_dump().items():
            setattr(pet, key, value)
        return self.pet_repo.actualizar(pet)

    def eliminar_pet(self, pet_id: int) -> None:
        pet = self.obtener_pet(pet_id)
        self.pet_repo.eliminar(pet)
