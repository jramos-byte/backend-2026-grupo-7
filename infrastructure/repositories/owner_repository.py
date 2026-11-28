from sqlalchemy import or_
from sqlalchemy.orm import Session
from infrastructure.models.models import Dueno


class OwnerRepo:
    def __init__(self, db: Session):
        self.db = db

    def crear_owner(self, owner: Dueno) -> Dueno:
        self.db.add(owner)
        self.db.commit()
        self.db.refresh(owner)
        return owner

    def lista_paginada(self, q: str | None, skip: int, limit: int) -> tuple[list[Dueno], int]:
        query = self.db.query(Dueno)
        if q:
            term = f"%{q}%"
            query = query.filter(or_(Dueno.nombre_completo.ilike(term), Dueno.rut.ilike(term)))
        total = query.count()
        items = query.order_by(Dueno.id).offset(skip).limit(limit).all()
        return items, total

    def obtener_por_id(self, owner_id: int) -> Dueno | None:
        return self.db.query(Dueno).filter(Dueno.id == owner_id).first()

    def actualizar(self, owner: Dueno) -> Dueno:
        self.db.commit()
        self.db.refresh(owner)
        return owner

    def eliminar(self, owner: Dueno) -> None:
        self.db.delete(owner)
        self.db.commit()
