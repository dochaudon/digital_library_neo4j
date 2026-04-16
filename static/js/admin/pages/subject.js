document.addEventListener("DOMContentLoaded", () => {
    loadSubjects();
});

function loadSubjects() {
    fetch("/admin/subjects")
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("subjectTable");
            table.innerHTML = "";

            data.forEach(s => {
                table.innerHTML += `
                    <tr>
                        <td>${s.name}</td>
                        <td>
                            <a href="/admin/subjects/edit/${s.id}">Edit</a>
                            <button onclick="deleteSubject('${s.id}')">Delete</button>
                        </td>
                    </tr>
                `;
            });
        });
}

function deleteSubject(id) {
    if (!confirm("Delete this subject?")) return;

    fetch(`/admin/subjects/${id}`, {
        method: "DELETE"
    }).then(() => loadSubjects());
}