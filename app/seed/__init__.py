"""Crea tablas y carga datos iniciales. Es idempotente: solo inserta lo que falta."""
import click
from flask import current_app

from app.extensions import db
from app.models import Ajuste, Bloque, Categoria, Juego, Usuario
from app.models.usuario import ROL_ADMIN, ROL_SUPERADMIN

from . import data


def _migrar_columnas():
    """Agrega columnas nuevas a tablas existentes (create_all no modifica tablas ya creadas)."""
    from sqlalchemy import inspect, text
    columnas = {c["name"] for c in inspect(db.engine).get_columns("usuario")}
    if "rol" not in columnas:
        with db.engine.begin() as con:
            con.execute(text(f"ALTER TABLE usuario ADD COLUMN rol VARCHAR(20) NOT NULL DEFAULT '{ROL_ADMIN}'"))


def _usuarios():
    """Crea el admin y el super admin si aún no existen."""
    cfg = current_app.config
    for rol, usuario, clave in ((ROL_ADMIN, cfg["ADMIN_USER"], cfg["ADMIN_PASSWORD"]),
                                (ROL_SUPERADMIN, cfg["SUPERADMIN_USER"], cfg["SUPERADMIN_PASSWORD"])):
        if not Usuario.query.filter_by(rol=rol).first() and not Usuario.query.filter_by(username=usuario).first():
            nuevo = Usuario(username=usuario, rol=rol)
            nuevo.set_password(clave)
            db.session.add(nuevo)


def _ajustes():
    """Crea las claves nuevas y elimina las que ya no existen (p. ej. SEO, que pasó a seo_config)."""
    existentes = {a.clave: a for a in Ajuste.query.all()}
    for clave, valor in data.AJUSTES.items():
        if clave not in existentes:
            db.session.add(Ajuste(clave=clave, valor=valor))
    for clave, ajuste in existentes.items():
        if clave not in data.AJUSTES:
            db.session.delete(ajuste)


def _bloques():
    if not Bloque.query.first():
        for i, b in enumerate(data.BLOQUES, start=1):
            db.session.add(Bloque(orden=i, **b))


def _catalogo():
    if Categoria.query.first():
        return
    cats = {}
    for orden, c in enumerate(data.CATEGORIAS, start=1):
        cats[c["slug"]] = Categoria(orden=orden, **c)
        db.session.add(cats[c["slug"]])
    for i, j in enumerate(data.JUEGOS):
        j = dict(j)
        db.session.add(Juego(categoria=cats[j.pop("categoria")], orden=(i % 3) + 1, **j))


def recargar_catalogo():
    """Reemplaza TODAS las categorías y juegos por los de seed/data.py (borra sus fotos)."""
    from app.utils.imagenes import borrar_imagen
    for juego in Juego.query.all():
        borrar_imagen(juego.imagen)
        db.session.delete(juego)
    Categoria.query.delete()
    db.session.flush()
    _catalogo()
    db.session.commit()


def registrar_comandos(app):
    @app.cli.command("recargar-catalogo")
    @click.option("--si", is_flag=True, help="Confirma sin preguntar.")
    def recargar_catalogo_cmd(si):
        """Reemplaza categorías y juegos por los datos de ejemplo (¡borra los actuales!)."""
        total = Juego.query.count()
        if not si:
            click.confirm(f"Se eliminarán {total} juegos y sus fotos. ¿Continuar?", abort=True)
        recargar_catalogo()
        click.echo(f"Catálogo recargado: {Categoria.query.count()} categorías, {Juego.query.count()} juegos.")


def inicializar_db():
    db.create_all()
    _migrar_columnas()
    for paso in (_usuarios, _ajustes, _bloques, _catalogo):
        paso()
    db.session.commit()
