document.addEventListener("DOMContentLoaded", () => {
    loadJournals();
});

function loadJournals() {
    fetch("/admin/journals")
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("journalTable");
            table.innerHTML = "";

            data.forEach(j => {
                table.innerHTML += `
                    <tr>
                        <td>${j.name}</td>
                        <td>
                            <a href="/admin/journals/edit/${j.id}">Edit</a>
                            <button onclick="deleteJournal('${j.id}')">Delete</button>
                        </td>
                    </tr>
                `;
            });
        });
}

function deleteJournal(id) {
    if (!confirm("Delete this journal?")) return;

    fetch(`/admin/journals/${id}`, {
        method: "DELETE"
    }).then(() => loadJournals());
}