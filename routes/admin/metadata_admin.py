from flask import Blueprint, request, render_template, redirect
from services.metadata_service import *

metadata_admin = Blueprint("metadata_admin", __name__, url_prefix="/admin")


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
# AUTHOR
# =====================================================

@metadata_admin.route("/authors")
def author_page():
    page = int(request.args.get("page", 1))
    q = request.args.get("q", "")
    authors, total_pages = paginate(get_authors_service(q), page)
    return render_template("admin/pages/author/index.html", authors=authors, page=page, total_pages=total_pages, q=q)

@metadata_admin.route("/authors/create", methods=["GET", "POST"])
def create_author():
    if request.method == "POST":
        create_author_service(request.form.to_dict())
        return redirect("/admin/authors")
    
    next_id = get_next_metadata_id("Author", "A")
    return render_template("admin/pages/author/create.html", next_id=next_id)

@metadata_admin.route("/authors/edit/<id>", methods=["GET", "POST"])
def edit_author(id):
    if request.method == "POST":
        update_author_service(id, request.form.to_dict())
        return redirect("/admin/authors")
    
    author = get_author_detail_service(id)
    return render_template("admin/pages/author/edit.html", author=author)

@metadata_admin.route("/authors/delete/<id>")
def delete_author(id):
    delete_author_service(id)
    return redirect("/admin/authors")


# =====================================================
# SUBJECT
# =====================================================

@metadata_admin.route("/subjects")
def subject_page():
    page = int(request.args.get("page", 1))
    q = request.args.get("q", "")
    subjects, total_pages = paginate(get_subjects_service(q), page)
    return render_template("admin/pages/subject/index.html", subjects=subjects, page=page, total_pages=total_pages, q=q)

@metadata_admin.route("/subjects/create", methods=["GET", "POST"])
def create_subject():
    if request.method == "POST":
        create_subject_service(request.form.to_dict())
        return redirect("/admin/subjects")
    
    next_id = get_next_metadata_id("Subject", "S")
    return render_template("admin/pages/subject/create.html", next_id=next_id)

@metadata_admin.route("/subjects/edit/<id>", methods=["GET", "POST"])
def edit_subject(id):
    if request.method == "POST":
        update_subject_service(id, request.form.to_dict())
        return redirect("/admin/subjects")
    
    subject = get_subject_detail_service(id)
    return render_template("admin/pages/subject/edit.html", subject=subject)

@metadata_admin.route("/subjects/delete/<id>")
def delete_subject(id):
    delete_subject_service(id)
    return redirect("/admin/subjects")


# =====================================================
# KEYWORD
# =====================================================

@metadata_admin.route("/keywords")
def keyword_page():
    page = int(request.args.get("page", 1))
    q = request.args.get("q", "")
    keywords, total_pages = paginate(get_keywords_service(q), page)
    return render_template("admin/pages/keyword/index.html", keywords=keywords, page=page, total_pages=total_pages, q=q)

@metadata_admin.route("/keywords/create", methods=["GET", "POST"])
def create_keyword():
    if request.method == "POST":
        create_keyword_service(request.form.to_dict())
        return redirect("/admin/keywords")
    
    next_id = get_next_metadata_id("Keyword", "K")
    return render_template("admin/pages/keyword/create.html", next_id=next_id)

@metadata_admin.route("/keywords/edit/<id>", methods=["GET", "POST"])
def edit_keyword(id):
    if request.method == "POST":
        update_keyword_service(id, request.form.to_dict())
        return redirect("/admin/keywords")
    
    keyword = get_keyword_detail_service(id)
    return render_template("admin/pages/keyword/edit.html", keyword=keyword)

@metadata_admin.route("/keywords/delete/<id>")
def delete_keyword(id):
    delete_keyword_service(id)
    return redirect("/admin/keywords")


# =====================================================
# CATEGORY
# =====================================================

@metadata_admin.route("/categories")
def category_page():
    page = int(request.args.get("page", 1))
    q = request.args.get("q", "")
    categories, total_pages = paginate(get_categories_service(q), page)
    return render_template("admin/pages/category/index.html", categories=categories, page=page, total_pages=total_pages, q=q)

@metadata_admin.route("/categories/create", methods=["GET", "POST"])
def create_category():
    if request.method == "POST":
        create_category_service(request.form.to_dict())
        return redirect("/admin/categories")
    
    next_id = get_next_metadata_id("Category", "C")
    return render_template("admin/pages/category/create.html", next_id=next_id)

@metadata_admin.route("/categories/edit/<id>", methods=["GET", "POST"])
def edit_category(id):
    if request.method == "POST":
        update_category_service(id, request.form.to_dict())
        return redirect("/admin/categories")
    
    category = get_category_detail_service(id)
    return render_template("admin/pages/category/edit.html", category=category)

@metadata_admin.route("/categories/delete/<id>")
def delete_category(id):
    delete_category_service(id)
    return redirect("/admin/categories")


# =====================================================
# PUBLISHER
# =====================================================

@metadata_admin.route("/publishers")
def publisher_page():
    page = int(request.args.get("page", 1))
    q = request.args.get("q", "")
    publishers, total_pages = paginate(get_publishers_service(q), page)
    return render_template("admin/pages/publisher/index.html", publishers=publishers, page=page, total_pages=total_pages, q=q)

@metadata_admin.route("/publishers/create", methods=["GET", "POST"])
def create_publisher():
    if request.method == "POST":
        create_publisher_service(request.form.to_dict())
        return redirect("/admin/publishers")
    
    next_id = get_next_metadata_id("Publisher", "P")
    return render_template("admin/pages/publisher/create.html", next_id=next_id)

@metadata_admin.route("/publishers/edit/<id>", methods=["GET", "POST"])
def edit_publisher(id):
    if request.method == "POST":
        update_publisher_service(id, request.form.to_dict())
        return redirect("/admin/publishers")
    
    publisher = get_publisher_detail_service(id)
    return render_template("admin/pages/publisher/edit.html", publisher=publisher)

@metadata_admin.route("/publishers/delete/<id>")
def delete_publisher(id):
    delete_publisher_service(id)
    return redirect("/admin/publishers")


# =====================================================
# UNIVERSITY
# =====================================================

@metadata_admin.route("/universities")
def university_page():
    page = int(request.args.get("page", 1))
    q = request.args.get("q", "")
    universities, total_pages = paginate(get_universities_service(q), page)
    return render_template("admin/pages/university/index.html", universities=universities, page=page, total_pages=total_pages, q=q)

@metadata_admin.route("/universities/create", methods=["GET", "POST"])
def create_university():
    if request.method == "POST":
        create_university_service(request.form.to_dict())
        return redirect("/admin/universities")
    
    next_id = get_next_metadata_id("University", "U")
    return render_template("admin/pages/university/create.html", next_id=next_id)

@metadata_admin.route("/universities/edit/<id>", methods=["GET", "POST"])
def edit_university(id):
    if request.method == "POST":
        update_university_service(id, request.form.to_dict())
        return redirect("/admin/universities")
    
    university = get_university_detail_service(id)
    return render_template("admin/pages/university/edit.html", university=university)

@metadata_admin.route("/universities/delete/<id>")
def delete_university(id):
    delete_university_service(id)
    return redirect("/admin/universities")


# =====================================================
# LANGUAGE
# =====================================================

@metadata_admin.route("/languages")
def language_page():
    page = int(request.args.get("page", 1))
    q = request.args.get("q", "")
    languages, total_pages = paginate(get_languages_service(q), page)
    return render_template("admin/pages/language/index.html", languages=languages, page=page, total_pages=total_pages, q=q)

@metadata_admin.route("/languages/create", methods=["GET", "POST"])
def create_language():
    if request.method == "POST":
        create_language_service(request.form.to_dict())
        return redirect("/admin/languages")
    
    next_id = get_next_metadata_id("Language", "L")
    return render_template("admin/pages/language/create.html", next_id=next_id)

@metadata_admin.route("/languages/edit/<id>", methods=["GET", "POST"])
def edit_language(id):
    if request.method == "POST":
        update_language_service(id, request.form.to_dict())
        return redirect("/admin/languages")
    
    language = get_language_detail_service(id)
    return render_template("admin/pages/language/edit.html", language=language)

@metadata_admin.route("/languages/delete/<id>")
def delete_language(id):
    delete_language_service(id)
    return redirect("/admin/languages")


# =====================================================
# JOURNAL
# =====================================================

@metadata_admin.route("/journals")
def journal_page():
    page = int(request.args.get("page", 1))
    q = request.args.get("q", "")
    journals, total_pages = paginate(get_journals_service(q), page)
    return render_template("admin/pages/journal/index.html", journals=journals, page=page, total_pages=total_pages, q=q)

@metadata_admin.route("/journals/create", methods=["GET", "POST"])
def create_journal():
    if request.method == "POST":
        create_journal_service(request.form.to_dict())
        return redirect("/admin/journals")
    
    next_id = get_next_metadata_id("Journal", "J")
    return render_template("admin/pages/journal/create.html", next_id=next_id)

@metadata_admin.route("/journals/edit/<id>", methods=["GET", "POST"])
def edit_journal(id):
    if request.method == "POST":
        update_journal_service(id, request.form.to_dict())
        return redirect("/admin/journals")
    
    journal = get_journal_detail_service(id)
    return render_template("admin/pages/journal/edit.html", journal=journal)

@metadata_admin.route("/journals/delete/<id>")
def delete_journal(id):
    delete_journal_service(id)
    return redirect("/admin/journals")


