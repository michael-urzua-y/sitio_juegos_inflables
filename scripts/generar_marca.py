"""
Genera todos los recursos de marca a partir del logo original.

Uso (desde la raíz del proyecto):
    python scripts/generar_marca.py                 # usa marca/logo-original.png
    python scripts/generar_marca.py otro-logo.png   # si cambia el logo

Crea en app/static/img/:
    logo-128.webp, logo-320.webp   logo con fondo transparente (header, footer, admin)
    favicon.ico, favicon-32.png    pestaña del navegador
    apple-touch-icon.png           ícono al "agregar a inicio" en iPhone (fondo oscuro)
    icon-192.png, icon-512.png     PWA, Google (Schema.org) y tarjetas para redes
    icon-maskable-512.png          ícono Android con margen de seguridad
    og-bg.jpg, og-default.jpg      fondo y tarjeta por defecto para compartir en redes

El logo viene sobre negro. Se quita el fondo negro que toca los bordes (relleno por
inundación) y el brillo neón que lo rodea se convierte en transparencia ("color a
alfa"), así se ve bien tanto sobre blanco como sobre el footer oscuro. El negro del
interior del logo (toro, siluetas, contornos) se mantiene.
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(RAIZ, "marca", "logo-original.png")
DESTINO = os.path.join(RAIZ, "app", "static", "img")
FUENTES = os.path.join(RAIZ, "app", "static", "fonts")

LADO_TRABAJO = 1024   # se procesa a este tamaño (todos los recursos son menores)
UMBRAL_FONDO = 48     # brillo máximo (0-255) que se considera "fondo negro"
NOCHE = (7, 11, 30)   # --night en core.css: fondo oscuro de la marca

# Paleta del logo (mantener en sincronía con los tokens de core.css)
AZUL, ROJO, AMARILLO, NARANJA = (29, 78, 216), (229, 32, 46), (255, 200, 30), (255, 138, 0)


# ---------- recorte del fondo ----------
def quitar_fondo(img):
    """Devuelve el logo RGBA con el fondo negro exterior transparente."""
    img = img.convert("RGB")
    r, g, b = img.split()
    brillo = ImageChops.lighter(ImageChops.lighter(r, g), b)

    # 1) Fondo = píxeles oscuros conectados con los bordes de la imagen.
    oscuro = brillo.point(lambda v: 255 if v <= UMBRAL_FONDO else 0)
    w, h = img.size
    for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if oscuro.getpixel((x, y)) == 255:
            ImageDraw.floodfill(oscuro, (x, y), 128)
    fondo = oscuro.point(lambda v: 255 if v == 128 else 0)

    # 2) Franja de brillo alrededor del fondo: ahí se aplica "color a alfa".
    franja = fondo.filter(ImageFilter.MaxFilter(9))

    px, pb, pf = img.load(), brillo.load(), franja.load()
    salida = Image.new("RGBA", img.size)
    po = salida.load()
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if not pf[x, y]:
                po[x, y] = (*c, 255)
                continue
            a = pb[x, y]
            if a == 0:
                po[x, y] = (0, 0, 0, 0)
                continue
            # quita el negro "premultiplicado" para que el brillo no quede sucio
            po[x, y] = (*(min(255, v * 255 // a) for v in c), a)
    return salida.crop(salida.getbbox())


def cuadrar(img, margen=0.0, fondo=(0, 0, 0, 0)):
    """Centra el logo en un lienzo cuadrado con `margen` (fracción del lado)."""
    lado = int(max(img.size) / (1 - 2 * margen))
    lienzo = Image.new("RGBA", (lado, lado), fondo)
    lienzo.alpha_composite(img, ((lado - img.width) // 2, (lado - img.height) // 2))
    return lienzo


def tam(img, lado):
    return img.resize((lado, lado), Image.LANCZOS)


# ---------- imágenes para redes ----------
def _resplandor(lienzo, centro, radio, color, opacidad):
    capa = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    cx, cy = centro
    ImageDraw.Draw(capa).ellipse((cx - radio, cy - radio, cx + radio, cy + radio), fill=(*color, opacidad))
    lienzo.alpha_composite(capa.filter(ImageFilter.GaussianBlur(radio // 2)))


def fondo_redes(ancho=1200, alto=630):
    """Noche con luces de feria (azul, rojo y amarillo del logo) y puntos sutiles."""
    lienzo = Image.new("RGBA", (ancho, alto), (*NOCHE, 255))
    _resplandor(lienzo, (ancho + 40, -60), 420, AZUL, 200)
    _resplandor(lienzo, (-60, alto + 40), 380, ROJO, 170)
    _resplandor(lienzo, (ancho // 2, alto + 160), 300, NARANJA, 110)
    puntos = ImageDraw.Draw(lienzo)
    for y in range(11, alto, 22):
        for x in range(11, ancho, 22):
            puntos.point((x, y), fill=(255, 255, 255, 40))
    return lienzo


def _fuente(nombre, peso, tamano):
    f = ImageFont.truetype(os.path.join(FUENTES, f"{nombre}.ttf"), tamano)
    f.set_variation_by_name(peso)
    return f


def tarjeta_por_defecto(fondo, logo):
    """Tarjeta OG genérica: logo grande + mensaje principal."""
    lienzo = fondo.copy()
    lienzo.alpha_composite(tam(logo, 520), (630, 55))
    d = ImageDraw.Draw(lienzo)
    titulo = _fuente("Fredoka", "Bold", 76)
    d.text((72, 150), "Entretención", font=titulo, fill="white")
    d.text((72, 236), "para tu evento", font=titulo, fill=AMARILLO)
    d.text((72, 340), "Juegos inflables · Toro mecánico\nElectrónicos · Destreza y mucho más",
           font=_fuente("PlusJakartaSans", "SemiBold", 28), fill=(255, 255, 255, 220), spacing=12)
    boton = _fuente("PlusJakartaSans", "ExtraBold", 28)
    texto = "Cotiza por WhatsApp"
    ancho = int(d.textlength(texto, font=boton))
    d.rounded_rectangle((72, 470, 72 + ancho + 56, 470 + 64), 32, fill=NARANJA)
    d.text((72 + 28, 470 + 15), texto, font=boton, fill="white")
    return lienzo


# ---------- principal ----------
def main(origen=ORIGEN):
    original = Image.open(origen)
    original.thumbnail((LADO_TRABAJO, LADO_TRABAJO), Image.LANCZOS)
    logo = cuadrar(quitar_fondo(original))
    guardar = lambda img, nombre, **kw: img.save(os.path.join(DESTINO, nombre), **kw) or print("  ✓", nombre)

    print("Generando recursos de marca en", os.path.relpath(DESTINO, RAIZ))
    for lado in (128, 320):
        guardar(tam(logo, lado), f"logo-{lado}.webp", quality=90, method=6)
    guardar(tam(logo, 32), "favicon-32.png", optimize=True)
    guardar(logo, "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    for lado in (192, 512):
        guardar(tam(logo, lado), f"icon-{lado}.png", optimize=True)

    # iOS y Android "maskable" no aceptan transparencia: fondo noche + margen
    con_fondo = cuadrar(logo, margen=0.06, fondo=(*NOCHE, 255))
    guardar(tam(con_fondo, 180).convert("RGB"), "apple-touch-icon.png", optimize=True)
    guardar(tam(cuadrar(logo, margen=0.12, fondo=(*NOCHE, 255)), 512).convert("RGB"),
            "icon-maskable-512.png", optimize=True)

    fondo = fondo_redes()
    guardar(fondo.convert("RGB"), "og-bg.jpg", quality=88, optimize=True, progressive=True)
    guardar(tarjeta_por_defecto(fondo, logo).convert("RGB"), "og-default.jpg",
            quality=88, optimize=True, progressive=True)


if __name__ == "__main__":
    main(*sys.argv[1:2])
