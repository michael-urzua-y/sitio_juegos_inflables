"""
Tarjetas para compartir en redes (Open Graph 1200x630).

Cuando alguien comparte un juego o una categoría por WhatsApp, Facebook, Instagram,
X o LinkedIn, se muestra una tarjeta con la marca: logo, nombre, precio y foto.
Se generan con Pillow la primera vez y quedan en caché. El nombre del archivo
incluye un hash del contenido, así que se regeneran solas al cambiar precio,
nombre o foto (y las redes ven una URL nueva).
"""
import hashlib
import os
from functools import lru_cache
from urllib.parse import urlparse

from flask import current_app
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from app.services.ajustes import obtener as ajustes
from app.utils.imagenes import nombre_archivo
from app.services import ajustes as ajustes_srv

ANCHO, ALTO = 1200, 630
MARGEN = 72
COL_TEXTO = 570           # ancho de la columna de texto
FOTO = (440, 330)         # tamaño de la foto a la derecha
NARANJA = ((229, 32, 46), (255, 138, 0))   # rojo -> naranja del logo (= .btn--accent)
VERSION = "2"             # súbelo si cambias el diseño para invalidar la caché


# ---------- utilidades de dibujo ----------
def _static(*partes):
    return os.path.join(current_app.static_folder, *partes)


@lru_cache(maxsize=32)
def _fuente(nombre, peso, tamano):
    f = ImageFont.truetype(_static("fonts", f"{nombre}.ttf"), tamano)
    f.set_variation_by_name(peso)
    return f


def _redondear(img, radio):
    mascara = Image.new("L", img.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, *img.size), radio, fill=255)
    img.putalpha(mascara)
    return img


def _degradado(tamano, c1, c2):
    w, h = tamano
    base = Image.new("RGB", (w, 1))
    for x in range(w):
        t = x / max(w - 1, 1)
        base.putpixel((x, 0), tuple(int(a + (b - a) * t) for a, b in zip(c1, c2)))
    return base.resize(tamano)


def _envolver(texto, fuente, ancho_max, max_lineas):
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = f"{actual} {p}".strip()
        if fuente.getlength(prueba) <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    if len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]
        lineas[-1] = lineas[-1].rstrip(".,;:") + "…"
    return lineas


def _titulo_ajustado(texto):
    """Busca el tamaño más grande en que el título cabe en 3 líneas."""
    for tamano in (72, 64, 56, 48, 42):
        f = _fuente("Fredoka", "Bold", tamano)
        lineas = _envolver(texto, f, COL_TEXTO, 3)
        if not lineas[-1].endswith("…"):
            return f, lineas
    return f, lineas


def _pastilla(lienzo, xy, texto, fuente, fondo, color=(255, 255, 255), pad=(26, 14), borde=None):
    """Dibuja un rectángulo redondeado con texto. Devuelve el alto ocupado."""
    x, y = xy
    tw = fuente.getlength(texto)
    asc, desc = fuente.getmetrics()
    w, h = int(tw + pad[0] * 2), int(asc + desc + pad[1] * 2)
    if isinstance(fondo, tuple) and len(fondo) == 2 and isinstance(fondo[0], tuple):
        capa = _redondear(_degradado((w, h), *fondo).convert("RGBA"), h // 2)
        lienzo.alpha_composite(capa, (x, y))
    else:
        capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(capa).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=fondo, outline=borde, width=2)
        lienzo.alpha_composite(capa, (x, y))
    ImageDraw.Draw(lienzo).text((x + pad[0], y + pad[1]), texto, font=fuente, fill=color)
    return h


def _foto(lienzo, ruta):
    """Foto con borde blanco, esquinas redondeadas, sombra y leve rotación."""
    try:
        img = Image.open(ruta).convert("RGB")
    except OSError:
        return
    borde = 10
    foto = _redondear(ImageOps.fit(img, FOTO, Image.LANCZOS).convert("RGBA"), 24)
    marco = _redondear(Image.new("RGBA", (FOTO[0] + borde * 2, FOTO[1] + borde * 2), (255, 255, 255, 255)), 32)
    marco.alpha_composite(foto, (borde, borde))

    sombra = Image.new("RGBA", (marco.width + 120, marco.height + 120), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle((60, 80, 60 + marco.width, 80 + marco.height), 32, fill=(7, 11, 30, 150))
    sombra = sombra.filter(ImageFilter.GaussianBlur(28))

    angulo = 3
    marco = marco.rotate(-angulo, resample=Image.BICUBIC, expand=True)
    sombra = sombra.rotate(-angulo, resample=Image.BICUBIC, expand=True)
    x = ANCHO - marco.width - 48
    y = (ALTO - marco.height) // 2 + 6
    lienzo.alpha_composite(sombra, (x - 60, y - 60))
    lienzo.alpha_composite(marco, (x, y))


def _componer(etiqueta, titulo, destacado, ruta_foto):
    n = ajustes()
    lienzo = Image.open(_static("img", "og-bg.jpg")).convert("RGBA").resize((ANCHO, ALTO))
    d = ImageDraw.Draw(lienzo)

    # Marca: logo + nombre
    logo = Image.open(_static("img", "icon-192.png")).convert("RGBA").resize((100, 100), Image.LANCZOS)
    lienzo.alpha_composite(logo, (MARGEN - 8, 40))
    d.text((MARGEN + 104, 66), n["nombre"], font=_fuente("Fredoka", "SemiBold", 36), fill="white")

    # Etiqueta (categoría)
    y = 176
    y += _pastilla(lienzo, (MARGEN, y), etiqueta.upper(), _fuente("PlusJakartaSans", "Bold", 20),
                   (255, 255, 255, 34), pad=(20, 9), borde=(255, 255, 255, 90)) + 22

    # Título
    fuente, lineas = _titulo_ajustado(titulo)
    alto_linea = int(fuente.size * 1.08)
    for linea in lineas:
        d.text((MARGEN, y), linea, font=fuente, fill="white")
        y += alto_linea
    y += 18

    # Precio / dato destacado
    if destacado:
        _pastilla(lienzo, (MARGEN, y), destacado, _fuente("PlusJakartaSans", "ExtraBold", 30), NARANJA, pad=(28, 14))

    # Pie: llamada a la acción + dominio
    dominio = urlparse(n["url"]).netloc or n["url"]
    d.text((MARGEN, ALTO - 74), f"Cotiza por WhatsApp  ·  {dominio}",
           font=_fuente("PlusJakartaSans", "SemiBold", 24), fill=(255, 255, 255, 215))

    _foto(lienzo, ruta_foto)
    return lienzo.convert("RGB")


# ---------- API pública ----------
def _ruta_foto_juego(juego):
    if juego.imagen:
        return os.path.join(current_app.config["UPLOAD_DIR"], nombre_archivo(juego.imagen, 960))
    ruta = _static("img", "placeholders", f"{juego.categoria.slug}.jpg")
    return ruta if os.path.exists(ruta) else _static("img", "placeholders", "generico.jpg")


def datos_juego(juego):
    return (juego.categoria.nombre, juego.nombre, f"Arriendo desde {ajustes_srv.precio_texto(juego.precio)}",
            _ruta_foto_juego(juego))


def datos_categoria(categoria, juegos):
    con_foto = next((j for j in juegos if j.imagen), None)
    foto = _ruta_foto_juego(con_foto or juegos[0]) if juegos else _static("img", "placeholders", "generico.jpg")
    if juegos:
        minimo = min(j.precio for j in juegos)
        destacado = f"{len(juegos)} {'opción' if len(juegos) == 1 else 'opciones'} · desde {ajustes_srv.precio_texto(minimo)}"
    else:
        destacado = None
    ciudad = ajustes()["ciudad"]
    titulo = f"Arriendo de {categoria.nombre}" + (f" en {ciudad}" if ciudad else "")
    return ("Categoría", titulo, destacado, foto)


def huella(datos):
    """Hash corto del contenido: cambia si cambia cualquier dato visible de la tarjeta."""
    etiqueta, titulo, destacado, foto = datos
    marca = ajustes()["nombre"] + ajustes()["url"]
    mtime = os.path.getmtime(foto) if os.path.exists(foto) else 0
    clave = "|".join(map(str, (VERSION, marca, etiqueta, titulo, destacado, foto, mtime)))
    return hashlib.sha1(clave.encode()).hexdigest()[:12]


def archivo_tarjeta(datos):
    """Devuelve la ruta del JPG (lo genera si no está en caché)."""
    carpeta = os.path.join(current_app.instance_path, "og-cache")
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"{huella(datos)}.jpg")
    if not os.path.exists(ruta):
        tmp = ruta + ".tmp"
        _componer(*datos).save(tmp, "JPEG", quality=85, optimize=True, progressive=True)
        os.replace(tmp, ruta)  # escritura atómica (varios workers)
    return ruta
