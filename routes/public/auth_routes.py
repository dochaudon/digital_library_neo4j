from flask import Blueprint, request, jsonify, session, redirect, render_template

from services.auth_service import register_user, login_user


auth = Blueprint("auth", __name__, url_prefix="/auth")


# =========================
# API - REGISTER
# =========================
@auth.route("/api/register", methods=["POST"])
def register_api():
    data = request.get_json() or {}

    result = register_user(data)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result), 200


# =========================
# API - LOGIN
# =========================
@auth.route("/api/login", methods=["POST"])
def login_api():
    data = request.get_json() or {}

    result = login_user(data)

    if "error" in result:
        return jsonify(result), 401

    # lưu session
    if "user" in result:
        session["user"] = result["user"]
        session.permanent = True

    return jsonify(result), 200


# =========================
# PAGE - LOGIN
# =========================
@auth.route("/login")
def login_page():
    return render_template("auth/login.html")


# =========================
# PAGE - REGISTER
# =========================
@auth.route("/register")
def register_page():
    return render_template("auth/register.html")


# =========================
# LOGOUT
# =========================
@auth.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")