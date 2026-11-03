from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm Session
from typing import List

from presentation.dependencies import get_db
from infrastructure.models.models import Mascota, Dueno
from presentation.schemas.dtos.schemas import MascotaCreate, MascotaResponse

router = APIRouter(prefix="/mascotas", tags=["Mascotas"])

@router.post("/", response_model=MascotaResponse, status_code=status.HTTP_201_CREATED)
def crear_mascota(mascota: MascotaCreate, db: Session = Depends(get_db)):
    # Validar la existencia del dueño (Integridad Referencial)
    dueno = db.query(Dueno).filter(Dueno.id == mascota.dueño_id).first()
    if not dueno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="El dueño especificado no existe"
        )
    
    nueva_mascota = Mascota(**mascota.model_dump())
    db.add(nueva_mascota)
    db.commit()
    db.refresh(nueva_mascota)
    return nueva_mascota

@router.get("/", response_model=List[MascotaResponse])
def listar_mascotas(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=100), 
    db: Session = Depends(get_db)
):
    return db.query(Mascota).offset(skip).limit(limit).all()

@router.get("/{mascota_id}", response_model=MascotaResponse)
def obtener_mascota(mascota_id: int, db: Session = Depends(get_db)):
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()
    if not mascota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Mascota no encontrada"
        )
    return mascota

@router.delete("/{mascota_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mascota(mascota_id: int, db: Session = Depends(get_db)):
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()
    if not mascota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Mascota no encontrada"
        )
    db.delete(mascota)
    db.commit()
    return None