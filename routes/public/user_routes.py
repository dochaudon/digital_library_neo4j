from flask import Blueprint, render_template, session, redirect, request, jsonify
from functools import wraps
from models.user_model import (
    get_user_by_id, find_user_by_email, change_password,
    add_bookmark, remove_bookmark, is_bookmarked, get_bookmarked_documents, count_bookmarked_documents
)
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


@user_bp.route("/api/user/bookmark", methods=["POST"])
@login_required
def toggle_bookmark():
    data = request.get_json()
    doc_id = data.get("doc_id")
    action = data.get("action") # 'add' or 'remove'
    
    if not doc_id or action not in ['add', 'remove']:
        return jsonify({"error": "Invalid data"}), 400
        
    user_session = session.get("user")
    user_id = user_session["id"]
    
    if action == 'add':
        success = add_bookmark(user_id, doc_id)
        if success:
            return jsonify({"message": "Đã lưu tài liệu", "bookmarked": True}), 200
    elif action == 'remove':
        success = remove_bookmark(user_id, doc_id)
        if success:
            return jsonify({"message": "Đã bỏ lưu tài liệu", "bookmarked": False}), 200
            
    return jsonify({"error": "Thao tác thất bại"}), 500


@user_bp.route("/api/user/bookmark/status/<doc_id>", methods=["GET"])
def check_bookmark_status(doc_id):
    if "user" not in session:
        return jsonify({"bookmarked": False}), 200
        
    user_session = session.get("user")
    user_id = user_session["id"]
    status = is_bookmarked(user_id, doc_id)
    return jsonify({"bookmarked": status}), 200


@user_bp.route("/bookmarks")
@login_required
def bookmarks_page():
    user_session = session.get("user")
    user_id = user_session["id"]
    
    page = request.args.get("page", 1, type=int)
    limit = 12
    skip = (page - 1) * limit
    
    total_docs = count_bookmarked_documents(user_id)
    total_pages = (total_docs + limit - 1) // limit if total_docs > 0 else 1
    
    docs = get_bookmarked_documents(user_id, skip=skip, limit=limit)
    
    return render_template("library/pages/user/bookmarks.html", documents=docs, page=page, total_pages=total_pages)
