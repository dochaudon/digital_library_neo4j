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


// 🔥 THÊM (book có thiếu → article cần)
function togglePdfViewer() {
    const viewer = document.getElementById("pdf-viewer");
    if (!viewer) return;
    viewer.classList.toggle("hidden");
}


document.addEventListener("DOMContentLoaded", function () {

    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        document.getElementById("graph").innerHTML = "Không có dữ liệu liên kết";
        return;
    }

    const container = document.getElementById("graph");

    // 🔥 phải tách riêng ra (GIỮ NGUYÊN)
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

            book: {
                shape: "dot",
                size: 30,
                color: "#2563eb"
            },

            // 🔥 CHỈ SỬA CHỖ NÀY
            article: {
                shape: "dot",
                size: 30,
                color: "#2563eb"
            },

            author: {
                shape: "dot",
                color: "#16a34a"
            },

            topic: {
                shape: "triangle",
                color: "#f59e0b"
            },

            keyword: {
                shape: "diamond",
                color: "#9333ea"
            },

            publisher: {
                shape: "dot",
                color: "#0ea5e9"
            },

            // 🔥 CHỈ SỬA: thêm journal cho article
            journal: {
                shape: "dot",
                color: "#0ea5e9"
            },

            language: {
                shape: "dot",
                color: "#ec4899"
            },

            related_book: {
                shape: "dot",
                color: "#6b7280"
            },

            // 🔥 giữ nguyên như book nhưng dùng cho article
            related_article: {
                shape: "dot",
                color: "#6b7280"
            }
        },

        physics: {
            enabled: true,
            stabilization: false
        },

        interaction: {
            hover: true
        }
    };

    const network = new vis.Network(container, data, options);

    /* =========================
       CLICK NODE (GIỮ NGUYÊN)
    ========================= */

    network.on("click", (params) => {

        if (!params.nodes || params.nodes.length === 0) return;

        const node = nodes.get(params.nodes[0]);  // 🔥 đúng
        if (!node) return;

        // 🔥 CHỈ SỬA NHẸ (thêm article)
        if (node.kind === "book" || node.kind === "article") return;

        // ===== RELATED BOOK =====
        if (node.kind === "related_book") {
            const id = String(node.id).replace("rel-", "");
            window.location.href = `/book/${encodeURIComponent(id)}`;
            return;
        }

        // 🔥 THÊM (article)
        if (node.kind === "related_article") {
            const id = String(node.id).replace("rel-", "");
            window.location.href = `/article/${encodeURIComponent(id)}`;
            return;
        }

        // ===== AUTHOR =====
        if (node.kind === "author") {
            window.location.href = `/search?author=${encodeURIComponent(node.label)}`;
            return;
        }

        // ===== TOPIC =====
        if (node.kind === "topic") {
            window.location.href = `/search?topic=${encodeURIComponent(node.label)}`;
            return;
        }

        // ===== PUBLISHER =====
        if (node.kind === "publisher") {
            window.location.href = `/search?publisher=${encodeURIComponent(node.label)}`;
            return;
        }

        // 🔥 THÊM (journal)
        if (node.kind === "journal") {
            window.location.href = `/search?query=${encodeURIComponent(node.label)}`;
            return;
        }

        // ===== LANGUAGE =====
        if (node.kind === "language") {
            window.location.href = `/search?query=${encodeURIComponent(node.label)}`;
            return;
        }

        // ===== DEFAULT =====
        window.location.href = `/search?query=${encodeURIComponent(node.label)}`;
    });

});


// =========================
// 🔥 GIỮ NGUYÊN BLOCK 2 (y chang book)
// =========================
document.addEventListener("DOMContentLoaded", function () {

    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        document.getElementById("graph").innerHTML = "Không có dữ liệu liên kết";
        return;
    }

    const container = document.getElementById("graph");

    const data = {
        nodes: new vis.DataSet(graphData.nodes),
        edges: new vis.DataSet(graphData.edges)
    };

    const options = {

        nodes: {
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
        book: {
            shape: "dot",
            size: 30,
            color: "#2563eb"
        },

        // 🔥 thêm article
        article: {
            shape: "dot",
            size: 30,
            color: "#2563eb"
        },

        author: {
            shape: "dot",
            color: "#16a34a"
        },

        topic: {
            shape: "triangle",
            color: "#f59e0b"
        },

        keyword: {
            shape: "diamond",
            color: "#9333ea"
        },

        publisher: {
            shape: "dot",
            color: "#0ea5e9"
        },

        language: {
            shape: "dot",
            color: "#ec4899"
        },

        related: {
            shape: "dot",
            color: "#6b7280"
        }
        },

        physics: {
            enabled: true,
            stabilization: false
        },

        interaction: {
            hover: true
        }
    };

    const network = new vis.Network(container, data, options);

    network.on("click", (params) => {

        if (!params.nodes || params.nodes.length === 0) return;

        const nodeId = params.nodes[0];
        const node = data.nodes.get(nodeId);

        if (!node) return;

        // 🔥 thêm article
        if (node.kind === "book" || node.kind === "article") return;

        if (node.kind === "related_book") {
            const relatedId = String(node.id).replace("rel-", "");
            window.location.href = `/book/${encodeURIComponent(relatedId)}`;
            return;
        }

        // 🔥 thêm article
        if (node.kind === "related_article") {
            const relatedId = String(node.id).replace("rel-", "");
            window.location.href = `/article/${encodeURIComponent(relatedId)}`;
            return;
        }

        if (node.kind === "author") {
            window.location.href = `/search?author=${encodeURIComponent(node.label)}`;
            return;
        }

        if (node.kind === "topic") {
            window.location.href = `/search?topic=${encodeURIComponent(node.label)}`;
            return;
        }

        if (node.kind === "publisher") {
            window.location.href = `/search?publisher=${encodeURIComponent(node.label)}`;
            return;
        }

        if (node.kind === "language") {
            window.location.href = `/search?query=${encodeURIComponent(node.label)}`;
            return;
        }

        window.location.href = `/search?query=${encodeURIComponent(node.label)}`;
    });

});