from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


# =========================
# INIT (OPTIONAL)
# =========================
def init_bcrypt(app):
    bcrypt.init_app(app)


# =========================
# HASH PASSWORD
# =========================
def hash_password(password):
    if not password:
        return None

    try:
        hashed = bcrypt.generate_password_hash(password)
        return hashed.decode('utf-8')
    except Exception:
        return None


# =========================
# CHECK PASSWORD
# =========================
def check_password(hashed_password, password):
    if not hashed_password or not password:
        return False

    try:
        return bcrypt.check_password_hash(hashed_password, password)
    except Exception:
        return False