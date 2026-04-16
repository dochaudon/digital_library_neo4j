function saveInstitution() {
    const id = document.getElementById("instId").value;
    const name = document.getElementById("name").value;
    const type = document.getElementById("type").value;

    const method = id ? "PUT" : "POST";
    const url = id ? `/admin/institutions/${id}` : "/admin/institutions";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, type })
    }).then(() => {
        window.location.href = "/admin/institutions/page";
    });
}