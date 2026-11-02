from flask import flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models import Categoria, Juego
from app.services import catalogo
from app.utils.imagenes import ImagenInvalida, borrar_imagen, guardar_imagen
from app.utils.db import obtener_o_404
from app.utils.plantillas import url_listado
from app.utils.formularios import asignar_textos
from app.utils.texto import a_entero, slug_unico

from . import bp


def _volver_al_listado():
    return redirect(url_listado("admin.dashboard", **_filtros()))


POR_PAGINA_ADMIN = 10


def _filtros():
    """Filtros actuales del listado (se conservan al paginar, editar o eliminar)."""
    return {
        "categoria": request.values.get("categoria", type=int),
        "q": request.values.get("q", "").strip()[:60],
        "pagina": request.values.get("pagina", 1, type=int),
    }


@bp.route("/")
def dashboard():
    f = _filtros()
    paginacion = catalogo.buscar(categoria_id=f["categoria"], texto=f["q"], pagina=f["pagina"],
                                 por_pagina=POR_PAGINA_ADMIN, solo_activos=False)
    total = catalogo.total_juegos()
    return render_template("admin/dashboard.html", paginacion=paginacion, filtros=f,
                           total=total, activos=catalogo.total_activos())


def _guardar(juego):
    """Valida y guarda el formulario. Devuelve True si se guardó."""
    f = request.form
    nombre = f.get("nombre", "").strip()[:150]
    categoria_id = f.get("categoria_id", type=int)
    if not nombre or not categoria_id or not db.session.get(Categoria, categoria_id):
        flash("Nombre y categoría son obligatorios.", "error")
        return False
    try:
        nueva_imagen = guardar_imagen(request.files.get("imagen"))
    except ImagenInvalida as e:
        flash(str(e), "error")
        return False

    if juego.nombre != nombre:
        juego.slug = slug_unico(Juego, nombre, juego.id)
    juego.nombre = nombre
    juego.categoria_id = categoria_id
    juego.precio = max(0, min(a_entero(f.get("precio")), 100_000_000))
    juego.orden = max(-999, min(a_entero(f.get("orden")), 999))
    juego.destacado = "destacado" in f
    juego.activo = "activo" in f
    asignar_textos(juego, f, Juego.CAMPOS_TEXTO)

    if nueva_imagen or "quitar_imagen" in f:
        borrar_imagen(juego.imagen)
        juego.imagen = nueva_imagen

    db.session.add(juego)
    db.session.commit()
    return True


def _formulario(juego, accion):
    if request.method == "POST" and _guardar(juego):
        flash(f"“{juego.nombre}” fue {accion}.", "ok")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/juego_form.html", juego=juego)


@bp.route("/juegos/nuevo", methods=["GET", "POST"])
def juego_nuevo():
    return _formulario(Juego(activo=True, orden=0), "agregado")


@bp.route("/juegos/<int:id>", methods=["GET", "POST"])
def juego_editar(id):
    return _formulario(obtener_o_404(Juego, id), "actualizado")


@bp.route("/juegos/<int:id>/activo", methods=["POST"])
def juego_toggle(id):
    juego = obtener_o_404(Juego, id)
    juego.activo = not juego.activo
    db.session.commit()
    flash(f"“{juego.nombre}” ahora está {'visible' if juego.activo else 'oculto'}.", "ok")
    return _volver_al_listado()


@bp.route("/juegos/<int:id>/eliminar", methods=["POST"])
def juego_eliminar(id):
    juego = obtener_o_404(Juego, id)
    borrar_imagen(juego.imagen)
    db.session.delete(juego)
    db.session.commit()
    flash(f"“{juego.nombre}” fue eliminado.", "ok")
    return _volver_al_listado()
