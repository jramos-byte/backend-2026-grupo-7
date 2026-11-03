from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from presentation.dependencies import get_db
from infrastructure.models.models import Consulta, Mascota, Estudiante, EstadoConsulta
from presentation.schemas.dtos.schemas import ConsultaCreate, ConsultaResponse

router = APIRouter(prefix="/consultas", tags=["Consultas"])

@router.post("/", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED)
def crear_consulta(consulta: ConsultaCreate, db: Session = Depends(get_db)):
    # 1. Verificar que la mascota exista (Instrucción 6)
    mascota = db.query(Mascota).filter(Mascota.id == consulta.mascota_id).first()
    if not mascota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La mascota especificada no existe"
        )

    # 2. Verificar que el estudiante exista (Instrucción 6)
    estudiante = db.query(Estudiante).filter(Estudiante.id == consulta.estudiante_id).first()
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El estudiante especificado no existe"
        )

    nueva_consulta = Consulta(**consulta.model_dump())
    db.add(nueva_consulta)
    db.commit()
    db.refresh(nueva_consulta)
    return nueva_consulta

@router.get("/", response_model=List[ConsultaResponse])
def listar_consultas(
    estado: Optional[EstadoConsulta] = None,
    mascota_id: Optional[int] = None,
    estudiante_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Consulta)

    # Filtros opcionales
    if estado:
        query = query.filter(Consulta.estado == estado)
    if mascota_id:
        query = query.filter(Consulta.mascota_id == mascota_id)
    if estudiante_id:
        query = query.filter(Consulta.estudiante_id == estudiante_id)

    return query.offset(skip).limit(limit).all()

@router.get("/{consulta_id}", response_model=ConsultaResponse)
def obtener_consulta(consulta_id: int, db: Session = Depends(get_db)):
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )
    return consulta

@router.patch("/{consulta_id}", response_model=ConsultaResponse)
def actualizar_estado_diagnostico(
    consulta_id: int,
    estado: Optional[EstadoConsulta] = None,
    diagnostico: Optional[str] = None,
    db: Session = Depends(get_db)
):
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )

    if estado is not None:
        consulta.estado = estado
    if diagnostico is not None:
        consulta.diagnostico = diagnostico

    db.commit()
    db.refresh(consulta)
    return consulta

@router.delete("/{consulta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_consulta(consulta_id: int, db: Session = Depends(get_db)):
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )
    db.delete(consulta)
    db.commit()
    return None