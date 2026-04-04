from flask import Flask
from flask_jwt_extended import JWTManager

from routes.routes import main
from routes.auth_routes import auth

from services.auth_utils import init_bcrypt


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
    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)