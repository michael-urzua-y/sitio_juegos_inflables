from app.extensions import db

# Tipos de bloques de contenido editables y cómo se rotulan sus campos en el admin
TIPOS = {
    "stat":      {"nombre": "Cifras de portada",    "titulo": "Cifra (ej: +500)", "texto": "Descripción", "icono": False},
    "beneficio": {"nombre": "Beneficios",           "titulo": "Título",           "texto": "Detalle",     "icono": True},
    "paso":      {"nombre": "Pasos para cotizar",   "titulo": "Título del paso",  "texto": "Explicación", "icono": False},
    "faq":       {"nombre": "Preguntas frecuentes", "titulo": "Pregunta",         "texto": "Respuesta",   "icono": False},
}


class Bloque(db.Model):
    """Contenido de la portada editable desde el admin (cifras, beneficios, pasos, FAQ)."""
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False, index=True)
    titulo = db.Column(db.String(200), nullable=False)
    texto = db.Column(db.String(1000), default="")
    icono = db.Column(db.String(30), default="")
    orden = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)

    CAMPOS_TEXTO = ("titulo", "texto")
