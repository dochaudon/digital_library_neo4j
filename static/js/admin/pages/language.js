document.addEventListener("DOMContentLoaded", () => {
    loadLanguages();
});

function loadLanguages() {
    fetch("/admin/languages")
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("languageTable");
            table.innerHTML = "";

            data.forEach(l => {
                table.innerHTML += `
                    <tr>
                        <td>${l.name}</td>
                        <td>
                            <a href="/admin/languages/edit/${l.id}">Edit</a>
                            <button onclick="deleteLanguage('${l.id}')">Delete</button>
                        </td>
                    </tr>
                `;
            });
        });
}

function deleteLanguage(id) {
    if (!confirm("Delete this language?")) return;

    fetch(`/admin/languages/${id}`, {
        method: "DELETE"
    }).then(() => loadLanguages());
}