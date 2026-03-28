// Auto focus search input
document.addEventListener("DOMContentLoaded", () => {
    const input = document.querySelector(".search-form input[name='query']");
    if (input) input.focus();
});