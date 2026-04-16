from flask import Blueprint, jsonify, render_template

from services.user_service import (
    get_users_service,
    delete_user_service,
    deactivate_user_service
)

user_admin_bp = Blueprint("user_admin", __name__)


# ================= PAGE =================
@user_admin_bp.route("/admin/users/page")
def user_page():
    return render_template("admin/pages/user/index.html")


# ================= API =================
@user_admin_bp.route("/admin/users", methods=["GET"])
def list_users():
    return jsonify(get_users_service())


@user_admin_bp.route("/admin/users/<id>/deactivate", methods=["PUT"])
def deactivate(id):
    deactivate_user_service(id)
    return jsonify({"message": "User deactivated"})


@user_admin_bp.route("/admin/users/<id>", methods=["DELETE"])
def delete(id):
    delete_user_service(id)
    return jsonify({"message": "User deleted"})