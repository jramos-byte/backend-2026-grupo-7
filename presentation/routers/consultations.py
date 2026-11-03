from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from domain.rules import (
    BusinessRuleError,
    validate_consultation_transition,
    validate_future_appointment,
    validate_student_entry_year,
)
from infrastructure.models.models import Consulta, EstadoConsulta, Estudiante, Mascota
from presentation.dependencies import get_db
from presentation.schemas.dtos.schemas import ConsultaCreate, ConsultaResponse, ConsultaUpdate, Page

router = APIRouter(prefix="/consultations", tags=["Consultas"])


def validate_references(db: Session, mascota_id: int, estudiante_id: int) -> None:
    if db.get(Mascota, mascota_id) is None:
        raise HTTPException(status_code=404, detail="Mascota asociada no encontrada")
    student = db.get(Estudiante, estudiante_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Estudiante asociado no encontrado")
    try:
        validate_student_entry_year(student.anio_ingreso)
    except BusinessRuleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED)
def create_consultation(payload: ConsultaCreate, db: Session = Depends(get_db)):
    try:
        validate_future_appointment(payload.fecha_hora)
    except BusinessRuleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if payload.estado != EstadoConsulta.PENDIENTE:
        raise HTTPException(status_code=400, detail="Una consulta nueva debe iniciar en estado PENDIENTE")
    validate_references(db, payload.mascota_id, payload.estudiante_id)
    consultation = Consulta(**payload.model_dump())
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation


@router.get("", response_model=Page[ConsultaResponse])
def list_consultations(
    estado: EstadoConsulta | None = None,
    mascota_id: int | None = None,
    estudiante_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Consulta)
    if estado is not None:
        query = query.filter(Consulta.estado == estado)
    if mascota_id is not None:
        query = query.filter(Consulta.mascota_id == mascota_id)
    if estudiante_id is not None:
        query = query.filter(Consulta.estudiante_id == estudiante_id)
    total = query.count()
    items = query.order_by(Consulta.fecha_hora).offset(skip).limit(limit).all()
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{consultation_id}", response_model=ConsultaResponse)
def get_consultation(consultation_id: int, db: Session = Depends(get_db)):
    consultation = db.get(Consulta, consultation_id)
    if consultation is None:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    return consultation


@router.patch("/{consultation_id}", response_model=ConsultaResponse)
def update_consultation(consultation_id: int, payload: ConsultaUpdate, db: Session = Depends(get_db)):
    consultation = db.get(Consulta, consultation_id)
    if consultation is None:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    changes = payload.model_dump(exclude_unset=True)
    for required_field in ("fecha_hora", "motivo", "estado", "mascota_id", "estudiante_id"):
        if required_field in changes and changes[required_field] is None:
            raise HTTPException(status_code=422, detail=f"El campo {required_field} no puede ser null")
    new_date = changes.get("fecha_hora")
    if new_date is not None:
        try:
            validate_future_appointment(new_date)
        except BusinessRuleError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    mascota_id = changes.get("mascota_id", consultation.mascota_id)
    estudiante_id = changes.get("estudiante_id", consultation.estudiante_id)
    validate_references(db, mascota_id, estudiante_id)
    new_state = changes.get("estado", consultation.estado)
    try:
        validate_consultation_transition(consultation.estado, new_state)
    except BusinessRuleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    for key, value in changes.items():
        setattr(consultation, key, value)
    db.commit()
    db.refresh(consultation)
    return consultation


@router.delete("/{consultation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consultation(consultation_id: int, db: Session = Depends(get_db)):
    consultation = db.get(Consulta, consultation_id)
    if consultation is None:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    db.delete(consultation)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
