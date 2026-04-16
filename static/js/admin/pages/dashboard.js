document.addEventListener("DOMContentLoaded", () => {
    console.log("Admin Dashboard Loaded 🚀");

    // Ví dụ animation nhỏ
    const cards = document.querySelectorAll(".stat-card");

    cards.forEach((card, index) => {
        card.style.opacity = 0;
        card.style.transform = "translateY(20px)";

        setTimeout(() => {
            card.style.transition = "0.5s";
            card.style.opacity = 1;
            card.style.transform = "translateY(0)";
        }, index * 150);
    });
});