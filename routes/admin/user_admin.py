from flask import Blueprint, request, render_template, redirect

from services.user_service import (
    get_users_service,
    delete_user_service,
    deactivate_user_service
)

user_admin = Blueprint("user_admin", __name__, url_prefix="/admin/users")


# =====================================================
# PAGINATION HELPER
# =====================================================
def paginate(data, page, limit=10):
    total = len(data)
    total_pages = (total // limit) + (1 if total % limit else 0)

    start = (page - 1) * limit
    items = data[start:start + limit]

    return items, total_pages


# =====================================================
# PAGE (SSR)
# =====================================================
@user_admin.route("/")
def user_page():
    page = int(request.args.get("page", 1))

    users, total_pages = paginate(get_users_service(), page)

    return render_template(
        "admin/pages/user/index.html",
        users=users,
        page=page,
        total_pages=total_pages
    )


# =====================================================
# DELETE USER
# =====================================================
@user_admin.route("/delete/<id>")
def delete_user(id):
    delete_user_service(id)
    return redirect("/admin/users")


# =====================================================
# TOGGLE ACTIVE
# =====================================================
@user_admin.route("/toggle/<id>")
def toggle_user(id):
    deactivate_user_service(id)
    return redirect("/admin/users")