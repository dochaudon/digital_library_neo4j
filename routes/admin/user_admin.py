from flask import Blueprint, jsonify, render_template

from services.user_service import (
    get_users_service,
    delete_user_service,
    deactivate_user_service
)


user_admin = Blueprint("user_admin", __name__, url_prefix="/admin/users")


# =========================
# PAGE
# =========================
@user_admin.route("/")
def user_page():
    return render_template("admin/pages/user/index.html")


# =========================
# LIST USERS
# =========================
@user_admin.route("/api", methods=["GET"])
def list_users():
    users = get_users_service()
    return jsonify(users)


# =========================
# DEACTIVATE USER
# =========================
@user_admin.route("/api/<id>/deactivate", methods=["PUT"])
def deactivate(id):
    result = deactivate_user_service(id)
    return jsonify(result)


# =========================
# DELETE USER
# =========================
@user_admin.route("/api/<id>", methods=["DELETE"])
def delete(id):
    result = delete_user_service(id)
    return jsonify(result)