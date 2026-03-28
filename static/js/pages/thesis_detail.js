// =========================
// TAB
// =========================
function openTab(evt, tabId) {

    document.querySelectorAll(".tab-content").forEach(tab => {
        tab.classList.remove("active");
    });

    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    const target = document.getElementById(tabId);
    if (target) {
        target.classList.add("active");
    }

    evt.currentTarget.classList.add("active");
}


// =========================
// PDF VIEWER
// =========================
function togglePdfViewer() {
    const viewer = document.getElementById("pdf-viewer");
    if (!viewer) return;
    viewer.classList.toggle("hidden");
}


// =========================
// GRAPH
// =========================
document.addEventListener("DOMContentLoaded", function () {

    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        document.getElementById("graph").innerHTML = "Không có dữ liệu liên kết";
        return;
    }

    const container = document.getElementById("graph");

    // ===== FIX DATA =====
    graphData.nodes.forEach(node => {

        // 🔥 FIX 1: bỏ shape từ backend
        if (node.shape) {
            delete node.shape;
        }

        // 🔥 FIX 2: cắt label dài
        if (node.label && node.label.length > 50) {
            node.label = node.label.substring(0, 50) + "...";
        }
    });

    const nodes = new vis.DataSet(graphData.nodes);
    const edges = new vis.DataSet(graphData.edges);

    const data = { nodes, edges };

    const options = {

        nodes: {
            size: 20,
            font: {
                size: 14,
                color: "#333",
                vadjust: 10
            },
            scaling: {
                min: 10,
                max: 30
            }
        },

        edges: {
            width: 1.5,
            color: "#aaa",
            smooth: true
        },

        groups: {

            thesis: {
                shape: "square",
                size: 30,
                color: "#9333ea"
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

            university: {
                shape: "dot",
                color: "#0ea5e9"
            },

            language: {
                shape: "star",
                color: "#ec4899"
            },

            related: {
                shape: "dot",
                color: "#6b7280"
            }
        },

        physics: {
            enabled: true,
            solver: "forceAtlas2Based",
            stabilization: false
        },

        interaction: {
            hover: true,
            zoomView: true,
            dragView: true
        }
    };

    const network = new vis.Network(container, data, options);


    // =========================
    // CLICK NODE
    // =========================
    network.on("click", (params) => {

        if (!params.nodes || params.nodes.length === 0) return;

        const node = nodes.get(params.nodes[0]);
        if (!node) return;

        if (node.kind === "thesis") return;

        if (node.kind === "related_thesis") {
            const id = String(node.id).replace("rel-", "");
            window.location.href = `/thesis/${encodeURIComponent(id)}`;
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

        if (node.kind === "university") {
            window.location.href = `/search?query=${encodeURIComponent(node.label)}`;
            return;
        }

        if (node.kind === "language") {
            window.location.href = `/search?query=${encodeURIComponent(node.label)}`;
            return;
        }

        // default
        window.location.href = `/search?query=${encodeURIComponent(node.label)}`;
    });

});