from urllib.parse import urlparse

from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.models import Usuario
from app.security import sellar_sesion
from app.utils.limite import intentos_login

from . import bp


def _url_interna(destino):
    return bool(destino) and destino.startswith("/") and not urlparse(destino).netloc


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        ip = request.remote_addr or "?"
        if intentos_login.bloqueada(ip):
            flash("Demasiados intentos desde esta conexión. Espera unos minutos e intenta nuevamente.", "error")
            return render_template("admin/login.html"), 429
        user, error = Usuario.autenticar(
            request.form.get("username", "").strip()[:80], request.form.get("password", "")[:200]
        )
        if not user:
            intentos_login.fallo(ip)
        else:
            intentos_login.limpiar(ip)
            destino = request.args.get("next")
            session.clear()  # evita fijación de sesión
            session.permanent = True
            login_user(user, remember=bool(request.form.get("recordar")))
            sellar_sesion()
            return redirect(destino if _url_interna(destino) else url_for("admin.dashboard"))
        flash(error, "error")
    return render_template("admin/login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    current_user.nueva_sesion()  # invalida también la cookie "recordarme" de este equipo
    db.session.commit()
    logout_user()
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("admin.login"))


@bp.route("/password", methods=["GET", "POST"])
def password():
    if request.method == "POST":
        f = request.form
        error = (
            "La contraseña actual no es correcta." if not current_user.check_password(f.get("actual", ""))
            else "La nueva contraseña debe tener al menos 8 caracteres." if len(f.get("nueva", "")) < 8
            else "Las contraseñas no coinciden." if f.get("nueva") != f.get("confirmar")
            else None
        )
        if error:
            flash(error, "error")
        else:
            current_user.set_password(f["nueva"])
            db.session.commit()
            login_user(current_user._get_current_object())  # renueva la sesión con la nueva versión
            flash("Contraseña actualizada. Las demás sesiones fueron cerradas.", "ok")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/password.html")
