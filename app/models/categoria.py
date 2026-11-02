from app.extensions import db

# Íconos disponibles: identificador interno (símbolo SVG) -> nombre visible en el admin
ICONOS = {
    "castle": "Castillo (inflables)",
    "gear": "Engranaje (mecánicos)",
    "target": "Diana (interactivos)",
    "smile": "Carita (zona infantil)",
    "gamepad": "Control (electrónicos)",
    "ball8": "Bola de pool (salón)",
    "kite": "Volantín (juegos típicos)",
    "drop": "Gota de agua (juegos de agua)",
    "slide": "Tobogán",
    "jump": "Salto (cama elástica)",
    "popcorn": "Cabritas (máquinas)",
    "star": "Estrella",
    "sparkles": "Destellos",
    "truck": "Camión (despacho)",
    "shield": "Escudo (seguridad)",
    "clock": "Reloj (puntualidad)",
    "users": "Personas",
    "calendar": "Calendario",
    "pin": "Ubicación",
}


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.String(255), default="")
    icono = db.Column(db.String(30), default="star")
    orden = db.Column(db.Integer, default=0)

    juegos = db.relationship("Juego", back_populates="categoria", lazy="dynamic")
