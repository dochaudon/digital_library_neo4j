from flask import Flask
from flask_jwt_extended import JWTManager

from routes.public.main_routes import main
from routes.public.auth_routes import auth
from routes.public.qa_routes import qa


from routes.admin.document_admin import document_admin
from routes.admin.metadata_admin import metadata_admin
from routes.admin.user_admin import user_admin

from routes.api.search_api import search_api
from routes.api.graph_api import graph_api

from services.auth_utils import init_bcrypt
from services.init_admin import init_admin_account
from routes.api.explore_api import explore_api
from routes.public.explore_routes import explore_bp




def create_app():
    app = Flask(__name__)

    # =========================
    # CONFIG
    # =========================
    app.config["SECRET_KEY"] = "your-secret-key"
    app.config["JWT_SECRET_KEY"] = "your-jwt-secret-key"

    # session config (optional)
    app.config["SESSION_PERMANENT"] = True
    app.config["SESSION_TYPE"] = "filesystem"

    # =========================
    # INIT EXTENSIONS
    # =========================
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

    # ADMIN
    app.register_blueprint(document_admin)
    app.register_blueprint(metadata_admin)
    app.register_blueprint(user_admin)

    # API
    app.register_blueprint(search_api)
    app.register_blueprint(graph_api)
    app.register_blueprint(explore_api)
    # =========================
    # INIT ADMIN (🔥 QUAN TRỌNG)
    # =========================
    with app.app_context():
        init_admin_account()

    return app


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)