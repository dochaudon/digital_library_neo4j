document.addEventListener("DOMContentLoaded", () => {
    loadAuthors();
});

const BASE_URL = "/admin/metadata/author";

function loadAuthors() {
    fetch(BASE_URL)
        .then(res => res.json())
        .then(data => {
            console.log("DATA:", data);

            const table = document.getElementById("authorTable");
            if (!table) {
                console.error("❌ Không tìm thấy #authorTable");
                return;
            }

            table.innerHTML = "";

            data.forEach(a => {
                table.innerHTML += `
                    <tr>
                        <td>${a.id}</td>
                        <td>${a.name}</td>
                        <td>
                            <a href="/admin/metadata/author/edit/${a.id}" class="btn-edit">Edit</a>
                            <button onclick="deleteAuthor('${a.id}')" class="btn-delete">Delete</button>
                        </td>
                    </tr>
                `;
            });
        })
        .catch(err => console.error("❌ Fetch error:", err));
}

function deleteAuthor(id) {
    if (!confirm("Delete this author?")) return;

    fetch(`${BASE_URL}/${id}`, {
        method: "DELETE"
    })
    .then(() => loadAuthors())
    .catch(err => console.error("❌ Delete error:", err));
}