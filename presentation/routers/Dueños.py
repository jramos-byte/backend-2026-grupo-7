from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from presentation.dependencies import get_db
from infrastructure.models.models import Dueno
from presentation.schemas.dtos.schemas import DuenoCreate, DuenoResponse

router = APIRouter(prefix="/duenos", tags=["Dueños"])

@router.post("/", response_model=DuenoResponse, status_code=status.HTTP_201_CREATED)
def crear_dueno(dueno: DuenoCreate, db: Session = Depends(get_db)):
    # Verificar si el RUT ya existe
    db_dueno = db.query(Dueno).filter(Dueno.rut == dueno.rut).first()
    if db_dueno:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="El RUT del dueño ya está registrado"
        )
    
    # Uso de .model_dump() recomendado en Pydantic v2
    nuevo_dueno = Dueno(**dueno.model_dump())
    
    try:
        db.add(nuevo_dueno)
        db.commit()
        db.refresh(nuevo_dueno)
        return nuevo_dueno
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Error de integridad: El RUT ya existe en el sistema"
        )

@router.get("/", response_model=List[DuenoResponse])
def listar_duenos(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=100), 
    db: Session = Depends(get_db)
):
    return db.query(Dueno).offset(skip).limit(limit).all()

@router.get("/{dueno_id}", response_model=DuenoResponse)
def obtener_dueno(dueno_id: int, db: Session = Depends(get_db)):
    dueno = db.query(Dueno).filter(Dueno.id == dueno_id).first()
    if not dueno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Dueño no encontrado"
        )
    return dueno

@router.delete("/{dueno_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_dueno(dueno_id: int, db: Session = Depends(get_db)):
    dueno = db.query(Dueno).filter(Dueno.id == dueno_id).first()
    if not dueno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Dueño no encontrado"
        )
    db.delete(dueno)
    db.commit()
    return None