const checkboxes = document.querySelectorAll(".filter-type");
const sortSelect = document.getElementById("sort-select");
const modeTabs = document.querySelectorAll(".mode-tab");
const searchTypeInput = document.getElementById("searchTypeInput");
const mainSearchForm = document.getElementById("mainSearchForm");

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

    // 4. Preserve search type
    if (searchTypeInput && searchTypeInput.value) {
        urlParams.set("search_type", searchTypeInput.value);
    }

    // 5. Always reset to page 1 when changing filters
    urlParams.set("page", "1");

    // 6. Reload page with new parameters
    const newUrl = window.location.pathname + "?" + urlParams.toString();
    window.location.href = newUrl;
}

// Search Mode Tab interactions
if (modeTabs && modeTabs.length > 0) {
    modeTabs.forEach(tab => {
        tab.addEventListener("click", function() {
            // Remove active class from all tabs
            modeTabs.forEach(t => t.classList.remove("active"));
            
            // Add active class to clicked tab
            this.classList.add("active");
            
            // Get selected mode
            const selectedMode = this.getAttribute("data-mode");
            
            // Set mode into hidden input
            if (searchTypeInput) {
                searchTypeInput.value = selectedMode;
            }
            
            // Submit search form immediately to get new results
            if (mainSearchForm) {
                mainSearchForm.submit();
            }
        });
    });
}

// Event listeners
checkboxes.forEach(cb => cb.addEventListener("change", applyFilters));
if (sortSelect) {
    sortSelect.addEventListener("change", applyFilters);
}