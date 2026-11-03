"""Consultas del catálogo. Toda lectura de juegos/categorías pasa por aquí."""
from sqlalchemy import and_, or_

from app.models import Categoria, Juego
from app.utils.texto import slugify

POR_PAGINA = 12
LIMITE_DESTACADOS = 8


def categorias():
    return Categoria.query.order_by(Categoria.orden, Categoria.nombre).all()


def _ordenados(solo_activos=True):
    q = Juego.query.join(Categoria).order_by(Categoria.orden, Juego.orden, Juego.nombre)
    return q.filter(Juego.activo.is_(True)) if solo_activos else q


def juegos(solo_activos=True, categoria_id=None):
    q = _ordenados(solo_activos)
    if categoria_id:
        q = q.filter(Juego.categoria_id == categoria_id)
    return q.all()


def _filtro_texto(texto):
    """Busca por nombre o descripción, y también por el slug para ignorar tildes
    ("tobogan" encuentra "Tobogán"). Los comodines del usuario se escapan."""
    texto = texto.strip()[:60]
    if not texto:
        return None
    patron = "%" + texto.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_") + "%"
    palabras = [p for p in slugify(texto).split("-") if p]
    sin_tildes = and_(*[Juego.slug.like(f"%{p}%") for p in palabras]) if palabras else None
    condiciones = [Juego.nombre.ilike(patron, escape="\\"), Juego.descripcion.ilike(patron, escape="\\")]
    if sin_tildes is not None:
        condiciones.append(sin_tildes)
    return or_(*condiciones)


def buscar(categoria_id=None, texto="", pagina=1, por_pagina=POR_PAGINA, solo_activos=True):
    """Juegos filtrados y paginados (catálogo público y listado del admin)."""
    q = _ordenados(solo_activos)
    if categoria_id:
        q = q.filter(Juego.categoria_id == categoria_id)
    filtro = _filtro_texto(texto or "")
    if filtro is not None:
        q = q.filter(filtro)
    return q.paginate(page=pagina, per_page=por_pagina, error_out=False)


def _completar(elegidos, limite):
    """Completa la lista hasta `limite` con el resto del catálogo (orden normal), sin repetir."""
    if len(elegidos) < limite:
        ids = [j.id for j in elegidos]
        resto = _ordenados().filter(Juego.id.notin_(ids)) if ids else _ordenados()
        elegidos += resto.limit(limite - len(elegidos)).all()
    return elegidos


def destacados(limite=LIMITE_DESTACADOS):
    """Siempre `limite` juegos (grilla pareja): primero los destacados y luego el resto."""
    return _completar(_ordenados().filter(Juego.destacado.is_(True)).limit(limite).all(), limite)


def portada(limite=Juego.MAX_PORTADA):
    """Juegos de las tarjetas grandes de la portada: los marcados "Mostrar en la portada"
    (en su orden); si faltan, se completa con destacados y luego con el resto."""
    elegidos = (Juego.query.filter(Juego.activo.is_(True), Juego.en_portada.is_(True))
                .order_by(Juego.orden, Juego.nombre).limit(limite).all())
    if len(elegidos) < limite:
        ids = [j.id for j in elegidos]
        extra = _ordenados().filter(Juego.destacado.is_(True))
        extra = extra.filter(Juego.id.notin_(ids)) if ids else extra
        elegidos += extra.limit(limite - len(elegidos)).all()
    return _completar(elegidos, limite)


def en_portada(excluir_id=None):
    q = Juego.query.filter(Juego.activo.is_(True), Juego.en_portada.is_(True))
    if excluir_id:
        q = q.filter(Juego.id != excluir_id)
    return q.order_by(Juego.orden, Juego.nombre).all()


def total_activos():
    return Juego.query.filter(Juego.activo.is_(True)).count()


def total_juegos():
    return Juego.query.count()


def juego_publico(slug):
    return Juego.query.filter_by(slug=slug, activo=True).first_or_404()


def relacionados(juego, limite=3):
    return (_ordenados().filter(Juego.categoria_id == juego.categoria_id, Juego.id != juego.id)
            .limit(limite).all())
