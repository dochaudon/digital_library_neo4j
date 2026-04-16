document.addEventListener("DOMContentLoaded", () => {
    loadKeywords();
});

function loadKeywords() {
    fetch("/admin/keywords")
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("keywordTable");
            table.innerHTML = "";

            data.forEach(k => {
                table.innerHTML += `
                    <tr>
                        <td>${k.name}</td>
                        <td>
                            <a href="/admin/keywords/edit/${k.id}">Edit</a>
                            <button onclick="deleteKeyword('${k.id}')">Delete</button>
                        </td>
                    </tr>
                `;
            });
        });
}

function deleteKeyword(id) {
    if (!confirm("Delete this keyword?")) return;

    fetch(`/admin/keywords/${id}`, {
        method: "DELETE"
    }).then(() => loadKeywords());
}