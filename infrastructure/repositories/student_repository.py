from sqlalchemy import or_
from sqlalchemy.orm import Session
from infrastructure.models.models import Estudiante


class StudentRepo:
    def __init__(self, db: Session):
        self.db = db

    def crear_student(self, student: Estudiante) -> Estudiante:
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def lista_paginada(
        self, q: str | None, anio_ingreso: int | None, skip: int, limit: int
    ) -> tuple[list[Estudiante], int]:
        query = self.db.query(Estudiante)
        if q:
            term = f"%{q}%"
            query = query.filter(
                or_(
                    Estudiante.nombre_completo.ilike(term),
                    Estudiante.rut.ilike(term),
                    Estudiante.correo.ilike(term),
                )
            )
        if anio_ingreso is not None:
            query = query.filter(Estudiante.anio_ingreso == anio_ingreso)
        total = query.count()
        items = query.order_by(Estudiante.id).offset(skip).limit(limit).all()
        return items, total

    def obtener_por_id(self, student_id: int) -> Estudiante | None:
        return self.db.get(Estudiante, student_id)

    def actualizar(self, student: Estudiante) -> Estudiante:
        self.db.commit()
        self.db.refresh(student)
        return student

    def eliminar(self, student: Estudiante) -> None:
        self.db.delete(student)
        self.db.commit()
