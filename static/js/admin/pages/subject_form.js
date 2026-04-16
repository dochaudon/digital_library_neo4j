function saveSubject() {
    const id = document.getElementById("subjectId").value;
    const name = document.getElementById("name").value;

    const method = id ? "PUT" : "POST";
    const url = id ? `/admin/subjects/${id}` : "/admin/subjects";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    }).then(() => {
        window.location.href = "/admin/subjects/page";
    });
}