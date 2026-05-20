# pyrefly: ignore [missing-import]
import os
import sys

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from flask import Flask
from flask_jwt_extended import JWTManager

from routes.public.main_routes import main
from routes.public.auth_routes import auth
from routes.public.qa_routes import qa
from routes.public.explore_routes import explore_bp
from routes.public.user_routes import user_bp

from routes.admin.document_admin import document_admin
from routes.admin.metadata_admin import metadata_admin
from routes.admin.user_admin import user_admin
from routes.admin.admin_main import admin_main

from routes.api.search_api import search_api
from routes.api.graph_api import graph_api
from routes.api.explore_api import explore_api

from services.auth_utils import init_bcrypt
from services.init_admin import init_admin_account

def create_app():
    # Setup Logging

    app = Flask(__name__)

    # =========================
    # CONFIG
    # =========================
    app.config["SESSION_PERMANENT"] = True
    app.config["SESSION_TYPE"] = "filesystem"

    # =========================
    # INIT EXTENSIONS
    # =========================
    app.secret_key = os.getenv("SECRET_KEY", "super-secret-session-key-456")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key-123")
    JWTManager(app)
    init_bcrypt(app)


    # =========================
    # REGISTER BLUEPRINT
    # =========================
    # PUBLIC
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(qa)
    app.register_blueprint(explore_bp)
    app.register_blueprint(user_bp)

    # ADMIN
    app.register_blueprint(admin_main)
    app.register_blueprint(document_admin)
    app.register_blueprint(metadata_admin)
    app.register_blueprint(user_admin)

    # API
    app.register_blueprint(search_api)
    app.register_blueprint(graph_api)
    app.register_blueprint(explore_api)

    # =========================
    # INIT ADMIN
    # =========================
    with app.app_context():
        init_admin_account()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)