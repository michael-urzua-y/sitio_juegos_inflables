"""Lee campos de request.form respetando el largo máximo de cada columna del modelo."""
from app.utils.texto import recortar

LARGO_TEXTO_LIBRE = 2000


def largo_columna(modelo, campo):
    return getattr(modelo.__table__.c[campo].type, "length", None) or LARGO_TEXTO_LIBRE


def asignar_textos(obj, form, campos):
    """Asigna varios campos de texto del form al objeto, recortados a su largo de columna."""
    for campo in campos:
        setattr(obj, campo, recortar(form.get(campo), largo_columna(type(obj), campo)))
