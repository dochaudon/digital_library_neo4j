from flask import Blueprint, render_template, request

from services.search_service import search_documents, get_latest
from services.graph_service import get_graph_data

from services.book_service import get_book_detail
from services.article_service import get_article_detail
from services.thesis_service import get_thesis_detail

from services.list_service import (
    get_books,
    count_books,
    get_articles,
    count_articles,
    get_thesis,
    count_thesis
)
from flask import request, render_template, redirect, url_for
from services.book_service import (
    create_book_service,
    get_books_service,
    get_book_detail_service,
    update_book_service,
    delete_book_service
)

from services.article_service import (
    create_article_service,
    get_articles_service,
    count_articles_service,
    get_article_detail_service,
    update_article_service,
    delete_article_service
)
from services.suggest_service import suggest_documents
main = Blueprint("main", __name__)


# =========================
# HOME
# =========================
@main.route("/")
def home():
    documents = get_latest()
    return render_template("library/pages/index.html", documents=documents)


# =========================
# SEARCH
# =========================
@main.route("/search")
def search():

    query = (request.args.get("query") or "").strip()
    mode = (request.args.get("mode") or "auto").strip()

    page = int(request.args.get("page", 1))
    sort = request.args.get("sort", "")

    limit = 5
    skip = (page - 1) * limit

    filters = {
        "doc_type": request.args.get("doc_type") or None,
        "author": request.args.get("author") or None,
        "topic": request.args.get("topic") or None,
        "publisher": request.args.get("publisher") or None,
        "university": request.args.get("university") or None,
        "year": None,
    }

    year_raw = (request.args.get("year") or "").strip()
    if year_raw.isdigit():
        filters["year"] = int(year_raw)

    # ===== SEARCH =====
    all_results = search_documents(
        query=query,
        mode=mode,
        filters=filters,
        limit=100
    )

    # ===== SORT =====
    if sort == "year_asc":
        all_results.sort(key=lambda x: x.get("year") or 0)
    elif sort == "year_desc":
        all_results.sort(key=lambda x: x.get("year") or 0, reverse=True)
    elif sort == "az":
        all_results.sort(key=lambda x: (x.get("title") or "").lower())
    elif sort == "za":
        all_results.sort(key=lambda x: (x.get("title") or "").lower(), reverse=True)

    # ===== PAGINATION =====
    total = len(all_results)
    total_pages = (total // limit) + (1 if total % limit else 0)

    results = all_results[skip: skip + limit]

    return render_template(
        "library/pages/results.html",
        query=query,
        mode=mode,
        filters=filters,
        results=results,
        page=page,
        total_pages=total_pages,
        sort=sort
    )


# =========================
# BOOK DETAIL
# =========================

@main.route("/book/<id>")
def book_detail(id):
    book = get_book_detail(id)
    if not book:
        return "Không tìm thấy sách", 404
    graph_data = get_graph_data("Book", id)

    return render_template(
        "library/pages/books/book_detail.html",
        book=book,
        graph_data=graph_data
    )
# =========================
# ARTICLE DETAIL
# =========================
@main.route("/article/<id>")
def article_detail(id):

    article = get_article_detail(id)
    if not article:
        return "Không tìm thấy bài báo", 404

    graph_data = get_graph_data("Article", id)

    return render_template(
        "library/pages/articles/article_detail.html",
        article=article,
        graph_data=graph_data
    )


# =========================
# THESIS DETAIL
# =========================
@main.route("/thesis/<id>")
def thesis_detail(id):

    thesis = get_thesis_detail(id)
    if not thesis:
        return "Không tìm thấy luận văn", 404

    graph_data = get_graph_data("Thesis", id)

    return render_template(
        "library/pages/thesis/thesis_detail.html",
        thesis=thesis,
        graph_data=graph_data
    )


# =========================
# BOOK LIST
# =========================
@main.route("/books")
def books_page():
    page = int(request.args.get("page", 1))
    limit = 5
    skip = (page - 1) * limit

    books = get_books(skip, limit)
    total = count_books()

    total_pages = (total // limit) + (1 if total % limit else 0)

    return render_template(
        "library/pages/books/books.html",
        books=books,
        page=page,
        total_pages=total_pages
    )


# =========================
# ARTICLE LIST
# =========================
@main.route("/articles")
def articles_page():
    page = int(request.args.get("page", 1))
    limit = 5
    skip = (page - 1) * limit

    data = get_articles(skip, limit)
    total = count_articles()

    total_pages = (total // limit) + (1 if total % limit else 0)

    return render_template(
        "library/pages/articles/articles.html",
        articles=data,
        page=page,
        total_pages=total_pages
    )


# =========================
# THESIS LIST
# =========================
@main.route("/thesis")
def thesis_page():
    page = int(request.args.get("page", 1))
    limit = 5
    skip = (page - 1) * limit

    data = get_thesis(skip, limit)
    total = count_thesis()

    total_pages = (total // limit) + (1 if total % limit else 0)

    return render_template(
        "library/pages/thesis/thesis.html",
        thesis=data,
        page=page,
        total_pages=total_pages
    )


# =========================
# SUGGEST
# =========================
@main.route("/suggest")
def suggest():

    query = request.args.get("q", "").strip()

    results = suggest_documents(query)

    return {"results": results}

# =========================
# ADMIN BOOK LIST
# =========================
@main.route("/admin/books")
def admin_books():
    page = int(request.args.get("page", 1))
    limit = 10
    skip = (page - 1) * limit

    books = get_books(skip, limit)   # ⚠️ KHÔNG dùng get_books_service() nữa nếu chưa hỗ trợ phân trang
    total = count_books()

    total_pages = (total // limit) + (1 if total % limit else 0)

    return render_template(
        "admin/pages/books/list.html",
        books=books,
        page=page,
        total_pages=total_pages,
        limit=limit
    )


# =========================
# CREATE
# =========================
@main.route("/admin/books/create", methods=["GET", "POST"])
def create_book():

    if request.method == "POST":
        data = {
            "title": request.form["title"],
            "year": int(request.form["year"]),
            "isbn": request.form["isbn"],
            "pages": int(request.form["pages"]),
            "abstract": request.form["abstract"]
        }

        create_book_service(data)
        return redirect("/admin/books")

    return render_template("admin/pages/books/create.html")

@main.route("/admin/books/<id>")
def admin_book_detail(id):
    book = get_book_detail(id)
    graph_data = get_graph_data("Book", id)

    return render_template(
        "admin/pages/books/detail.html",
        book=book,
        graph_data=graph_data
    )

# =========================
# EDIT
# =========================
@main.route("/admin/books/edit/<id>", methods=["GET", "POST"])
def edit_book(id):

    book = get_book_detail_service(id)

    if request.method == "POST":
        data = {
            "title": request.form["title"],
            "year": int(request.form["year"]),
            "isbn": request.form["isbn"],
            "pages": int(request.form["pages"]),
            "abstract": request.form["abstract"]
        }

        update_book_service(id, data)
        return redirect("/admin/books")

    return render_template("admin/pages/books/edit.html", book=book)


# =========================
# DELETE
# =========================
@main.route("/admin/books/delete/<id>")
def delete_book_route(id):
    delete_book_service(id)
    return redirect("/admin/books")

@main.route("/admin/articles")
def admin_articles():
    page = int(request.args.get("page", 1))
    limit = 5

    articles = get_articles_service(page, limit)
    total = count_articles_service()

    total_pages = max(1, (total // limit) + (1 if total % limit else 0))

    return render_template(
        "admin/pages/articles/list.html",
        articles=articles,
        page=page,
        total_pages=total_pages,
        limit=limit
    )

@main.route("/admin/articles/create", methods=["GET", "POST"])
def create_article():

    if request.method == "POST":
        data = {
            "title": request.form.get("title"),
            "year": int(request.form.get("year") or 0),
            "doi": request.form.get("doi"),
            "journal": request.form.get("journal"),
            "abstract": request.form.get("abstract")
        }

        create_article_service(data)

        return redirect("/admin/articles")

    return render_template("admin/pages/articles/create.html")

@main.route("/admin/articles/edit/<id>", methods=["GET", "POST"])
def edit_article(id):

    article = get_article_detail_service(id)

    if request.method == "POST":
        data = {
            "title": request.form.get("title"),
            "year": int(request.form.get("year") or 0),
            "doi": request.form.get("doi"),
            "journal": request.form.get("journal"),
            "abstract": request.form.get("abstract")
        }

        update_article_service(id, data)

        return redirect("/admin/articles")

    return render_template(
        "admin/pages/articles/edit.html",
        article=article
    )

@main.route("/admin/articles/<id>")
def detail_article(id):

    article = get_article_detail_service(id)

    return render_template(
        "admin/pages/articles/detail.html",
        article=article
    )

@main.route("/admin/articles/delete/<id>")
def delete_article(id):

    delete_article_service(id)

    return redirect("/admin/articles")

