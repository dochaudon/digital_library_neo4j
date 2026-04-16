function saveKeyword() {
    const id = document.getElementById("keywordId").value;
    const name = document.getElementById("name").value;

    const method = id ? "PUT" : "POST";
    const url = id ? `/admin/keywords/${id}` : "/admin/keywords";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    }).then(() => {
        window.location.href = "/admin/keywords/page";
    });
}