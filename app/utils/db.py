from flask import abort

from app.extensions import db


def obtener_o_404(modelo, id):
    return db.session.get(modelo, id) or abort(404)
