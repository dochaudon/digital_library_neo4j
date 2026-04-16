document.addEventListener("DOMContentLoaded", () => {
    loadAuthors();
});

function loadAuthors() {
    fetch("/admin/authors")
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("authorTable");
            table.innerHTML = "";

            data.forEach(a => {
                table.innerHTML += `
                    <tr>
                        <td>${a.name}</td>
                        <td>
                            <a href="/admin/authors/edit/${a.id}">Edit</a>
                            <button onclick="deleteAuthor('${a.id}')">Delete</button>
                        </td>
                    </tr>
                `;
            });
        });
}

function deleteAuthor(id) {
    if (!confirm("Delete this author?")) return;

    fetch(`/admin/authors/${id}`, {
        method: "DELETE"
    }).then(() => loadAuthors());
}