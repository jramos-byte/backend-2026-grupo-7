from sqlalchemy.orm import Session
from infrastructure.models.models import Rol, Usuario


class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_id(self, user_id: int) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.id == user_id).first()

    def obtener_por_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def crear_usuario(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def actualizar_usuario(self, usuario: Usuario) -> Usuario:
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def obtener_rol_por_nombre(self, name: str) -> Rol | None:
        return self.db.query(Rol).filter(Rol.name == name).first()

    def crear_rol(self, rol: Rol) -> Rol:
        self.db.add(rol)
        self.db.commit()
        self.db.refresh(rol)
        return rol
