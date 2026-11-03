"""Configuración central. Todo se puede sobreescribir con variables de entorno (.env)."""
import os
from datetime import timedelta

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INSTANCE_DIR = os.getenv("INSTANCE_DIR", os.path.join(PROJECT_DIR, "instance"))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-cambia-esto")
    # Docker usa PostgreSQL (ver docker-compose.yml). Sin DATABASE_URL se usa SQLite local.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(INSTANCE_DIR, "sitio.db")
    )
    # Fija el driver psycopg2 (SQLAlchemy 2.1 usa psycopg v3 por defecto con "postgresql://")
    for _prefijo in ("postgres://", "postgresql://"):
        if SQLALCHEMY_DATABASE_URI.startswith(_prefijo):
            SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://" + SQLALCHEMY_DATABASE_URI[len(_prefijo):]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    UPLOAD_DIR = os.path.join(INSTANCE_DIR, "uploads")
    MAX_UPLOAD_MB = 25  # fotos de celular modernas pueden pesar 10-20 MB
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024

    # Rendimiento: estáticos cacheados 1 año (las URLs llevan ?v= de versión)
    SEND_FILE_MAX_AGE_DEFAULT = 60 * 60 * 24 * 365
    COMPRESS_MIMETYPES = ["text/html", "text/css", "text/javascript", "application/javascript",
                          "application/json", "image/svg+xml", "application/xml"]

    # Admin: dueño del negocio. Super admin: equipo de desarrollo. Se crean solo la primera vez.
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    SUPERADMIN_USER = os.getenv("SUPERADMIN_USER", "superadmin")
    SUPERADMIN_PASSWORD = os.getenv("SUPERADMIN_PASSWORD", "superadmin123")

    # Sesión: cookie firmada, inaccesible desde JS, expira y solo viaja por HTTPS en producción
    SESSION_COOKIE_NAME = "sid"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "0") == "1"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    WTF_CSRF_TIME_LIMIT = 60 * 60 * 4

    SITIO_URL = os.getenv("SITIO_URL", "http://localhost:8000").rstrip("/")
    CREDITOS = "Monay Solutions"
    CREDITOS_URL = os.getenv("CREDITOS_URL", "#")
