from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from infrastructure.models.models import Dueno
from presentation.dependencies import get_db
from presentation.schemas.dtos.schemas import DuenoCreate, DuenoResponse, Page

router = APIRouter(prefix="/owners", tags=["Dueños"])


@router.post("", response_model=DuenoResponse, status_code=status.HTTP_201_CREATED)
def create_owner(payload: DuenoCreate, db: Session = Depends(get_db)):
    owner = Dueno(**payload.model_dump())
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner


@router.get("", response_model=Page[DuenoResponse])
def list_owners(q: str | None = Query(None, description="Busca por nombre o RUT"), limit: int = Query(20, ge=1, le=100), skip: int = Query(0, ge=0), db: Session = Depends(get_db)):
    query = db.query(Dueno)
    if q:
        term = f"%{q}%"
        query = query.filter(or_(Dueno.nombre_completo.ilike(term), Dueno.rut.ilike(term)))
    total = query.count()
    return {"items": query.order_by(Dueno.id).offset(skip).limit(limit).all(), "total": total, "skip": skip, "limit": limit}


@router.get("/{owner_id}", response_model=DuenoResponse)
def get_owner(owner_id: int, db: Session = Depends(get_db)):
    owner = db.get(Dueno, owner_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    return owner


@router.put("/{owner_id}", response_model=DuenoResponse)
def update_owner(owner_id: int, payload: DuenoCreate, db: Session = Depends(get_db)):
    owner = db.get(Dueno, owner_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    for key, value in payload.model_dump().items():
        setattr(owner, key, value)
    db.commit()
    db.refresh(owner)
    return owner


@router.delete("/{owner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_owner(owner_id: int, db: Session = Depends(get_db)):
    owner = db.get(Dueno, owner_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    db.delete(owner)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
