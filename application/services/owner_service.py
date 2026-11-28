from fastapi import HTTPException
from infrastructure.models.models import Dueno
from infrastructure.repositories.owner_repository import OwnerRepo
from presentation.schemas.dtos.schemas import DuenoCreate


class OwnerServicio:
    def __init__(self, owner_repo: OwnerRepo):
        self.owner_repo = owner_repo

    def crear_owner(self, payload: DuenoCreate) -> Dueno:
        owner = Dueno(**payload.model_dump())
        return self.owner_repo.crear_owner(owner)

    def lista_owners(self, q: str | None, skip: int, limit: int) -> dict:
        items, total = self.owner_repo.lista_paginada(q=q, skip=skip, limit=limit)
        return {"items": items, "total": total, "skip": skip, "limit": limit}

    def obtener_owner(self, owner_id: int) -> Dueno:
        owner = self.owner_repo.obtener_por_id(owner_id)
        if owner is None:
            raise HTTPException(status_code=404, detail="Owner no encontrado")
        return owner

    def actualizar_owner(self, owner_id: int, payload: DuenoCreate) -> Dueno:
        owner = self.obtener_owner(owner_id)
        for key, value in payload.model_dump().items():
            setattr(owner, key, value)
        return self.owner_repo.actualizar(owner)

    def eliminar_owner(self, owner_id: int) -> None:
        owner = self.obtener_owner(owner_id)
        self.owner_repo.eliminar(owner)
