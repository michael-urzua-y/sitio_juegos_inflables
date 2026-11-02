import hashlib
from datetime import datetime, timedelta

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

# scrypt si está disponible (Docker); PBKDF2-SHA256 600k iteraciones como respaldo (OWASP)
HASH_METHOD = "scrypt" if hasattr(hashlib, "scrypt") else "pbkdf2:sha256:600000"
ROL_ADMIN = "admin"            # dueño del negocio
ROL_SUPERADMIN = "superadmin"  # equipo de desarrollo (Monay Solutions)
MAX_INTENTOS = 5
BLOQUEO = timedelta(minutes=15)
# Hash "señuelo" para que el tiempo de respuesta sea igual exista o no el usuario
_HASH_SENUELO = generate_password_hash("senuelo-no-usar", method=HASH_METHOD)


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default=ROL_ADMIN, server_default=ROL_ADMIN)
    intentos_fallidos = db.Column(db.Integer, default=0, nullable=False)
    bloqueado_hasta = db.Column(db.DateTime)
    ultimo_login = db.Column(db.DateTime)
    # Cambia al modificar la contraseña: invalida sesiones y cookies "recordarme" anteriores
    version_sesion = db.Column(db.Integer, default=1, nullable=False)

    @property
    def es_superadmin(self):
        return self.rol == ROL_SUPERADMIN

    def desbloquear(self):
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None

    def get_id(self):
        return f"{self.id}:{self.version_sesion}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method=HASH_METHOD)
        self.version_sesion = (self.version_sesion or 0) + 1

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def bloqueado(self):
        return bool(self.bloqueado_hasta and self.bloqueado_hasta > datetime.utcnow())

    def registrar_fallo(self):
        self.intentos_fallidos = (self.intentos_fallidos or 0) + 1
        if self.intentos_fallidos >= MAX_INTENTOS:
            self.bloqueado_hasta = datetime.utcnow() + BLOQUEO
            self.intentos_fallidos = 0

    def registrar_exito(self):
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.ultimo_login = datetime.utcnow()

    @classmethod
    def autenticar(cls, username, password):
        """Devuelve (usuario, error). Mensajes genéricos para no revelar qué usuarios existen."""
        user = cls.query.filter_by(username=username).first()
        if not user:
            check_password_hash(_HASH_SENUELO, password)
            return None, "Usuario o contraseña incorrectos."
        if user.bloqueado:
            return None, "Demasiados intentos fallidos. Intenta nuevamente en 15 minutos."
        if not user.check_password(password):
            user.registrar_fallo()
            db.session.commit()
            return None, "Usuario o contraseña incorrectos."
        user.registrar_exito()
        db.session.commit()
        return user, None
