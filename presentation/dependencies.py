from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.database import SessionLocal
from infrastructure.repositories.consultation_repository import ConsultationRepo
from infrastructure.repositories.owner_repository import OwnerRepo
from infrastructure.repositories.pet_repository import PetRepo
from infrastructure.repositories.student_repository import StudentRepo
from application.services.consultation_service import ConsultationServicio
from application.services.owner_service import OwnerServicio
from application.services.pet_service import PetServicio
from application.services.student_service import StudentServicio


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_owner_service(db: Session = Depends(get_db)) -> OwnerServicio:
    return OwnerServicio(OwnerRepo(db))


def get_student_service(db: Session = Depends(get_db)) -> StudentServicio:
    return StudentServicio(StudentRepo(db))


def get_pet_service(db: Session = Depends(get_db)) -> PetServicio:
    return PetServicio(PetRepo(db), OwnerRepo(db))


def get_consultation_service(db: Session = Depends(get_db)) -> ConsultationServicio:
    return ConsultationServicio(
        ConsultationRepo(db), PetRepo(db), StudentRepo(db)
    )
