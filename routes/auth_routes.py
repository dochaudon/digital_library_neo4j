from flask import Blueprint, request, jsonify, session, redirect, render_template
from services.auth_service import register_user, login_user

auth = Blueprint("auth", __name__, url_prefix="/auth")


# API
@auth.route("/register", methods=["POST"])
def register():
    data = request.json
    result = register_user(data)
    return jsonify(result)


@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    result = login_user(data)

    if "token" in result:
        session["user"] = result["user"]

    return jsonify(result)


# PAGE
@auth.route("/login-page")
def login_page():
    return render_template("auth/login.html")


@auth.route("/register-page")
def register_page():
    return render_template("auth/register.html")


# LOGOUT
@auth.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")