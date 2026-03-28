const input = document.getElementById("search-input");
const box = document.getElementById("suggest-box");

// ===== SUGGEST =====
input.addEventListener("input", async function () {

    const q = this.value.trim();

    if (!q) {
        box.style.display = "none";
        return;
    }

    const res = await fetch(`/suggest?q=${q}`);
    const data = await res.json();

    box.innerHTML = "";

    if (!data.results.length) {
        box.style.display = "none";
        return;
    }

    data.results.forEach(item => {

        const div = document.createElement("div");
        div.classList.add("suggest-item");

        div.innerHTML = `
            <span class="suggest-icon">${getIcon(item.type)}</span>
            <span>${item.title}</span>
        `;

        // 👉 CLICK → đi thẳng detail
        div.onclick = () => {
            if (item.type === "Book") {
                window.location.href = `/book/${item.id}`;
            } else if (item.type === "Article") {
                window.location.href = `/article/${item.id}`;
            } else {
                window.location.href = `/thesis/${item.id}`;
            }
        };

        box.appendChild(div);
    });

    box.style.display = "block";
});

// ===== ICON =====
function getIcon(type) {
    if (type === "Book") return "📘";
    if (type === "Article") return "📰";
    if (type === "Thesis") return "🎓";
    return "📄";
}

// ===== CLICK OUTSIDE =====
document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-wrapper")) {
        box.style.display = "none";
    }
});

// ===== SAMPLE CLICK (🔥 FIX QUAN TRỌNG) =====
document.querySelectorAll(".search-suggestions span").forEach(el => {
    el.onclick = () => {
        const value = el.innerText;

        // 👉 redirect luôn (giống Google)
        window.location.href = `/search?query=${encodeURIComponent(value)}`;
    };
});