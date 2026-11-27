"""Unitarias aisladas (sin BD ni HTTP): repositorio falso en memoria."""
import time
from datetime import datetime, timedelta
from types import SimpleNamespace

import jwt
import pytest

from application.services.password_reset_service import (
    InvalidResetToken, PasswordResetService, RateLimitExceeded, WeakPassword, GENERIC_REQUEST_MESSAGE,
)
from infrastructure.security import reset_token as rt
from infrastructure.security.email_sender import ConsoleEmailSender
from infrastructure.security.password_policy import validate_password, PasswordPolicyError
from infrastructure.security.rate_limiter import RateLimiter

SECRET = "x" * 40


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("RESET_JWT_SECRET", SECRET)


class FakeRepo:
    def __init__(self):
        self.users = {1: SimpleNamespace(id=1, correo="a@x.cl", activo=True, password_hash="old"),
                      2: SimpleNamespace(id=2, correo="b@x.cl", activo=True, password_hash="oldb")}
        self.tokens, self.revoked = {}, []

    def get_user_by_email(self, c): return next((u for u in self.users.values() if u.correo == c), None)
    def get_user_by_id(self, i): return self.users.get(i)
    def invalidate_pending_tokens(self, uid, now):
        for t in self.tokens.values():
            if t.usuario_id == uid and t.used_at is None: t.used_at = now
    def add_token(self, jti, uid, c, e): self.tokens[jti] = SimpleNamespace(jti=jti, usuario_id=uid, expires_at=e, used_at=None)
    def get_token(self, jti): return self.tokens.get(jti)
    def consume_token(self, jti, now):
        t = self.tokens[jti]
        if t.used_at is None and t.expires_at > now: t.used_at = now; return True
        return False
    def update_password(self, uid, h, now): self.users[uid].password_hash = h
    def revoke_all_sessions(self, uid, now): self.revoked.append(uid)
    def commit(self): pass
    def rollback(self): pass


def make(clock=None, limiter=None):
    repo, mail = FakeRepo(), ConsoleEmailSender()
    kw = {"clock": clock} if clock else {}
    svc = PasswordResetService(repo, mail, limiter or RateLimiter(50, 60), lambda p: "H:" + p,
                               validate_password, lambda t: "http://t/?token=" + t, expose_link=True, **kw)
    return svc, repo, mail


def token_of(result): return result.reset_link.split("token=")[1]


def test_request_generica_igual_para_correo_existente_y_no_existente():
    svc, _, mail = make()
    a, b = svc.request_reset("a@x.cl"), svc.request_reset("nadie@x.cl")
    assert a.message == b.message == GENERIC_REQUEST_MESSAGE
    assert len(mail.outbox) == 1 and b.reset_link is None


def test_token_tiene_sujeto_proposito_expiracion_y_jti_unico():
    t1, j1, _ = rt.create_reset_token(7, int(time.time()))
    t2, j2, _ = rt.create_reset_token(7, int(time.time()))
    data = jwt.decode(t1, SECRET, algorithms=["HS256"], issuer=rt.ISSUER)
    assert data["sub"] == "7" and data["purpose"] == "password_reset" and "exp" in data and j1 != j2


def test_token_expirado_firma_invalida_y_otro_proposito_se_rechazan():
    expired, _, _ = rt.create_reset_token(1, int(time.time()) - 7200, ttl_seconds=60)
    with pytest.raises(rt.ResetTokenError): rt.decode_reset_token(expired)
    good, _, _ = rt.create_reset_token(1, int(time.time()))
    with pytest.raises(rt.ResetTokenError): rt.decode_reset_token(good, secret="y" * 40)
    access = jwt.encode({"sub": "1", "purpose": "access", "jti": "j", "iat": int(time.time()),
                         "exp": int(time.time()) + 60, "iss": rt.ISSUER}, SECRET, algorithm="HS256")
    with pytest.raises(rt.ResetTokenError): rt.decode_reset_token(access)
    none_alg = jwt.encode({"sub": "1"}, None, algorithm="none")
    with pytest.raises(rt.ResetTokenError): rt.decode_reset_token(none_alg)


def test_confirmacion_cambia_clave_e_invalida_sesiones_y_otros_permisos():
    svc, repo, _ = make()
    first = token_of(svc.request_reset("a@x.cl"))
    second = token_of(svc.request_reset("a@x.cl"))
    with pytest.raises(InvalidResetToken): svc.confirm_reset(first, "nueva-clave-segura-1")  # reemplazado
    svc.confirm_reset(second, "nueva-clave-segura-1")
    assert repo.users[1].password_hash == "H:nueva-clave-segura-1" and repo.revoked == [1]
    assert repo.users[2].password_hash == "oldb"


def test_token_es_de_un_solo_uso():
    svc, _, _ = make()
    tok = token_of(svc.request_reset("a@x.cl"))
    svc.confirm_reset(tok, "nueva-clave-segura-1")
    with pytest.raises(InvalidResetToken): svc.confirm_reset(tok, "otra-clave-segura-22")


def test_clave_debil_no_consume_el_token():
    svc, _, _ = make()
    tok = token_of(svc.request_reset("a@x.cl"))
    with pytest.raises(WeakPassword): svc.confirm_reset(tok, "corta")
    svc.confirm_reset(tok, "nueva-clave-segura-1")  # sigue vigente


def test_token_no_sirve_para_otra_cuenta():
    svc, repo, _ = make()
    tok, jti, exp = rt.create_reset_token(2, int(time.time()))  # firmado válido, sub=2
    repo.add_token(jti, 1, datetime.utcnow(), datetime.utcnow() + timedelta(minutes=5))  # registro es de la cuenta 1
    with pytest.raises(InvalidResetToken): svc.confirm_reset(tok, "nueva-clave-segura-1")
    assert repo.users[1].password_hash == "old" and repo.users[2].password_hash == "oldb"


def test_token_expira_segun_el_reloj_del_servicio():
    now = [datetime(2026, 1, 1, 12, 0)]
    svc, _, _ = make(clock=lambda: now[0])
    # el JWT se firma con iat real; el registro caduca con el reloj inyectado
    tok = token_of(svc.request_reset("a@x.cl"))
    now[0] += timedelta(hours=1)
    with pytest.raises(InvalidResetToken): svc.confirm_reset(tok, "nueva-clave-segura-1")


def test_limite_de_intentos_y_politica_de_clave():
    svc, _, _ = make(limiter=RateLimiter(2, 60))
    svc.request_reset("a@x.cl"); svc.request_reset("a@x.cl")
    with pytest.raises(RateLimitExceeded): svc.request_reset("a@x.cl")
    with pytest.raises(PasswordPolicyError): validate_password("a" * 11)
    validate_password("a" * 12)
