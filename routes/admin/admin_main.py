from flask import Blueprint, render_template, session, redirect, url_for
from services.document_service import count_documents_service

admin_main = Blueprint("admin_main", __name__, url_prefix="/admin")

@admin_main.route("/")
def admin_index():
    return redirect(url_for("admin_main.dashboard"))

@admin_main.route("/dashboard")
def dashboard():
    # Only allow admin (you might want to add a decorator later)
    if "user" not in session or session["user"].get("role") != "admin":
        return redirect(url_for("auth.login_page"))
        
    total_books = count_documents_service(doc_type="Book")
    total_articles = count_documents_service(doc_type="Article")
    total_thesis = count_documents_service(doc_type="Thesis")
    
    return render_template("admin/pages/dashboard/index.html", 
                           total_books=total_books, 
                           total_articles=total_articles, 
                           total_thesis=total_thesis)

@admin_main.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.login_page"))
