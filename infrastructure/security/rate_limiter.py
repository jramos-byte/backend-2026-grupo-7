"""Límite de intentos por ventana deslizante (en memoria, por proceso).

Suficiente para una sola réplica; con varias réplicas habría que moverlo a
Redis/BD. Se aplica por correo y por IP, exista o no la cuenta, para no filtrar
qué correos están registrados.
"""
import threading
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, max_attempts: int, window_seconds: int, clock=time.monotonic):
        self.max_attempts, self.window, self.clock = max_attempts, window_seconds, clock
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        """Registra un intento; False si se superó el límite."""
        now = self.clock()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= self.window:
                hits.popleft()
            if len(hits) >= self.max_attempts:
                return False
            hits.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()
