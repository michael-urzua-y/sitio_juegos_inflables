from flask import abort, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Bloque
from app.models.bloque import TIPOS
from app.models.categoria import ICONOS
from app.services.contenido import bloques_por_tipo
from app.utils.db import obtener_o_404
from app.utils.formularios import asignar_textos
from app.utils.texto import a_entero

from . import bp, solo_superadmin


def _tipo_valido(tipo):
    return tipo if tipo in TIPOS else abort(404)


@bp.route("/contenido/<tipo>", methods=["GET", "POST"])
@solo_superadmin
def contenido(tipo):
    _tipo_valido(tipo)
    if request.method == "POST":
        f = request.form
        bloque = obtener_o_404(Bloque, f.get("id", type=int)) if f.get("id") else Bloque(tipo=tipo)
        asignar_textos(bloque, f, Bloque.CAMPOS_TEXTO)
        if not bloque.titulo:
            flash("El campo principal es obligatorio.", "error")
        else:
            bloque.icono = f.get("icono") if f.get("icono") in ICONOS else ""
            bloque.orden = max(-999, min(a_entero(f.get("orden")), 999))
            bloque.activo = "activo" in f
            db.session.add(bloque)
            db.session.commit()
            flash("Contenido guardado.", "ok")
        return redirect(url_for("admin.contenido", tipo=tipo))
    return render_template("admin/contenido.html", tipo=tipo, tipos=TIPOS, cfg=TIPOS[tipo],
                           bloques=bloques_por_tipo(solo_activos=False)[tipo], iconos=ICONOS)


@bp.route("/contenido/<tipo>/<int:id>/eliminar", methods=["POST"])
@solo_superadmin
def contenido_eliminar(tipo, id):
    bloque = obtener_o_404(Bloque, id)
    db.session.delete(bloque)
    db.session.commit()
    flash("Contenido eliminado.", "ok")
    return redirect(url_for("admin.contenido", tipo=_tipo_valido(tipo)))
