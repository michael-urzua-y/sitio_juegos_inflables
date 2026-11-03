"""
Panel de administración en /admin.

- Todas las rutas requieren login salvo /admin/login.
- Una sola sesión activa por usuario: al entrar desde otro equipo, la anterior se cierra.
  Además la sesión queda atada a la IP y navegador donde se inició (app/security.py).
- Las rutas marcadas con @solo_superadmin solo las ve el equipo de desarrollo.
- El menú se arma desde MENU según el rol del usuario.
"""
from functools import wraps

from flask import Blueprint, flash, g, redirect, request, session, url_for
from flask_login import current_user, logout_user

from app.extensions import login_manager
from app.security import sesion_del_mismo_equipo

bp = Blueprint("admin", __name__, url_prefix="/admin")

RUTAS_PUBLICAS = {"admin.login"}

# (endpoint, texto, ícono, endpoints que lo marcan activo, solo super admin, argumentos de url_for)
MENU = [
    ("admin.dashboard", "Juegos", "list", {"admin.dashboard", "admin.juego_editar", "admin.juego_nuevo"}, False, {}),
    ("admin.contacto", "Contacto y redes", "phone", {"admin.contacto"}, False, {}),
    ("admin.contenido", "Contenido portada", "star", {"admin.contenido"}, True, {"tipo": "faq"}),
    ("admin.textos", "Textos del sitio", "sparkles", {"admin.textos"}, True, {}),
    ("admin.categorias", "Categorías", "target", {"admin.categorias", "admin.categoria_nueva", "admin.categoria_editar"}, True, {}),
    ("admin.usuarios", "Usuarios", "users", {"admin.usuarios"}, True, {}),
    ("admin.password", "Mi contraseña", "shield", {"admin.password"}, False, {}),
]


def solo_superadmin(vista):
    """Restringe una vista al super admin; el admin vuelve al inicio del panel con un aviso."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not getattr(current_user, "es_superadmin", False):
            if request.is_json:
                return {"error": "No tienes permiso para esta acción."}, 403
            flash("No tienes permiso para acceder a esa sección.", "error")
            return redirect(url_for("admin.dashboard"))
        return vista(*args, **kwargs)
    return envoltura


@bp.before_request
def requiere_login():
    if current_user.is_authenticated:
        if sesion_del_mismo_equipo():
            return None
        logout_user()
        session.clear()
        flash("Por seguridad se cerró la sesión: se detectó un cambio de red o navegador.", "info")
        return redirect(url_for("admin.login"))
    if g.pop("sesion_reemplazada", False):
        flash("Tu sesión se cerró porque se inició sesión con tu usuario en otro equipo.", "info")
        if request.endpoint not in RUTAS_PUBLICAS:
            return redirect(url_for("admin.login"))
    if request.endpoint not in RUTAS_PUBLICAS:
        return login_manager.unauthorized()


@bp.context_processor
def menu_admin():
    if not current_user.is_authenticated:
        return {"menu": []}
    visibles = [m for m in MENU if current_user.es_superadmin or not m[4]]
    return {"menu": visibles}


from . import ajustes, auth, categorias, contenido, juegos, usuarios  # noqa: E402,F401
