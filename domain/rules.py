from datetime import datetime


class BusinessRuleError(ValueError):
    """Indica que una operación válida en forma incumple una regla del dominio."""


def validate_future_appointment(value: datetime) -> None:
    now = datetime.now(value.tzinfo) if value.tzinfo else datetime.now()
    if value <= now:
        raise BusinessRuleError("La consulta debe programarse en una fecha y hora futuras")


def validate_student_entry_year(year: int, current_year: int | None = None) -> None:
    current_year = current_year or datetime.now().year
    if not 2010 <= year <= current_year:
        raise BusinessRuleError("El estudiante no tiene un año de ingreso válido")


def validate_consultation_transition(current: object, target: object) -> None:
    current_value = getattr(current, "value", current)
    target_value = getattr(target, "value", target)
    if current_value == target_value:
        return
    allowed = current_value == "pendiente" and target_value in ("realizada", "cancelada")
    if not allowed:
        raise BusinessRuleError("Transición de estado no permitida")
