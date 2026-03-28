const checkboxes = document.querySelectorAll(".filter-type");
const sortSelect = document.getElementById("sort-select");
const results = document.querySelectorAll(".result-card");
const container = document.getElementById("results-list");

function applyFilters() {

    let selectedTypes = Array.from(checkboxes)
        .filter(c => c.checked)
        .map(c => c.value);

    let items = Array.from(results);

    // ===== FILTER TYPE =====
    items.forEach(item => {
        const type = item.dataset.type;

        if (selectedTypes.length === 0 || selectedTypes.includes(type)) {
            item.style.display = "flex";
        } else {
            item.style.display = "none";
        }
    });

    // ===== SORT =====
    let visibleItems = items.filter(i => i.style.display !== "none");

    const sort = sortSelect.value;

    visibleItems.sort((a, b) => {

        const yearA = parseInt(a.dataset.year) || 0;
        const yearB = parseInt(b.dataset.year) || 0;

        const titleA = a.dataset.title.toLowerCase();
        const titleB = b.dataset.title.toLowerCase();

        if (sort === "year_desc") return yearB - yearA;
        if (sort === "year_asc") return yearA - yearB;
        if (sort === "az") return titleA.localeCompare(titleB);
        if (sort === "za") return titleB.localeCompare(titleA);

        return 0;
    });

    visibleItems.forEach(item => container.appendChild(item));
}

checkboxes.forEach(cb => cb.addEventListener("change", applyFilters));
sortSelect.addEventListener("change", applyFilters);