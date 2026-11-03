from datetime import date, datetime
from xml.sax.saxutils import escape

from flask import (Response, current_app, render_template, request, send_file,
                   send_from_directory, url_for)

from app.marca import MARCA
from app.models import Categoria
from app.services import ajustes, catalogo, seo, tarjetas
from app.utils.plantillas import og_imagen_juego
from app.services.contenido import bloques_por_tipo

from . import bp


@bp.route("/")
def inicio():
    return render_template("public/index.html", destacados=catalogo.destacados(), portada=catalogo.portada(),
                           total=catalogo.total_activos(), bloques=bloques_por_tipo())


def _listado(categoria=None):
    """Catálogo paginado; lo comparten /catalogo y /categoria/<slug>."""
    texto = request.args.get("q", "").strip()[:60]
    paginacion = catalogo.buscar(categoria_id=categoria.id if categoria else None, texto=texto,
                                 pagina=request.args.get("pagina", 1, type=int))
    return render_template("public/catalogo.html", categoria=categoria, q=texto, paginacion=paginacion)


@bp.route("/catalogo")
def catalogo_completo():
    return _listado()


@bp.route("/categoria/<slug>")
def categoria(slug):
    return _listado(Categoria.query.filter_by(slug=slug).first_or_404())


@bp.route("/juego/<slug>")
def juego(slug):
    j = catalogo.juego_publico(slug)
    return render_template("public/juego.html", juego=j, relacionados=catalogo.relacionados(j))


@bp.route("/media/<path:filename>")
def media(filename):
    resp = send_from_directory(current_app.config["UPLOAD_DIR"], filename)
    resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return resp


def _enviar_tarjeta(datos):
    resp = send_file(tarjetas.archivo_tarjeta(datos), mimetype="image/jpeg")
    resp.headers["Cache-Control"] = "public, max-age=86400"
    return resp


@bp.route("/og/juego/<slug>.jpg")
def og_juego(slug):
    return _enviar_tarjeta(tarjetas.datos_juego(catalogo.juego_publico(slug)))


@bp.route("/og/categoria/<slug>.jpg")
def og_categoria(slug):
    cat = Categoria.query.filter_by(slug=slug).first_or_404()
    return _enviar_tarjeta(tarjetas.datos_categoria(cat, catalogo.juegos(categoria_id=cat.id)))


@bp.route("/healthz")
def healthz():
    return {"status": "ok"}


# Rastreadores de buscadores e IAs a los que se invita explícitamente a indexar el sitio
BOTS_PERMITIDOS = [
    "Googlebot", "Bingbot", "DuckDuckBot", "YandexBot", "Applebot", "Applebot-Extended",
    "Google-Extended",                                  # Gemini
    "GPTBot", "OAI-SearchBot", "ChatGPT-User",          # ChatGPT
    "ClaudeBot", "Claude-SearchBot", "Claude-User",     # Claude
    "PerplexityBot", "Perplexity-User",                 # Perplexity
    "meta-externalagent", "facebookexternalhit",        # Meta / Facebook / WhatsApp
    "Twitterbot", "LinkedInBot", "CCBot",
]


def _texto(contenido):
    return Response(contenido, mimetype="text/plain; charset=utf-8")


@bp.route("/robots.txt")
def robots():
    base = current_app.config["SITIO_URL"]
    reglas = "Disallow: /admin\nAllow: /\n"
    bloques = [f"User-agent: {bot}\n{reglas}" for bot in BOTS_PERMITIDOS]
    bloques.append(f"User-agent: *\n{reglas}")
    return _texto("\n".join(bloques) + f"\nSitemap: {base}/sitemap.xml\n")


@bp.route("/sitemap.xml")
def sitemap():
    base = current_app.config["SITIO_URL"]
    hoy = date.today().isoformat()

    def url(loc, lastmod=hoy, prioridad="0.7", imagen=None):
        img = (f"<image:image><image:loc>{escape(base + imagen)}</image:loc></image:image>" if imagen else "")
        return (f"<url><loc>{escape(base + loc)}</loc><lastmod>{lastmod}</lastmod>"
                f"<priority>{prioridad}</priority>{img}</url>")

    urls = [url("/", prioridad="1.0"), url("/catalogo", prioridad="0.9")]
    urls += [url(f"/categoria/{c.slug}", prioridad="0.8") for c in catalogo.categorias()]
    urls += [url(f"/juego/{j.slug}", (j.actualizado or datetime.utcnow()).date().isoformat(),
                 imagen=og_imagen_juego(j)) for j in catalogo.juegos()]
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">' + "".join(urls) + "</urlset>")
    return Response(xml, mimetype="application/xml")


@bp.route("/llms.txt")
def llms():
    """Resumen en Markdown pensado para IAs (ChatGPT, Claude, Gemini, Perplexity)."""
    return _texto(render_template("public/llms.txt", juegos=catalogo.juegos(),
                                  preguntas=bloques_por_tipo()["faq"], palabras=seo.palabras_clave()))


@bp.route("/site.webmanifest")
def manifest():
    n = ajustes.obtener()
    def icono(archivo, lado, proposito="any"):
        return {"src": url_for("static", filename=f"img/{archivo}"), "sizes": f"{lado}x{lado}",
                "type": "image/png", "purpose": proposito}
    return {
        "name": n["nombre"], "short_name": n["nombre_corto"], "description": seo.descripcion_negocio(),
        "lang": "es-CL", "start_url": "/", "display": "standalone",
        "background_color": MARCA["color_tema"], "theme_color": MARCA["color_tema"],
        "icons": [icono("icon-192.png", 192), icono("icon-512.png", 512),
                  icono("icon-maskable-512.png", 512, "maskable")],
    }


@bp.route("/favicon.ico")
def favicon():
    """Navegadores y Google piden el ícono en la raíz aunque el HTML indique otra ruta."""
    return send_from_directory(current_app.static_folder, "img/favicon.ico", max_age=60 * 60 * 24 * 30)


@bp.app_errorhandler(404)
def no_encontrado(_e):
    return render_template("public/404.html"), 404


@bp.app_errorhandler(413)
def muy_grande(_e):
    return f"La foto supera el tamaño máximo permitido ({current_app.config['MAX_UPLOAD_MB']} MB).", 413
