"""Filtros y funciones globales disponibles en todas las plantillas Jinja."""
import os
from datetime import date
from functools import lru_cache
from urllib.parse import quote

from flask import current_app, url_for

from app.services import ajustes, catalogo, seo, tarjetas
from app.utils.imagenes import ANCHOS, nombre_archivo
from app.utils.comunas import COMUNAS_RM
from app.utils.texto import formato_clp, resaltar


@lru_cache(maxsize=None)
def _placeholder(static_folder, slug):
    existe = os.path.exists(os.path.join(static_folder, "img", "placeholders", f"{slug}.svg"))
    return f"img/placeholders/{slug if existe else 'generico'}.svg"


def imagen_juego(juego, ancho=960, ext="webp"):
    """URL de la foto del juego o, si no tiene, la imagen referencial de su categoría."""
    if juego.imagen:
        return url_for("public.media", filename=nombre_archivo(juego.imagen, ancho, ext))
    slug = juego.categoria.slug if juego.categoria else "generico"
    return url_for("static", filename=_placeholder(current_app.static_folder, slug))


def og_imagen_juego(juego):
    """Tarjeta de marca para compartir el juego en redes (ruta relativa, con versión)."""
    return url_for("public.og_juego", slug=juego.slug, v=tarjetas.huella(tarjetas.datos_juego(juego)))


def og_imagen_categoria(categoria):
    datos = tarjetas.datos_categoria(categoria, catalogo.juegos(categoria_id=categoria.id))
    return url_for("public.og_categoria", slug=categoria.slug, v=tarjetas.huella(datos))


def srcset_juego(juego, ext="webp"):
    """srcset con todos los tamaños de un formato; vacío para imágenes referenciales (SVG)."""
    if not juego.imagen:
        return ""
    return ", ".join(f"{imagen_juego(juego, a, ext)} {a}w" for a in ANCHOS)


@lru_cache(maxsize=None)
def _version(static_folder, filename):
    try:
        return int(os.path.getmtime(os.path.join(static_folder, filename)))
    except OSError:
        return 0


def asset(filename):
    """URL de un archivo estático con versión (?v=) para poder cachearlo 1 año sin quedar obsoleto."""
    return url_for("static", filename=filename, v=_version(current_app.static_folder, filename))


ORIGEN_WEB = "🌐 *Mensaje desde el sitio web*"


def wa_url(texto=None):
    """Link a WhatsApp del negocio. Todos los mensajes llevan la marca de origen web,
    así el negocio distingue los contactos que llegan desde el sitio."""
    n = ajustes.obtener()
    cuerpo = texto or f"¡Hola {n['nombre']}! Les escribo desde su página web y quiero más información."
    return f"https://wa.me/{n['whatsapp']}?text={quote(ORIGEN_WEB + chr(10) + cuerpo)}"


def url_listado(endpoint, **params):
    """URL de un listado conservando filtros; omite parámetros vacíos y pagina=1 (URLs limpias)."""
    params = {k: v for k, v in params.items() if v not in (None, "") and not (k == "pagina" and v == 1)}
    return url_for(endpoint, **params)


def url_catalogo(categoria=None, **params):
    """URL del catálogo público (completo o de una categoría)."""
    if categoria:
        return url_listado("public.categoria", slug=categoria.slug, **params)
    return url_listado("public.catalogo_completo", **params)


def registrar(app):
    app.add_template_filter(formato_clp, "clp")
    app.add_template_filter(resaltar, "resaltar")
    app.add_template_filter(lambda a, b: list(zip(a, b)), "zip")

    @app.context_processor
    def globales():
        return {
            "negocio": ajustes.obtener(),
            "categorias": catalogo.categorias(),
            "imagen_juego": imagen_juego,
            "srcset_juego": srcset_juego,
            "asset": asset,
            "url_catalogo": url_catalogo,
            "url_listado": url_listado,
            "og_imagen_juego": og_imagen_juego,
            "og_imagen_categoria": og_imagen_categoria,
            "seo": seo,
            "wa_url": wa_url,
            "comunas_rm": COMUNAS_RM,
            "anio": date.today().year,
        }
