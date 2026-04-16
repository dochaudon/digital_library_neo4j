from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


# =========================
# INIT
# =========================
def init_bcrypt(app):
    bcrypt.init_app(app)


# =========================
# HASH PASSWORD
# =========================
def hash_password(password):
    if not password:
        raise ValueError("Password is required")

    try:
        # 🔥 rounds mặc định tốt, có thể chỉnh nếu cần
        hashed = bcrypt.generate_password_hash(password)
        return hashed.decode("utf-8")

    except Exception as e:
        print("HASH ERROR:", e)
        raise


# =========================
# CHECK PASSWORD
# =========================
def check_password(hashed_password, password):
    if not hashed_password or not password:
        return False

    try:
        # 🔥 đảm bảo hashed là string
        if isinstance(hashed_password, bytes):
            hashed_password = hashed_password.decode("utf-8")

        return bcrypt.check_password_hash(hashed_password, password)

    except Exception as e:
        print("CHECK PASSWORD ERROR:", e)
        return False