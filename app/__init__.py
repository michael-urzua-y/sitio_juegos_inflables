import os

from flask import Flask

from app.config import INSTANCE_DIR, Config
from app.extensions import compress, csrf, db, login_manager


def create_app(config=Config):
    app = Flask(__name__, instance_path=INSTANCE_DIR)
    app.config.from_object(config)
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    from app.security import init_security
    init_security(app)
    _init_extensiones(app)
    _registrar_blueprints(app)

    from app.utils import plantillas
    plantillas.registrar(app)

    from app.seed import inicializar_db, registrar_comandos
    registrar_comandos(app)
    with app.app_context():
        inicializar_db()

    return app


def _init_extensiones(app):
    db.init_app(app)
    compress.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message = "Inicia sesión para continuar."
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"

    from app.models import Usuario

    @login_manager.user_loader
    def cargar_usuario(token):
        # token = "id:version"; si la contraseña cambió, la sesión antigua deja de ser válida
        try:
            uid, version = (int(x) for x in token.split(":"))
        except ValueError:
            return None
        user = db.session.get(Usuario, uid)
        return user if user and user.version_sesion == version else None


def _registrar_blueprints(app):
    from app.blueprints.admin import bp as admin_bp
    from app.blueprints.public import bp as public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
