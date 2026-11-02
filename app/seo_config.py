"""
Configuración SEO interna — la mantiene el equipo de desarrollo (Monay Solutions),
NO el cliente desde el panel admin.

Se usa en: títulos de página, meta descripción, Schema.org (knowsAbout, dirección),
llms.txt (para IAs) y tarjetas para redes sociales.
Los códigos de verificación dependen del despliegue, por eso van en el .env.
"""
import os
import re


def _token(nombre):
    """Lee un código de verificación del entorno, permitiendo solo caracteres seguros."""
    return re.sub(r"[^A-Za-z0-9_\-]", "", os.getenv(nombre, ""))[:100]


SEO = {
    # Título de la portada (pestaña del navegador y resultado de Google)
    "seo_titulo": "Arriendo de juegos inflables en Santiago",

    # Lo que la gente busca. Primero lo más importante.
    "seo_palabras_clave": ", ".join([
        "arriendo de juegos inflables", "juegos inflables", "castillos inflables", "toboganes inflables",
        "juegos mecánicos", "juegos mecanizados", "toro mecánico", "reloj derribador",
        "juegos interactivos", "zona infantil", "piscina de pelotas",
        "juegos electrónicos", "simulador de carreras", "máquina de baile",
        "juegos de salón", "mesa de pool", "taca taca", "ping pong", "arcade",
        "juegos típicos chilenos", "juegos para fiestas patrias", "rayuela",
        "juegos de agua", "juegos acuáticos", "tobogán acuático",
        "juegos para cumpleaños", "juegos para eventos", "entretención para empresas",
    ]),

    # Descripción para Google y redes (ideal: menos de 160 caracteres)
    "seo_descripcion": (
        "Arriendo de juegos inflables, mecánicos, interactivos, electrónicos, de salón, "
        "típicos y de agua para cumpleaños y eventos en Santiago. Instalación incluida."
    ),

    # Ubicación (títulos "Arriendo de X en {ciudad}" y dirección en Schema.org)
    "ciudad": "Santiago",
    "region": "Región Metropolitana",

    # Verificación de propiedad: Google Search Console, Bing Webmaster Tools y Meta
    "google_verificacion": _token("GOOGLE_VERIFICACION"),
    "bing_verificacion": _token("BING_VERIFICACION"),
    "facebook_verificacion": _token("FACEBOOK_VERIFICACION"),
}
