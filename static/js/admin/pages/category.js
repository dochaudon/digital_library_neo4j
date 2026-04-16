document.addEventListener("DOMContentLoaded", () => {
    loadCategories();
});

function loadCategories() {
    fetch("/admin/categories")
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("categoryTable");
            table.innerHTML = "";

            data.forEach(c => {
                table.innerHTML += `
                    <tr>
                        <td>${c.name}</td>
                        <td>
                            <a href="/admin/categories/edit/${c.id}">Edit</a>
                            <button onclick="deleteCategory('${c.id}')">Delete</button>
                        </td>
                    </tr>
                `;
            });
        });
}

function deleteCategory(id) {
    if (!confirm("Delete this category?")) return;

    fetch(`/admin/categories/${id}`, {
        method: "DELETE"
    }).then(() => loadCategories());
}