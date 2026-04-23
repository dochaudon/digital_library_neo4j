const input = document.getElementById("search-input");
const box = document.getElementById("suggest-box");

let debounceTimer = null;

// ===== SUGGEST =====
input.addEventListener("input", function () {

    const q = this.value.trim();

    // clear timer cũ
    clearTimeout(debounceTimer);

    // debounce (tránh spam API)
    debounceTimer = setTimeout(async () => {

        if (!q || q.length < 2) {
            box.style.display = "none";
            box.innerHTML = "";
            return;
        }

        try {
            const res = await fetch(`/api/search/suggest?q=${encodeURIComponent(q)}`);
            const data = await res.json();

            box.innerHTML = "";

            if (!data.results || !data.results.length) {
                box.style.display = "none";
                return;
            }

            data.results.forEach(item => {

                const div = document.createElement("div");
                div.classList.add("suggest-item");

                div.innerHTML = `
                    <span class="suggest-icon">${getIcon(item.type)}</span>
                    <span>${highlightText(item.title, q)}</span>
                `;

                // 👉 CLICK → đi detail
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

        } catch (err) {
            console.error("Suggest error:", err);
            box.style.display = "none";
        }

    }, 300); // delay 300ms
});


// ===== HIGHLIGHT TEXT =====
function highlightText(text, keyword) {
    if (!keyword) return text;

    const regex = new RegExp(`(${keyword})`, "gi");
    return text.replace(regex, "<b>$1</b>");
}


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


// ===== ENTER SEARCH =====
input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        const value = input.value.trim();
        if (value) {
            window.location.href = `/search?query=${encodeURIComponent(value)}`;
        }
    }
});


// ===== SAMPLE CLICK (QUICK SUGGEST) =====
document.querySelectorAll(".search-suggestions span").forEach(el => {
    el.onclick = () => {
        const value = el.innerText;
        window.location.href = `/search?query=${encodeURIComponent(value)}`;
    };
});