"""
Procesamiento de fotos subidas desde el admin.

El cliente puede subir CUALQUIER foto (JPG, PNG, HEIC de iPhone, WebP, AVIF, GIF, BMP,
TIFF) y el sistema la deja lista para todas las tarjetas del sitio, que usan formato 4:3:

1. Valida el contenido real del archivo (no la extensión) y lo abre de forma segura.
2. Corrige la orientación de fotos de celular, convierte el color a sRGB y pone las
   transparencias sobre fondo blanco.
3. Encuadra a 4:3:
   - foto casi horizontal  -> recorte suave al centro;
   - vertical / cuadrada / panorámica -> foto COMPLETA sobre un fondo difuminado de
     sí misma (no se corta el juego).
4. Genera 3 tamaños (480, 960, 1400 px), cada uno desde la original para no perder
   calidad, con un enfoque suave, en AVIF (más liviano) y WebP (respaldo).

Se guardan en disco (volumen Docker), no en la BD: un BLOB pesa más, no se cachea en el
navegador y hace más lenta la base de datos. La tarjeta para redes se genera aparte
(services/tarjetas.py).
"""
import io
import mimetypes
import os
import uuid

from flask import current_app
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, UnidentifiedImageError

try:  # Fotos HEIC/HEIF de iPhone
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:  # pragma: no cover - el sitio funciona igual, solo sin HEIC
    pass

FORMATOS_PIL = {"JPEG", "MPO", "PNG", "WEBP", "AVIF", "HEIF", "GIF", "BMP", "TIFF"}
ANCHOS = (480, 960, 1400)            # móvil, tarjeta en pantalla retina, detalle
PROPORCION = 4 / 3                   # formato de todas las tarjetas del sitio
RECORTE_MIN, RECORTE_MAX = 1.2, 1.5  # en este rango se recorta; fuera, se muestra completa
ANCHO_RECOMENDADO = 1200             # bajo esto se avisa que podría verse borrosa
LADO_TRABAJO = 2800                  # se reduce primero a esto (rapidez y memoria)
FORMATOS = {
    "avif": {"format": "AVIF", "quality": 62, "speed": 6},
    "webp": {"format": "WEBP", "quality": 82, "method": 6},
}
Image.MAX_IMAGE_PIXELS = 130_000_000  # admite fotos de 108 MP; bloquea "imágenes bomba"
mimetypes.add_type("image/avif", ".avif")


class ImagenInvalida(ValueError):
    pass


def nombre_archivo(base, ancho, ext="webp"):
    return f"{os.path.basename(base)}-{ancho}.{ext}"


def _ruta(archivo):
    return os.path.join(current_app.config["UPLOAD_DIR"], archivo)


# ---------- preparación ----------
def _abrir(archivo):
    try:
        img = Image.open(archivo.stream)
        if img.format not in FORMATOS_PIL:
            raise ImagenInvalida("Ese archivo no es una foto compatible. Prueba con una foto JPG, PNG o de tu celular.")
        if img.format == "JPEG":
            img.draft("RGB", (LADO_TRABAJO, LADO_TRABAJO))  # decodifica más rápido fotos enormes
        img.seek(0)                                          # GIF animado: primer cuadro
        img = ImageOps.exif_transpose(img)                   # orientación de fotos de celular
        img.load()
        return img
    except ImagenInvalida:
        raise
    except Image.DecompressionBombError:
        raise ImagenInvalida("La foto tiene demasiados píxeles. Usa una de menos de 100 megapíxeles.")
    except (UnidentifiedImageError, OSError, ValueError, EOFError):
        raise ImagenInvalida("No pudimos leer el archivo. Asegúrate de que sea una foto y no esté dañada.")


def _a_srgb(img):
    """Convierte perfiles de color (p. ej. Display P3 de iPhone) a sRGB para que los
    colores se vean iguales en todos los navegadores."""
    icc = img.info.get("icc_profile")
    if not icc:
        return img
    try:
        from PIL import ImageCms
        origen = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        modo = "RGBA" if img.mode in ("RGBA", "LA", "PA") else "RGB"
        return ImageCms.profileToProfile(img.convert(modo), origen, ImageCms.createProfile("sRGB"),
                                         outputMode=modo)
    except Exception:  # perfil dañado o no soportado: se usa la imagen tal cual
        return img


def _aplanar(img):
    """Transparencias sobre fondo blanco (si no, quedarían negras)."""
    if img.mode in ("RGBA", "LA", "PA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        fondo = Image.new("RGB", img.size, (255, 255, 255))
        fondo.paste(img, mask=img.getchannel("A"))
        return fondo
    return img.convert("RGB")


def preparar(img):
    img = _aplanar(_a_srgb(img))
    img.thumbnail((LADO_TRABAJO, LADO_TRABAJO), Image.LANCZOS)
    return img


# ---------- encuadre 4:3 ----------
def _escalar(img, tamano):
    return img.resize(tamano, Image.LANCZOS, reducing_gap=3.0)


def encuadrar(img, ancho):
    """Devuelve la foto en 4:3 de `ancho` px, sin deformarla."""
    alto = round(ancho / PROPORCION)
    w, h = img.size
    relacion = w / h
    if RECORTE_MIN <= relacion <= RECORTE_MAX:
        # Casi horizontal: recorte mínimo al centro (un poco más arriba, donde suele estar el juego)
        return ImageOps.fit(img, (ancho, alto), Image.LANCZOS, centering=(0.5, 0.45))

    # Vertical, cuadrada o panorámica: foto completa sobre fondo difuminado de sí misma
    fondo = ImageOps.fit(img, (max(ancho // 10, 1), max(alto // 10, 1)), Image.BILINEAR)
    fondo = _escalar(fondo, (ancho, alto)).filter(ImageFilter.GaussianBlur(ancho / 40))
    fondo = ImageEnhance.Brightness(fondo).enhance(0.82)
    escala = min(ancho / w, alto / h)
    frente = _escalar(img, (max(round(w * escala), 1), max(round(h * escala), 1)))
    fondo.paste(frente, ((ancho - frente.width) // 2, (alto - frente.height) // 2))
    return fondo


def _enfocar(img, original_ancho, ancho):
    """Enfoque suave solo al reducir (compensa la pérdida de nitidez del redimensionado)."""
    if original_ancho > ancho * 1.2:
        return img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=60, threshold=2))
    return img


# ---------- API ----------
def guardar_imagen(archivo):
    """Procesa y guarda la foto. Devuelve (identificador, aviso) o (None, None) si no se subió nada.
    `aviso` es un texto para el admin cuando la foto es pequeña (puede verse borrosa)."""
    if not archivo or not archivo.filename:
        return None, None
    img = preparar(_abrir(archivo))
    ancho_original = img.width

    base = uuid.uuid4().hex
    for ancho in ANCHOS:
        version = _enfocar(encuadrar(img, ancho), ancho_original, ancho)
        for ext, opciones in FORMATOS.items():
            version.save(_ruta(nombre_archivo(base, ancho, ext)), **opciones)

    aviso = None
    if ancho_original < ANCHO_RECOMENDADO:
        aviso = (f"La foto es pequeña ({img.width}×{img.height} px) y podría verse poco nítida en "
                 f"pantallas grandes. Si puedes, súbela en mejor calidad (ideal: {ANCHO_RECOMENDADO} px de ancho o más).")
    return base, aviso


def borrar_imagen(base):
    if not base:
        return
    for archivo in (nombre_archivo(base, a, ext) for a in ANCHOS for ext in FORMATOS):
        if os.path.exists(_ruta(archivo)):
            os.remove(_ruta(archivo))
