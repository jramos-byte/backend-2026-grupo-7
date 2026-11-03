from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from infrastructure.models.models import Dueno, Mascota
from presentation.dependencies import get_db
from presentation.schemas.dtos.schemas import MascotaCreate, MascotaResponse, Page

router = APIRouter(prefix="/pets", tags=["Mascotas"])


@router.post("", response_model=MascotaResponse, status_code=status.HTTP_201_CREATED)
def create_pet(payload: MascotaCreate, db: Session = Depends(get_db)):
    if db.get(Dueno, payload.dueno_id) is None:
        raise HTTPException(status_code=404, detail="Dueño asociado no encontrado")
    pet = Mascota(**payload.model_dump())
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


@router.get("", response_model=Page[MascotaResponse])
def list_pets(
    especie: str | None = None,
    q: str | None = Query(None, description="Busca por nombre o raza"),
    sort_by: str = Query("id", pattern="^(id|nombre|especie|raza|peso_kg)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Mascota)
    if especie:
        query = query.filter(Mascota.especie.ilike(especie))
    if q:
        term = f"%{q}%"
        query = query.filter(Mascota.nombre.ilike(term) | Mascota.raza.ilike(term))
    total = query.count()
    column = getattr(Mascota, sort_by)
    column = column.desc() if order == "desc" else column.asc()
    items = query.order_by(column).offset(skip).limit(limit).all()
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{pet_id}", response_model=MascotaResponse)
def get_pet(pet_id: int, db: Session = Depends(get_db)):
    pet = db.get(Mascota, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return pet


@router.put("/{pet_id}", response_model=MascotaResponse)
def update_pet(pet_id: int, payload: MascotaCreate, db: Session = Depends(get_db)):
    pet = db.get(Mascota, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    if db.get(Dueno, payload.dueno_id) is None:
        raise HTTPException(status_code=404, detail="Dueño asociado no encontrado")
    for key, value in payload.model_dump().items():
        setattr(pet, key, value)
    db.commit()
    db.refresh(pet)
    return pet


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: int, db: Session = Depends(get_db)):
    pet = db.get(Mascota, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    db.delete(pet)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
