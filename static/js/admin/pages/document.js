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
document.getElementById("searchInput").addEventListener("input", function () {
    const keyword = this.value.toLowerCase();
    const rows = document.querySelectorAll("#docTableBody tr");

    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(keyword) ? "" : "none";
    });
});