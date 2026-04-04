from flask import Blueprint, request, jsonify, session, redirect, render_template
from services.auth_service import register_user, login_user

auth = Blueprint("auth", __name__, url_prefix="/auth")


# =========================
# REGISTER API
# =========================
@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    result = register_user(data)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result), 200


# =========================
# LOGIN API
# =========================
@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    result = login_user(data)

    if "error" in result:
        return jsonify(result), 401

    # lưu session
    if "token" in result:
        session["user"] = result["user"]
        session.permanent = True

    return jsonify(result), 200


# =========================
# LOGIN PAGE
# =========================
@auth.route("/login-page")
def login_page():
    return render_template("auth/login.html")


# =========================
# REGISTER PAGE
# =========================
@auth.route("/register-page")
def register_page():
    return render_template("auth/register.html")


# =========================
# LOGOUT
# =========================
@auth.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")