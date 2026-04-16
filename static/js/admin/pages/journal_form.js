function saveJournal() {
    const id = document.getElementById("journalId").value;
    const name = document.getElementById("name").value;

    const method = id ? "PUT" : "POST";
    const url = id ? `/admin/journals/${id}` : "/admin/journals";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    }).then(() => {
        window.location.href = "/admin/journals/page";
    });
}

