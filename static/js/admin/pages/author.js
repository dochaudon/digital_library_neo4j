document.addEventListener("DOMContentLoaded", () => {

    const rows = Array.from(document.querySelectorAll("tbody tr"));
    const searchInput = document.getElementById("searchInput");
    const pagination = document.getElementById("pagination");

    let currentPage = 1;
    const pageSize = 5;

    let filteredRows = [...rows];

    // ================= SEARCH =================
    if (searchInput) {
        searchInput.addEventListener("input", () => {
            const keyword = searchInput.value.toLowerCase();

            filteredRows = rows.filter(row => {
                const text = row.innerText.toLowerCase();
                return text.includes(keyword);
            });

            currentPage = 1;
            renderTable();
        });
    }

    // ================= RENDER =================
    function renderTable() {

        rows.forEach(r => r.style.display = "none");

        const start = (currentPage - 1) * pageSize;
        const paginated = filteredRows.slice(start, start + pageSize);

        paginated.forEach(r => r.style.display = "");

        renderPagination(filteredRows.length);
    }

    // ================= PAGINATION =================
    function renderPagination(total) {

        if (!pagination) return;

        const totalPages = Math.ceil(total / pageSize);
        pagination.innerHTML = "";

        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement("button");
            btn.innerText = i;

            if (i === currentPage) {
                btn.classList.add("active");
            }

            btn.onclick = () => {
                currentPage = i;
                renderTable();
            };

            pagination.appendChild(btn);
        }
    }

    // INIT
    renderTable();
});