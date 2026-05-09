from flask import Blueprint, render_template, session, redirect, request, jsonify
from functools import wraps
from models.user_model import get_user_by_id, find_user_by_email, change_password
from services.auth_utils import check_password, hash_password

user_bp = Blueprint("user", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect("/auth/login")
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route("/profile")
@login_required
def profile():
    user_session = session.get("user")
    user_data = get_user_by_id(user_session["id"])
    
    if not user_data:
        session.pop("user", None)
        return redirect("/auth/login")
        
    return render_template("library/pages/user/profile.html", user=user_data)

@user_bp.route("/api/user/change-password", methods=["POST"])
@login_required
def change_password_api():
    data = request.get_json()
    user_session = session.get("user")
    
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")
    
    if not old_password or not new_password:
        return jsonify({"error": "Vui lòng nhập đầy đủ thông tin"}), 400
        
    if new_password != confirm_password:
        return jsonify({"error": "Mật khẩu mới không khớp"}), 400
        
    # Lấy thông tin user đầy đủ (bao gồm hashed password)
    user = find_user_by_email(user_session["email"])
    
    if not check_password(user["password"], old_password):
        return jsonify({"error": "Mật khẩu cũ không chính xác"}), 400
        
    # Hash mật khẩu mới và lưu
    hashed = hash_password(new_password)
    success = change_password(user["id"], hashed)
    
    if success:
        return jsonify({"message": "Đổi mật khẩu thành công"}), 200
    else:
        return jsonify({"error": "Có lỗi xảy ra, vui lòng thử lại"}), 500
