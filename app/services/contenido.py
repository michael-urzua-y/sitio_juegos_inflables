"""Bloques de contenido (cifras, beneficios, pasos, FAQ) agrupados por tipo."""
from collections import defaultdict

from app.models import Bloque


def bloques_por_tipo(solo_activos=True):
    q = Bloque.query.order_by(Bloque.tipo, Bloque.orden, Bloque.id)
    if solo_activos:
        q = q.filter(Bloque.activo.is_(True))
    agrupados = defaultdict(list)
    for b in q.all():
        agrupados[b.tipo].append(b)
    return agrupados
