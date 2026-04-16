document.addEventListener("DOMContentLoaded", () => {
    loadInstitutions();
});

function loadInstitutions() {
    fetch("/admin/institutions")
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("institutionTable");
            table.innerHTML = "";

            data.forEach(i => {
                table.innerHTML += `
                    <tr>
                        <td>${i.name}</td>
                        <td>${i.type}</td>
                        <td>
                            <a href="/admin/institutions/edit/${i.id}">Edit</a>
                            <button onclick="deleteInstitution('${i.id}')">Delete</button>
                        </td>
                    </tr>
                `;
            });
        });
}

function deleteInstitution(id) {
    if (!confirm("Delete this institution?")) return;

    fetch(`/admin/institutions/${id}`, {
        method: "DELETE"
    }).then(() => loadInstitutions());
}