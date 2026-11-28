from sqlalchemy.orm import Session
from infrastructure.models.models import Mascota


class PetRepo:
    def __init__(self, db: Session):
        self.db = db

    def crear_pet(self, pet: Mascota) -> Mascota:
        self.db.add(pet)
        self.db.commit()
        self.db.refresh(pet)
        return pet

    def lista_paginada(
        self,
        especie: str | None,
        q: str | None,
        sort_by: str,
        order: str,
        skip: int,
        limit: int,
    ) -> tuple[list[Mascota], int]:
        query = self.db.query(Mascota)
        if especie:
            query = query.filter(Mascota.especie.ilike(especie))
        if q:
            term = f"%{q}%"
            query = query.filter(Mascota.nombre.ilike(term) | Mascota.raza.ilike(term))
        total = query.count()
        column = getattr(Mascota, sort_by)
        column = column.desc() if order == "desc" else column.asc()
        items = query.order_by(column).offset(skip).limit(limit).all()
        return items, total

    def obtener_por_id(self, pet_id: int) -> Mascota | None:
        return self.db.get(Mascota, pet_id)

    def actualizar(self, pet: Mascota) -> Mascota:
        self.db.commit()
        self.db.refresh(pet)
        return pet

    def eliminar(self, pet: Mascota) -> None:
        self.db.delete(pet)
        self.db.commit()
