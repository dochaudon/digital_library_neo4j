function openTab(evt, tabId) {

    // 1. ẨN tất cả tab content
    document.querySelectorAll(".tab-content").forEach(tab => {
        tab.classList.remove("active");
    });

    // 2. BỎ active tất cả button
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    // 3. HIỆN tab được chọn
    const target = document.getElementById(tabId);
    if (target) {
        target.classList.add("active");
    }

    // 4. ACTIVE button
    evt.currentTarget.classList.add("active");
}
document.addEventListener("DOMContentLoaded", function () {

    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        document.getElementById("graph").innerHTML = "Không có dữ liệu liên kết";
        return;
    }

    const container = document.getElementById("graph");

    const nodes = new vis.DataSet(graphData.nodes);
    const edges = new vis.DataSet(graphData.edges);

    const data = { nodes, edges };

    const options = {
        nodes: {
            shape: "dot",
            size: 20,
            font: {
                size: 14,
                color: "#333",
                vadjust: 10
            }
        },

        edges: {
            width: 1.5,
            color: "#aaa",
            smooth: true
        },

        groups: {
            book: { size: 30, color: "#2563eb" },
            article: { size: 30, color: "#2563eb" },
            author: { color: "#16a34a" },
            topic: { shape: "triangle", color: "#f59e0b" },
            keyword: { shape: "diamond", color: "#9333ea" },
            publisher: { color: "#0ea5e9" },
            language: { color: "#ec4899" },
            related_book: { color: "#6b7280" },
            related_article: { color: "#6b7280" }
        },

        physics: { enabled: true },
        interaction: { hover: true }
    };

    const network = new vis.Network(container, data, options);

    // 🔥 CLICK NODE
    network.on("click", (params) => {

        if (!params.nodes || params.nodes.length === 0) return;

        const node = nodes.get(params.nodes[0]);
        if (!node) return;

        console.log("CLICK:", node);

        const type = (node.group || "").toLowerCase();

        // ===== AUTHOR → POPUP =====
        if (type === "author") {
            const name = node.label;

            fetch(`/api/author_preview?name=${encodeURIComponent(name)}`)
                .then(res => res.json())
                .then(data => {
                    console.log("PREVIEW DATA:", data);
                    showAuthorPreview(data);
                });

            return; // 🔥 QUAN TRỌNG
        }

        // ===== RELATED BOOK =====
        if (type === "related_book") {
            const id = String(node.id).replace("rel-", "");
            window.location.href = `/book/${encodeURIComponent(id)}`;
            return;
        }

        // ===== RELATED ARTICLE =====
        if (type === "related_article") {
            const id = String(node.id).replace("rel-", "");
            window.location.href = `/article/${encodeURIComponent(id)}`;
            return;
        }

        // ===== TOPIC =====
        if (type === "topic") {
            window.location.href = `/search?query=${encodeURIComponent(node.label)}`;
            return;
        }

        // ===== PUBLISHER =====
        if (type === "publisher") {
            window.location.href = `/search?query=${encodeURIComponent(node.label)}`;
            return;
        }

        // ===== DEFAULT =====
        window.location.href = `/search?query=${encodeURIComponent(node.label)}`;
    });
});

function showAuthorPreview(data) {

    const box = document.getElementById("authorPreview");
    const name = document.getElementById("previewName");
    const list = document.getElementById("previewList");
    const btn = document.getElementById("viewAllBtn");

    name.innerText = data.name;
    list.innerHTML = "";

    data.documents.forEach(doc => {

        let url = "#";
        let icon = "📄";
        let typeClass = "";

        // 🔥 PHÂN LOẠI
        if (doc.type === "Book") {
            url = `/book/${doc.id}`;
            icon = "📘";
            typeClass = "type-book";
        }
        else if (doc.type === "Article") {
            url = `/article/${doc.id}`;
            icon = "📰";
            typeClass = "type-article";
        }
        else if (doc.type === "Thesis") {
            url = `/thesis/${doc.id}`;
            icon = "🎓";
            typeClass = "type-thesis";
        }

        list.innerHTML += `
            <div class="preview-item">
                <a href="${url}">
                    <span class="doc-icon">${icon}</span>
                    <span class="doc-title">${doc.title}</span>
                </a>

                <span class="doc-type ${typeClass}">
                    ${doc.type}
                </span>
            </div>
        `;
    });

    btn.href = `/author/${data.name}`;

    box.classList.remove("hidden");
}
document.getElementById("authorPreview").addEventListener("click", function(e) {
    e.stopPropagation(); // 🔥 CHẶN không cho graph nhận click
});