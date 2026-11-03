"""
Límite de intentos fallidos de login por IP (complementa el bloqueo por usuario).

El bloqueo por usuario frena a quien prueba muchas claves contra UNA cuenta; este frena a
quien prueba muchas cuentas desde la misma conexión. Vive en memoria de cada worker de
gunicorn: es simple, no necesita Redis y se reinicia con la app (suficiente para un panel
con pocos usuarios).
"""
import threading
import time
from collections import defaultdict, deque


class LimitadorIntentos:
    def __init__(self, maximo, ventana_seg):
        self.maximo, self.ventana = maximo, ventana_seg
        self._fallos = defaultdict(deque)
        self._lock = threading.Lock()

    def _vigentes(self, clave):
        fallos, limite = self._fallos[clave], time.monotonic() - self.ventana
        while fallos and fallos[0] < limite:
            fallos.popleft()
        if not fallos:
            self._fallos.pop(clave, None)
        return fallos

    def bloqueada(self, clave):
        with self._lock:
            return len(self._vigentes(clave)) >= self.maximo

    def fallo(self, clave):
        with self._lock:
            self._fallos[clave].append(time.monotonic())

    def limpiar(self, clave):
        with self._lock:
            self._fallos.pop(clave, None)


# 10 intentos fallidos por IP cada 15 minutos
intentos_login = LimitadorIntentos(maximo=10, ventana_seg=15 * 60)
