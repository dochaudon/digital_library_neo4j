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

    authors, total_pages = paginate(get_authors_service(), page)

    return render_template(
        "admin/pages/author/index.html",
        authors=authors,
        page=page,
        total_pages=total_pages
    )


@metadata_admin.route("/authors/create", methods=["POST"])
def create_author():
    create_author_service(request.form.to_dict())
    return redirect("/admin/authors")


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

    subjects, total_pages = paginate(get_subjects_service(), page)

    return render_template(
        "admin/pages/subject/index.html",
        subjects=subjects,
        page=page,
        total_pages=total_pages
    )


@metadata_admin.route("/subjects/create", methods=["POST"])
def create_subject():
    create_subject_service(request.form.to_dict())
    return redirect("/admin/subjects")


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

    keywords, total_pages = paginate(get_keywords_service(), page)

    return render_template(
        "admin/pages/keyword/index.html",
        keywords=keywords,
        page=page,
        total_pages=total_pages
    )


@metadata_admin.route("/keywords/create", methods=["POST"])
def create_keyword():
    create_keyword_service(request.form.to_dict())
    return redirect("/admin/keywords")


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

    categories, total_pages = paginate(get_categories_service(), page)

    return render_template(
        "admin/pages/category/index.html",
        categories=categories,
        page=page,
        total_pages=total_pages
    )


@metadata_admin.route("/categories/create", methods=["POST"])
def create_category():
    create_category_service(request.form.to_dict())
    return redirect("/admin/categories")


@metadata_admin.route("/categories/delete/<id>")
def delete_category(id):
    delete_category_service(id)
    return redirect("/admin/categories")


# =====================================================
# INSTITUTION
# =====================================================

@metadata_admin.route("/institutions")
def institution_page():
    page = int(request.args.get("page", 1))

    institutions, total_pages = paginate(get_institutions_service(), page)

    return render_template(
        "admin/pages/institution/index.html",
        institutions=institutions,
        page=page,
        total_pages=total_pages
    )


@metadata_admin.route("/institutions/create", methods=["POST"])
def create_institution():
    create_institution_service(request.form.to_dict())
    return redirect("/admin/institutions")


@metadata_admin.route("/institutions/delete/<id>")
def delete_institution(id):
    delete_institution_service(id)
    return redirect("/admin/institutions")


# =====================================================
# LANGUAGE
# =====================================================

@metadata_admin.route("/languages")
def language_page():
    page = int(request.args.get("page", 1))

    languages, total_pages = paginate(get_languages_service(), page)

    return render_template(
        "admin/pages/language/index.html",
        languages=languages,
        page=page,
        total_pages=total_pages
    )


@metadata_admin.route("/languages/create", methods=["POST"])
def create_language():
    create_language_service(request.form.to_dict())
    return redirect("/admin/languages")


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

    journals, total_pages = paginate(get_journals_service(), page)

    return render_template(
        "admin/pages/journal/index.html",
        journals=journals,
        page=page,
        total_pages=total_pages
    )


@metadata_admin.route("/journals/create", methods=["POST"])
def create_journal():
    create_journal_service(request.form.to_dict())
    return redirect("/admin/journals")


@metadata_admin.route("/journals/delete/<id>")
def delete_journal(id):
    delete_journal_service(id)
    return redirect("/admin/journals")

