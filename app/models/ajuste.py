from app.extensions import db


class Ajuste(db.Model):
    """Par clave/valor para textos y datos de contacto editables."""
    clave = db.Column(db.String(60), primary_key=True)
    valor = db.Column(db.Text, default="")
