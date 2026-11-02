from flask import flash, redirect, render_template, request, url_for

from app.services import ajustes as servicio

from . import bp, solo_superadmin


def _pagina(grupos, endpoint, titulo, ayuda=None):
    """Formulario de ajustes reutilizable: solo guarda los campos de los grupos indicados."""
    if request.method == "POST":
        servicio.guardar(request.form, grupos)
        flash(f"{titulo}: cambios guardados.", "ok")
        return redirect(url_for(endpoint))
    return render_template("admin/ajustes.html", grupos=grupos, valores=servicio.editables(),
                           titulo=titulo, ayuda=ayuda)


@bp.route("/contacto", methods=["GET", "POST"])
def contacto():
    return _pagina(servicio.GRUPOS_CONTACTO, "admin.contacto", "Contacto y redes",
                   "Los enlaces deben comenzar con https://. Los valores inválidos se descartan.")


@bp.route("/textos", methods=["GET", "POST"])
@solo_superadmin
def textos():
    return _pagina(servicio.GRUPOS_TEXTOS, "admin.textos", "Textos del sitio",
                   "Encierra entre *asteriscos* la palabra del título que quieras destacar con degradado.")
