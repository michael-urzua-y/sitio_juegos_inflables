from urllib.parse import urlparse

from flask import flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.models import Usuario

from . import bp


def _url_interna(destino):
    return bool(destino) and destino.startswith("/") and not urlparse(destino).netloc


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        user, error = Usuario.autenticar(
            request.form.get("username", "").strip()[:80], request.form.get("password", "")[:200]
        )
        if user:
            destino = request.args.get("next")
            session.clear()  # evita fijación de sesión
            session.permanent = True
            login_user(user, remember=bool(request.form.get("recordar")))
            return redirect(destino if _url_interna(destino) else url_for("admin.dashboard"))
        flash(error, "error")
    return render_template("admin/login.html")


@bp.route("/logout", methods=["POST"])
def logout():
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
