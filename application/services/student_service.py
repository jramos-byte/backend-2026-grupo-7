from fastapi import HTTPException
from infrastructure.models.models import Estudiante
from infrastructure.repositories.student_repository import StudentRepo
from presentation.schemas.dtos.schemas import EstudianteCreate


class StudentServicio:
    def __init__(self, student_repo: StudentRepo):
        self.student_repo = student_repo

    def crear_student(self, payload: EstudianteCreate) -> Estudiante:
        student = Estudiante(**payload.model_dump())
        return self.student_repo.crear_student(student)

    def lista_students(
        self, q: str | None, anio_ingreso: int | None, skip: int, limit: int
    ) -> dict:
        items, total = self.student_repo.lista_paginada(
            q=q, anio_ingreso=anio_ingreso, skip=skip, limit=limit
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}

    def obtener_student(self, student_id: int) -> Estudiante:
        student = self.student_repo.obtener_por_id(student_id)
        if student is None:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return student

    def actualizar_student(self, student_id: int, payload: EstudianteCreate) -> Estudiante:
        student = self.obtener_student(student_id)
        for key, value in payload.model_dump().items():
            setattr(student, key, value)
        return self.student_repo.actualizar(student)

    def eliminar_student(self, student_id: int) -> None:
        student = self.obtener_student(student_id)
        self.student_repo.eliminar(student)
