const checkboxes = document.querySelectorAll(".filter-type");
const sortSelect = document.getElementById("sort-select");

function applyFilters() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // 1. Collect selected document types
    const selectedTypes = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);
    
    // 2. Update doc_type in URL (supporting multiple)
    urlParams.delete("doc_type");
    selectedTypes.forEach(type => {
        urlParams.append("doc_type", type);
    });

    // 3. Update sort in URL
    if (sortSelect && sortSelect.value) {
        urlParams.set("sort", sortSelect.value);
    } else {
        urlParams.delete("sort");
    }

    // 4. Always reset to page 1 when changing filters
    urlParams.set("page", "1");

    // 5. Reload page with new parameters
    const newUrl = window.location.pathname + "?" + urlParams.toString();
    window.location.href = newUrl;
}

// Event listeners
checkboxes.forEach(cb => cb.addEventListener("change", applyFilters));
if (sortSelect) {
    sortSelect.addEventListener("change", applyFilters);
}