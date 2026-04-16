document.addEventListener("DOMContentLoaded", () => {
    loadUsers();
});

function loadUsers() {
    fetch("/admin/users")
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("userTable");
            table.innerHTML = "";

            data.forEach(u => {

                const statusColor = u.status === "active" ? "green" : "red";

                table.innerHTML += `
                    <tr>
                        <td>${u.username}</td>
                        <td>${u.email}</td>
                        <td>${u.role}</td>
                        <td style="color:${statusColor}">
                            ${u.status}
                        </td>
                        <td>
                            <button onclick="deactivateUser('${u.id}')">Deactivate</button>
                            <button onclick="deleteUser('${u.id}')">Delete</button>
                        </td>
                    </tr>
                `;
            });
        });
}


function deactivateUser(id) {
    if (!confirm("Deactivate this user?")) return;

    fetch(`/admin/users/${id}/deactivate`, {
        method: "PUT"
    }).then(() => loadUsers());
}


function deleteUser(id) {
    if (!confirm("Delete this user permanently?")) return;

    fetch(`/admin/users/${id}`, {
        method: "DELETE"
    }).then(() => loadUsers());
}