from fastapi import HTTPException
from domain.rules import (
    BusinessRuleError,
    validate_consultation_transition,
    validate_future_appointment,
    validate_student_entry_year,
)
from infrastructure.models.models import Consulta, EstadoConsulta
from infrastructure.repositories.consultation_repository import ConsultationRepo
from infrastructure.repositories.pet_repository import PetRepo
from infrastructure.repositories.student_repository import StudentRepo
from presentation.schemas.dtos.schemas import ConsultaCreate, ConsultaUpdate


class ConsultationServicio:
    def __init__(
        self,
        consultation_repo: ConsultationRepo,
        pet_repo: PetRepo,
        student_repo: StudentRepo,
    ):
        self.consultation_repo = consultation_repo
        self.pet_repo = pet_repo
        self.student_repo = student_repo

    def _validar_referencias(self, mascota_id: int, estudiante_id: int) -> None:
        if self.pet_repo.obtener_por_id(mascota_id) is None:
            raise HTTPException(status_code=404, detail="Mascota asociada no encontrada")
        student = self.student_repo.obtener_por_id(estudiante_id)
        if student is None:
            raise HTTPException(status_code=404, detail="Estudiante asociado no encontrado")
        try:
            validate_student_entry_year(student.anio_ingreso)
        except BusinessRuleError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def crear_consultation(self, payload: ConsultaCreate) -> Consulta:
        try:
            validate_future_appointment(payload.fecha_hora)
        except BusinessRuleError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if payload.estado != EstadoConsulta.PENDIENTE:
            raise HTTPException(
                status_code=400, detail="Una consulta nueva debe iniciar en estado PENDIENTE"
            )
        self._validar_referencias(payload.mascota_id, payload.estudiante_id)
        consultation = Consulta(**payload.model_dump())
        return self.consultation_repo.crear_consultation(consultation)

    def lista_consultations(
        self,
        estado: EstadoConsulta | None,
        mascota_id: int | None,
        estudiante_id: int | None,
        skip: int,
        limit: int,
    ) -> dict:
        items, total = self.consultation_repo.lista_paginada(
            estado=estado,
            mascota_id=mascota_id,
            estudiante_id=estudiante_id,
            skip=skip,
            limit=limit,
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}

    def obtener_consultation(self, consultation_id: int) -> Consulta:
        consultation = self.consultation_repo.obtener_por_id(consultation_id)
        if consultation is None:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")
        return consultation

    def actualizar_consultation(
        self, consultation_id: int, payload: ConsultaUpdate
    ) -> Consulta:
        consultation = self.obtener_consultation(consultation_id)
        changes = payload.model_dump(exclude_unset=True)
        for required_field in ("fecha_hora", "motivo", "estado", "mascota_id", "estudiante_id"):
            if required_field in changes and changes[required_field] is None:
                raise HTTPException(
                    status_code=422, detail=f"El campo {required_field} no puede ser null"
                )
        new_date = changes.get("fecha_hora")
        if new_date is not None:
            try:
                validate_future_appointment(new_date)
            except BusinessRuleError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
        mascota_id = changes.get("mascota_id", consultation.mascota_id)
        estudiante_id = changes.get("estudiante_id", consultation.estudiante_id)
        self._validar_referencias(mascota_id, estudiante_id)
        new_state = changes.get("estado", consultation.estado)
        try:
            validate_consultation_transition(consultation.estado, new_state)
        except BusinessRuleError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        for key, value in changes.items():
            setattr(consultation, key, value)
        return self.consultation_repo.actualizar(consultation)

    def eliminar_consultation(self, consultation_id: int) -> None:
        consultation = self.obtener_consultation(consultation_id)
        self.consultation_repo.eliminar(consultation)
