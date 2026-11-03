"""
Identidad visual (la mantiene el equipo de desarrollo, no el cliente).

Los archivos del logo se generan con `python scripts/generar_marca.py` a partir de
marca/logo-original.png. Los colores del sitio están en los tokens de
app/static/css/core.css; aquí solo va lo que usa Python/HTML fuera del CSS.
"""
MARCA = {
    # Barra del navegador en móviles y fondo del ícono instalado (= --night en core.css)
    "color_tema": "#070B1E",
    "logo": "img/logo-128.webp",          # header y panel admin (se muestra a ≤64 px)
    "logo_grande": "img/logo-320.webp",   # footer y login (se muestra a ≤160 px)
}
