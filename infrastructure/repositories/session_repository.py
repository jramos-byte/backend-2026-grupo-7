from sqlalchemy.orm import Session
from infrastructure.models.models import RecuperacionContrasena, SessionUsuario


class SessionRepo:
    def __init__(self, db: Session):
        self.db = db

    def crear_sesion(self, sesion: SessionUsuario) -> SessionUsuario:
        self.db.add(sesion)
        self.db.commit()
        self.db.refresh(sesion)
        return sesion

    def obtener_sesion_por_token(self, refresh_token: str) -> SessionUsuario | None:
        return (
            self.db.query(SessionUsuario)
            .filter(SessionUsuario.refresh_token == refresh_token)
            .first()
        )

    def revocar_sesion(self, sesion: SessionUsuario) -> SessionUsuario:
        sesion.is_revoked = True
        self.db.commit()
        self.db.refresh(sesion)
        return sesion

    def crear_token_recuperacion(self, recovery: RecuperacionContrasena) -> RecuperacionContrasena:
        self.db.add(recovery)
        self.db.commit()
        self.db.refresh(recovery)
        return recovery

    def obtener_token_recuperacion(self, token: str) -> RecuperacionContrasena | None:
        return (
            self.db.query(RecuperacionContrasena)
            .filter(RecuperacionContrasena.token == token)
            .first()
        )

    def marcar_token_usado(self, recovery: RecuperacionContrasena) -> RecuperacionContrasena:
        recovery.is_used = True
        self.db.commit()
        self.db.refresh(recovery)
        return recovery
