document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("toggleSidebar");
    const sidebar = document.getElementById("sidebar");

    if (btn) {
        btn.addEventListener("click", function () {
            sidebar.classList.toggle("collapsed");
        });
    }
});