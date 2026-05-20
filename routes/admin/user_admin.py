from flask import Blueprint, request, render_template, redirect, session, Response, url_for

from services.user_service import (
    get_users_service,
    delete_user_service,
    deactivate_user_service
)
from services.export_service import (
    get_export_stats_service,
    generate_csv_data,
    generate_all_zip_service
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


# =====================================================
# DATA EXPORT DASHBOARD (NEW)
# =====================================================
@user_admin.route("/export")
def export_dashboard():
    # Admin security check
    if "user" not in session or session["user"].get("role") != "admin":
        return redirect(url_for("auth.login_page"))
        
    stats = get_export_stats_service()
    
    # Split stats into node and relationship categories
    nodes_stats = [item for item in stats if item["category"] == "node"]
    rels_stats = [item for item in stats if item["category"] == "relationship"]
    
    return render_template(
        "admin/pages/user/export.html",
        nodes_stats=nodes_stats,
        rels_stats=rels_stats
    )


# =====================================================
# DOWNLOAD EXPORT DATA (NEW)
# =====================================================
@user_admin.route("/export/download")
def download_export():
    # Admin security check
    if "user" not in session or session["user"].get("role") != "admin":
        return redirect(url_for("auth.login_page"))
        
    file_target = request.args.get("file", "all")
    
    if file_target == "all":
        # Download ZIP of all 19 CSVs
        zip_data = generate_all_zip_service()
        return Response(
            zip_data,
            mimetype="application/zip",
            headers={"Content-Disposition": "attachment; filename=neo4j_export_all.zip"}
        )
    else:
        # Download specific CSV
        csv_data = generate_csv_data(file_target)
        if csv_data is None:
            return "Export file configuration not found", 404
            
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={file_target}"}
        )