from models.user_model import find_user_by_email, create_user
from services.auth_utils import hash_password


# =========================
# INIT ADMIN ACCOUNT
# =========================
def init_admin_account():
    admin_email = "admin@gmail.com"

    # 🔍 check tồn tại
    existing_admin = find_user_by_email(admin_email)

    if existing_admin:
        print("✅ Admin already exists")
        return

    # 🔥 tạo admin
    admin_data = {
        "username": "admin",
        "email": admin_email,
        "password": hash_password("123456"),  # 🔥 auto hash
        "role": "admin"
    }

    create_user(admin_data)

    print("🔥 Admin account created:")
    print("   Email: admin@gmail.com")
    print("   Password: 123456")