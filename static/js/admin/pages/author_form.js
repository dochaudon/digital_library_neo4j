function saveAuthor() {
    const id = document.getElementById("authorId").value;
    const name = document.getElementById("name").value;

    const method = id ? "PUT" : "POST";
    const url = id ? `/admin/authors/${id}` : "/admin/authors";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    }).then(() => {
        window.location.href = "/admin/authors/page";
    });
}