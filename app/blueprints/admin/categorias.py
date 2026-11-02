from flask import flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Categoria
from app.models.categoria import ICONOS
from app.services import catalogo
from app.utils.db import obtener_o_404
from app.utils.formularios import asignar_textos
from app.utils.texto import recortar, slug_unico

from . import bp, solo_superadmin


@bp.route("/categorias")
@solo_superadmin
def categorias():
    return render_template("admin/categorias.html")


# ---------- lógica compartida (página de categorías y select del formulario de juegos) ----------
def _preparar_nueva(cat, nombre):
    cat.slug = slug_unico(Categoria, nombre)
    cat.orden = len(catalogo.categorias()) + 1  # las nuevas van al final
    cat.icono = cat.icono or "star"


def _nombre_repetido(nombre, excluir_id=None):
    q = Categoria.query.filter(db.func.lower(Categoria.nombre) == nombre.lower())
    if excluir_id:
        q = q.filter(Categoria.id != excluir_id)
    return q.first() is not None


def _eliminar(cat):
    """Elimina la categoría si no tiene juegos. Devuelve un mensaje de error o None."""
    n = cat.juegos.count()
    if n:
        return f"“{cat.nombre}” tiene {n} {'juego' if n == 1 else 'juegos'}. Muévelos a otra categoría antes de quitarla."
    db.session.delete(cat)
    db.session.commit()
    return None


def _guardar(cat):
    f = request.form
    nombre = recortar(f.get("nombre"), 120)
    if not nombre:
        flash("El nombre es obligatorio.", "error")
        return False
    if _nombre_repetido(nombre, cat.id):
        flash(f"Ya existe una categoría llamada “{nombre}”.", "error")
        return False
    if not cat.id:
        _preparar_nueva(cat, nombre)
    cat.nombre = nombre
    asignar_textos(cat, f, ("descripcion",))
    cat.icono = f.get("icono") if f.get("icono") in ICONOS else "star"
    db.session.add(cat)
    db.session.commit()
    return True


def _formulario(cat, accion):
    if request.method == "POST" and _guardar(cat):
        flash(f"Categoría “{cat.nombre}” {accion}.", "ok")
        return redirect(url_for("admin.categorias"))
    return render_template("admin/categoria_form.html", cat=cat, iconos=ICONOS)


@bp.route("/categorias/nueva", methods=["GET", "POST"])
@solo_superadmin
def categoria_nueva():
    return _formulario(Categoria(icono="star"), "creada")


@bp.route("/categorias/<int:id>", methods=["GET", "POST"])
@solo_superadmin
def categoria_editar(id):
    return _formulario(obtener_o_404(Categoria, id), "actualizada")


@bp.route("/categorias/<int:id>/mover", methods=["POST"])
@solo_superadmin
def categoria_mover(id):
    """Sube o baja una categoría una posición y renumera el orden (1, 2, 3…)."""
    cats = catalogo.categorias()
    actual = obtener_o_404(Categoria, id)
    i = cats.index(actual)
    j = i - 1 if request.form.get("direccion") == "arriba" else i + 1
    if 0 <= j < len(cats):
        cats[i], cats[j] = cats[j], cats[i]
        for pos, c in enumerate(cats, start=1):
            c.orden = pos
        db.session.commit()
    return redirect(url_for("admin.categorias"))


@bp.route("/categorias/<int:id>/eliminar", methods=["POST"])
@solo_superadmin
def categoria_eliminar(id):
    cat = obtener_o_404(Categoria, id)
    nombre = cat.nombre
    error = _eliminar(cat)
    flash(error or f"Categoría “{nombre}” eliminada.", "error" if error else "ok")
    return redirect(url_for("admin.categorias"))


# ---------- acciones rápidas desde el select del formulario de juegos (JSON, también para el admin) ----------
@bp.route("/categorias/rapida", methods=["POST"])
def categoria_rapida():
    nombre = recortar((request.get_json(silent=True) or {}).get("nombre"), 120)
    if not nombre:
        return {"error": "Escribe un nombre para la categoría."}, 400
    if _nombre_repetido(nombre):
        return {"error": f"Ya existe una categoría llamada “{nombre}”."}, 400
    cat = Categoria(nombre=nombre, descripcion="")
    _preparar_nueva(cat, nombre)
    db.session.add(cat)
    db.session.commit()
    return {"id": cat.id, "nombre": cat.nombre}, 201


@bp.route("/categorias/<int:id>/quitar", methods=["POST"])
def categoria_quitar(id):
    cat = obtener_o_404(Categoria, id)
    error = _eliminar(cat)
    return ({"error": error}, 400) if error else {"ok": True}
