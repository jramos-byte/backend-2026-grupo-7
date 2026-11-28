from sqlalchemy.orm import Session
from infrastructure.models.models import Consulta, EstadoConsulta


class ConsultationRepo:
    def __init__(self, db: Session):
        self.db = db

    def crear_consultation(self, consultation: Consulta) -> Consulta:
        self.db.add(consultation)
        self.db.commit()
        self.db.refresh(consultation)
        return consultation

    def lista_paginada(
        self,
        estado: EstadoConsulta | None,
        mascota_id: int | None,
        estudiante_id: int | None,
        skip: int,
        limit: int,
    ) -> tuple[list[Consulta], int]:
        query = self.db.query(Consulta)
        if estado is not None:
            query = query.filter(Consulta.estado == estado)
        if mascota_id is not None:
            query = query.filter(Consulta.mascota_id == mascota_id)
        if estudiante_id is not None:
            query = query.filter(Consulta.estudiante_id == estudiante_id)
        total = query.count()
        items = query.order_by(Consulta.fecha_hora).offset(skip).limit(limit).all()
        return items, total

    def obtener_por_id(self, consultation_id: int) -> Consulta | None:
        return self.db.get(Consulta, consultation_id)

    def actualizar(self, consultation: Consulta) -> Consulta:
        self.db.commit()
        self.db.refresh(consultation)
        return consultation

    def eliminar(self, consultation: Consulta) -> None:
        self.db.delete(consultation)
        self.db.commit()
