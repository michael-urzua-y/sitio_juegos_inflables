from datetime import datetime

from app.extensions import db


class Juego(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)
    precio = db.Column(db.Integer, nullable=False, default=0)
    medidas = db.Column(db.String(80), default="")
    edad = db.Column(db.String(80), default="")
    capacidad = db.Column(db.String(80), default="")
    descripcion = db.Column(db.Text, default="")
    imagen = db.Column(db.String(255))  # archivo en instance/uploads
    destacado = db.Column(db.Boolean, default=False)
    # Aparece en las tarjetas grandes de la portada (máximo MAX_PORTADA juegos)
    en_portada = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    actualizado = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    categoria = db.relationship("Categoria", back_populates="juegos")

    MAX_PORTADA = 3

    # Campos de texto simples que se editan desde el formulario admin
    CAMPOS_TEXTO = ("medidas", "edad", "capacidad", "descripcion")
