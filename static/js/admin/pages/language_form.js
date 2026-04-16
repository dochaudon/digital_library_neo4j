function saveLanguage() {
    const id = document.getElementById("langId").value;
    const name = document.getElementById("name").value;

    const method = id ? "PUT" : "POST";
    const url = id ? `/admin/languages/${id}` : "/admin/languages";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    }).then(() => {
        window.location.href = "/admin/languages/page";
    });
}