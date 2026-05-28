document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("toggleSidebar");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");

    function openMobileSidebar() {
        sidebar.classList.add("is-open");
        overlay.classList.add("is-visible");
        document.body.style.overflow = "hidden";
    }

    function closeMobileSidebar() {
        sidebar.classList.remove("is-open");
        if (overlay) overlay.classList.remove("is-visible");
        document.body.style.overflow = "";
    }

    if (btn) {
        btn.addEventListener("click", function () {
            if (window.innerWidth <= 992) {
                // Mobile behavior: drawer
                if (sidebar.classList.contains("is-open")) {
                    closeMobileSidebar();
                } else {
                    openMobileSidebar();
                }
            } else {
                // Desktop behavior: collapse
                sidebar.classList.toggle("collapsed");
            }
        });
    }

    if (overlay) {
        overlay.addEventListener("click", closeMobileSidebar);
    }

    // Reset state on resize
    window.addEventListener("resize", function () {
        if (window.innerWidth > 992) {
            closeMobileSidebar();
        }
    });
});