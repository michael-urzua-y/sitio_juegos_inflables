"""Textos y datos de contacto editables desde el admin (tabla Ajuste)."""
from collections import defaultdict

from flask import current_app, g

from app.extensions import db
from app.models import Ajuste
from app.seo_config import SEO
from app.utils.texto import abreviar_nombre, email_valido, recortar, solo_digitos, url_segura

# (grupo, [(clave, etiqueta, tipo_input)])
# Textos del sitio: los edita el super admin
GRUPOS_TEXTOS = [
    ("Marca", [
        ("nombre", "Nombre del negocio", "text"),
        ("nombre_corto", "Nombre corto: panel admin e ícono en el celular (vacío = automático: «Ent. Santos»)", "text"),
        ("razon_social", "Razón social (aparece en el footer)", "text"),
        ("slogan", "Slogan", "text"),
    ]),
    ("Portada", [
        ("hero_titulo", "Título principal (encierra entre *asteriscos* la palabra a destacar)", "text"),
        ("hero_subtitulo", "Texto bajo el título", "textarea"),
    ]),
]
# Contacto: lo edita el admin (dueño del negocio)
GRUPOS_CONTACTO = [
    ("Contacto", [
        ("whatsapp", "WhatsApp (formato 569XXXXXXXX, sin + ni espacios)", "text"),
        ("telefono", "Teléfono visible", "text"),
        ("email", "Email", "email"),
        ("zona", "Zona de cobertura", "text"),
        ("horario", "Horario de atención", "text"),
    ]),
    ("Redes sociales", [
        ("instagram", "URL de Instagram", "url"),
        ("facebook", "URL de Facebook", "url"),
    ]),
]
# Validación por clave o por tipo de input: los valores inválidos quedan vacíos
LIMPIADORES = {
    "whatsapp": lambda v: solo_digitos(v)[:15],
    "url": url_segura,
    "email": email_valido,
}
LARGO_MAX = 500


def editables():
    return defaultdict(str, {a.clave: a.valor or "" for a in Ajuste.query.all()})


def obtener():
    """Ajustes editables + SEO interno + datos fijos del sitio. Una consulta por request."""
    if "ajustes" not in g:
        cfg = current_app.config
        g.ajustes = editables()
        g.ajustes.update(SEO)  # el SEO no es editable por el cliente
        g.ajustes["nombre_corto"] = g.ajustes["nombre_corto"] or abreviar_nombre(g.ajustes["nombre"])
        g.ajustes.update(url=cfg["SITIO_URL"], creditos=cfg["CREDITOS"], creditos_url=cfg["CREDITOS_URL"])
    return g.ajustes


def guardar(form, grupos):
    """Guarda solo los campos de los grupos indicados (los demás no se tocan)."""
    actuales = {a.clave: a for a in Ajuste.query.all()}
    for _grupo, campos in grupos:
        for clave, _label, tipo in campos:
            valor = recortar(form.get(clave), LARGO_MAX)
            limpiar = LIMPIADORES.get(clave) or LIMPIADORES.get(tipo)
            ajuste = actuales.get(clave) or Ajuste(clave=clave)
            ajuste.valor = limpiar(valor) if limpiar else valor
            db.session.add(ajuste)
    db.session.commit()
    g.pop("ajustes", None)
