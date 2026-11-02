"""Gestión de usuarios (solo super admin): restablecer contraseña y desbloquear al admin."""
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.extensions import db
from app.models import Usuario
from app.utils.db import obtener_o_404

from . import bp, solo_superadmin

LARGO_MINIMO = 8


@bp.route("/usuarios")
@solo_superadmin
def usuarios():
    return render_template("admin/usuarios.html",
                           usuarios=Usuario.query.order_by(Usuario.rol, Usuario.username).all())


@bp.route("/usuarios/<int:id>/password", methods=["POST"])
@solo_superadmin
def usuario_password(id):
    user = obtener_o_404(Usuario, id)
    if user.id == current_user.id:
        flash("Para tu propia cuenta usa “Mi contraseña”.", "error")
        return redirect(url_for("admin.usuarios"))
    nueva, confirmar = request.form.get("nueva", ""), request.form.get("confirmar", "")
    if len(nueva) < LARGO_MINIMO:
        flash(f"La contraseña debe tener al menos {LARGO_MINIMO} caracteres.", "error")
    elif nueva != confirmar:
        flash("Las contraseñas no coinciden.", "error")
    else:
        user.set_password(nueva)  # también cierra sus sesiones abiertas
        user.desbloquear()
        db.session.commit()
        flash(f"Contraseña de “{user.username}” actualizada. Sus sesiones abiertas se cerraron.", "ok")
    return redirect(url_for("admin.usuarios"))


@bp.route("/usuarios/<int:id>/desbloquear", methods=["POST"])
@solo_superadmin
def usuario_desbloquear(id):
    user = obtener_o_404(Usuario, id)
    user.desbloquear()
    db.session.commit()
    flash(f"“{user.username}” fue desbloqueado.", "ok")
    return redirect(url_for("admin.usuarios"))
