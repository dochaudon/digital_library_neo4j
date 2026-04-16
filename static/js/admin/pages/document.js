document.addEventListener("DOMContentLoaded", () => {
    loadDocuments();
});

async function loadDocuments() {
    const res = await fetch("/admin/documents");
    const data = await res.json();

    const table = document.getElementById("documentTable");
    table.innerHTML = "";

    data.forEach(doc => {
        table.innerHTML += `
        <tr>
            <td>${doc.title}</td>
            <td>${doc.year || ""}</td>
            <td>${doc.type}</td>
            <td>
                <a href="/admin/documents/edit/${doc.id}" class="btn btn-warning btn-sm">Edit</a>
                <button onclick="deleteDoc('${doc.id}')" class="btn btn-danger btn-sm">Delete</button>
            </td>
        </tr>
        `;
    });
}

async function deleteDoc(id) {
    if (!confirm("Delete this document?")) return;

    await fetch(`/admin/documents/${id}`, {
        method: "DELETE"
    });

    loadDocuments();
}