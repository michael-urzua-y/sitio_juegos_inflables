"""Endurecimiento de seguridad: headers HTTP, CSP, chequeos de producción, errores CSRF y
sesiones atadas al equipo (IP + navegador)."""
import hashlib
import hmac
import os

from flask import current_app, flash, redirect, request, session, url_for
from flask_wtf.csrf import CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

CSP = "; ".join([
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: blob:",
    "connect-src 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "object-src 'none'",
])


def _validar_produccion(app):
    """En producción no se permite arrancar con claves por defecto."""
    if os.getenv("APP_ENV") != "production":
        return
    errores = []
    if app.config["SECRET_KEY"].startswith("dev-") or len(app.config["SECRET_KEY"]) < 32:
        errores.append("SECRET_KEY debe tener al menos 32 caracteres aleatorios.")
    for var, ejemplo in (("ADMIN_PASSWORD", "admin123"), ("SUPERADMIN_PASSWORD", "superadmin123")):
        clave = app.config[var]
        if clave in (ejemplo, "cambia-esta-clave") or len(clave) < 10:
            errores.append(f"{var} es débil (mínimo 10 caracteres y distinta a la de ejemplo).")
    if app.config["ADMIN_USER"] == app.config["SUPERADMIN_USER"]:
        errores.append("ADMIN_USER y SUPERADMIN_USER deben ser distintos.")
    if errores:
        raise RuntimeError("Configuración insegura:\n- " + "\n- ".join(errores))


# ---------- Sesión atada al equipo ----------
# Flask-Login trae algo parecido ("strong"), pero con sesiones permanentes no la cierra y
# confía en la cabecera X-Forwarded-For, que cualquiera puede falsificar. Aquí se usa
# request.remote_addr, que solo se corrige con ProxyFix cuando TRUST_PROXY=1.
def _huella():
    datos = f"{request.remote_addr}|{request.headers.get('User-Agent', '')}"
    return hmac.new(current_app.secret_key.encode(), datos.encode(), hashlib.sha256).hexdigest()


def sellar_sesion():
    """Se llama al iniciar sesión: guarda la huella del equipo actual."""
    session["huella"] = _huella()


def sesion_del_mismo_equipo():
    """False si la cookie de sesión se está usando desde otra IP o navegador."""
    if not current_app.config["SESION_ATADA_IP"]:
        return True
    if "huella" not in session:  # sesión restaurada con la cookie "recordarme"
        sellar_sesion()
        return True
    return hmac.compare_digest(session["huella"], _huella())


def init_security(app):
    _validar_produccion(app)

    if os.getenv("TRUST_PROXY", "0") == "1":
        # Detrás de Nginx/Traefik/Cloudflare: respeta X-Forwarded-Proto para HTTPS
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    @app.after_request
    def headers(resp):
        h = resp.headers
        h.setdefault("Content-Security-Policy", CSP)
        h.setdefault("X-Content-Type-Options", "nosniff")
        h.setdefault("X-Frame-Options", "DENY")
        h.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        h.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        h.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        if app.config["SESSION_COOKIE_SECURE"]:
            h.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        if request.blueprint == "admin":
            h["Cache-Control"] = "no-store"
        return resp

    @app.errorhandler(CSRFError)
    def csrf_error(_e):
        if request.is_json:
            return {"error": "La sesión expiró. Recarga la página e intenta nuevamente."}, 400
        flash("La sesión del formulario expiró. Intenta nuevamente.", "error")
        return redirect(request.referrer or url_for("admin.login"))
