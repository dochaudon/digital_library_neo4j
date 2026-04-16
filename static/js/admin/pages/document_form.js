document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;
    const id = path.split("/").pop();

    if (id !== "create") {
        loadDetail(id);
        document.getElementById("formTitle").innerText = "✏️ Update Document";
    }

    document.getElementById("documentForm")
        .addEventListener("submit", submitForm);
});

async function loadDetail(id) {
    const res = await fetch(`/admin/documents/${id}`);
    const doc = await res.json();

    document.getElementById("docId").value = doc.id;
    document.getElementById("title").value = doc.title;
    document.getElementById("year").value = doc.year;
    document.getElementById("pages").value = doc.pages;
    document.getElementById("abstract").value = doc.abstract;
    document.getElementById("file_url").value = doc.file_url;
    document.getElementById("type").value = doc.type;

    document.getElementById("authors").value =
        doc.authors_info.map(a => a.name).join(", ");
}

async function submitForm(e) {
    e.preventDefault();

    const id = document.getElementById("docId").value;

    const data = {
        type: document.getElementById("type").value,
        title: document.getElementById("title").value,
        year: parseInt(document.getElementById("year").value),
        pages: document.getElementById("pages").value,
        abstract: document.getElementById("abstract").value,
        file_url: document.getElementById("file_url").value,
        authors: document.getElementById("authors").value.split(",").map(x => x.trim())
    };

    if (id) {
        await fetch(`/admin/documents/${id}`, {
            method: "PUT",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });
    } else {
        await fetch("/admin/documents", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });
    }

    window.location.href = "/admin/documents";
}