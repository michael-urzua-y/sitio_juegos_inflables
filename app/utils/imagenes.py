"""
Procesa imágenes subidas: valida el contenido real, corrige orientación, elimina
metadatos y genera varias versiones livianas para usar con <picture> + srcset:
  - AVIF: el formato más liviano (~50% menos que WebP), lo usan los navegadores modernos.
  - WebP: respaldo para navegadores que no soportan AVIF.
La tarjeta para redes sociales se genera aparte (services/tarjetas.py).

Se guardan en disco (volumen Docker), no en la BD: un BLOB/base64 pesa más,
no se puede cachear por el navegador y hace más lenta la base de datos.
"""
import mimetypes
import os
import uuid

from flask import current_app
from PIL import Image, ImageOps, UnidentifiedImageError

EXTENSIONES = {"jpg", "jpeg", "png", "webp"}
FORMATOS_PIL = {"JPEG", "PNG", "WEBP", "MPO"}
ANCHOS = (480, 960, 1400)  # móvil, tarjeta en pantalla retina, detalle
# formato -> opciones de compresión (la calidad AVIF 55 se ve similar a WebP 75)
FORMATOS = {
    "avif": {"format": "AVIF", "quality": 55, "speed": 6},
    "webp": {"format": "WEBP", "quality": 75, "method": 6},
}
Image.MAX_IMAGE_PIXELS = 40_000_000  # protege contra "imágenes bomba"
mimetypes.add_type("image/avif", ".avif")


class ImagenInvalida(ValueError):
    pass


def nombre_archivo(base, ancho, ext="webp"):
    return f"{os.path.basename(base)}-{ancho}.{ext}"


def _ruta(archivo):
    return os.path.join(current_app.config["UPLOAD_DIR"], archivo)


def guardar_imagen(archivo):
    """Devuelve el identificador base de la imagen guardada o None si no se subió nada."""
    if not archivo or not archivo.filename:
        return None
    if archivo.filename.rsplit(".", 1)[-1].lower() not in EXTENSIONES:
        raise ImagenInvalida("Formato no permitido. Usa JPG, PNG o WebP.")
    try:
        img = Image.open(archivo.stream)
        if img.format not in FORMATOS_PIL:  # valida el contenido real, no solo la extensión
            raise ImagenInvalida("Formato no permitido. Usa JPG, PNG o WebP.")
        img = ImageOps.exif_transpose(img).convert("RGB")  # re-codificar elimina EXIF/GPS
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ImagenInvalida("El archivo no es una imagen válida o es demasiado grande.")

    base = uuid.uuid4().hex
    for ancho in ANCHOS:
        copia = img.copy()
        copia.thumbnail((ancho, ancho), Image.LANCZOS)
        for ext, opciones in FORMATOS.items():
            copia.save(_ruta(nombre_archivo(base, ancho, ext)), **opciones)
    return base


def borrar_imagen(base):
    if not base:
        return
    archivos = [nombre_archivo(base, a, ext) for a in ANCHOS for ext in FORMATOS]
    for archivo in archivos:
        if os.path.exists(_ruta(archivo)):
            os.remove(_ruta(archivo))
