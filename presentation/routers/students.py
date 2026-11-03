from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from infrastructure.models.models import Estudiante
from presentation.dependencies import get_db
from presentation.schemas.dtos.schemas import EstudianteCreate, EstudianteResponse, Page

router = APIRouter(prefix="/students", tags=["Estudiantes"])


@router.post("", response_model=EstudianteResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: EstudianteCreate, db: Session = Depends(get_db)):
    student = Estudiante(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("", response_model=Page[EstudianteResponse])
def list_students(
    q: str | None = Query(None, description="Busca por nombre, RUT o correo"),
    anio_ingreso: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Estudiante)
    if q:
        term = f"%{q}%"
        query = query.filter(or_(Estudiante.nombre_completo.ilike(term), Estudiante.rut.ilike(term), Estudiante.correo.ilike(term)))
    if anio_ingreso is not None:
        query = query.filter(Estudiante.anio_ingreso == anio_ingreso)
    total = query.count()
    items = query.order_by(Estudiante.id).offset(skip).limit(limit).all()
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{student_id}", response_model=EstudianteResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Estudiante, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student


@router.put("/{student_id}", response_model=EstudianteResponse)
def update_student(student_id: int, payload: EstudianteCreate, db: Session = Depends(get_db)):
    student = db.get(Estudiante, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    for key, value in payload.model_dump().items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Estudiante, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    db.delete(student)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
