"""Entrega del enlace de recuperación.

RESET_DELIVERY=console (defecto): log + bandeja en memoria (`outbox`), sin enviar correo.
RESET_DELIVERY=json: igual que console, y la API devuelve el enlace en la respuesta
                     (solo para pruebas/demostración; nunca en producción).
RESET_DELIVERY=smtp: envío real con SMTP_HOST/PORT/USER/PASSWORD/FROM.
"""
import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger("password_reset")


def build_link(token: str) -> str:
    base = os.getenv("RESET_URL_BASE", "http://localhost:8000/reset-password")
    return f"{base}?token={token}"


class ConsoleEmailSender:
    def __init__(self):
        self.outbox: list[dict] = []

    def send_reset_link(self, to: str, link: str) -> None:
        self.outbox.append({"to": to, "link": link})
        # No se registra el token completo en logs.
        logger.info("Enlace de recuperación generado para %s (modo prueba)", to)


class SmtpEmailSender:
    def send_reset_link(self, to: str, link: str) -> None:
        msg = EmailMessage()
        msg["Subject"] = "Recuperación de contraseña"
        msg["From"] = os.environ["SMTP_FROM"]
        msg["To"] = to
        msg.set_content(f"Para restablecer tu contraseña usa este enlace (vence pronto, un solo uso):\n{link}")
        with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.getenv("SMTP_PORT", "587")), timeout=10) as smtp:
            smtp.starttls()
            smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
            smtp.send_message(msg)


def delivery_mode() -> str:
    return os.getenv("RESET_DELIVERY", "console").lower()


_console = ConsoleEmailSender()


def get_email_sender():
    return SmtpEmailSender() if delivery_mode() == "smtp" else _console
