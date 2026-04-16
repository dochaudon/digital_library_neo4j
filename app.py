from flask import Flask
from flask_jwt_extended import JWTManager
from routes.admin.document_routes import document_bp
from routes.routes import main
from routes.auth_routes import auth
from routes.admin.author_routes import author_bp
from services.auth_utils import init_bcrypt
from services.init_admin import init_admin_account   # 🔥 thêm
from routes.admin.subject_routes import subject_bp
from routes.admin.keyword_routes import keyword_bp
from routes.admin.journal_routes import journal_bp
from routes.admin.category_routes import category_bp
from routes.admin.institution_routes import institution_bp
from routes.admin.language_routes import language_bp
from routes.admin.user_admin_routes import user_admin_bp

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
    app.register_blueprint(author_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(subject_bp)
    app.register_blueprint(keyword_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(institution_bp)
    app.register_blueprint(language_bp)
    app.register_blueprint(user_admin_bp)
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