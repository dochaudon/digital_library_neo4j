
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
    if (target) target.classList.add("active");

    evt.currentTarget.classList.add("active");

    // 🔥 FIX GRAPH
    if (tabId === "graph") {
        setTimeout(() => {
            if (window.network) {
                window.network.redraw();
                window.network.fit({
                    animation: {
                        duration: 800,
                        easingFunction: "easeInOutQuad"
                    }
                });
            }
        }, 200);
    }
}


// =========================
// FORMAT LABEL
// =========================
function formatLabel(text) {
    if (!text) return "";

    const max = 25;
    let result = "";

    for (let i = 0; i < text.length; i += max) {
        result += text.substring(i, i + max) + "\n";
    }

    return result;
}


// =========================
// CLOSE POPUP
// =========================
function closePopup() {
    document.getElementById("graph-popup")?.classList.add("hidden");
}


// =========================
// MAIN
// =========================
document.addEventListener("DOMContentLoaded", function () {

    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        document.getElementById("graph-network").innerHTML = "Không có dữ liệu liên kết";
        return;
    }

    const container = document.getElementById("graph-network");

    const nodes = new vis.DataSet(
        graphData.nodes.map(n => ({
            ...n,
            label: formatLabel(n.label)
        }))
    );

    const edges = new vis.DataSet(graphData.edges);

    const data = { nodes, edges };

    const options = {

        nodes: {
            shape: "dot",
            size: 18,

            widthConstraint: {
                maximum: 120
            },

            font: {
                size: 13,
                color: "#111",
                vadjust: 30,
                multi: "html"
            },

            borderWidth: 2
        },

        edges: {
            width: 1.5,
            color: "#aaa",
            smooth: false   // ✅ thẳng luôn
        },

        groups: {
            book: { shape: "dot", size: 22, color: "#2563eb" },
            article: { shape: "dot", size: 22, color: "#16a34a" },
            thesis: { shape: "dot", size: 24, color: "#9333ea" },
            author: { shape: "dot", size: 18, color: "#22c55e" },
            subject: { shape: "diamond", size: 20, color: "#f59e0b" },
            keyword: { shape: "star", size: 20, color: "#ec4899" },
            publisher: { shape: "hexagon", size: 20, color: "#0ea5e9" }
        },

        physics: {
            solver: "forceAtlas2Based",
            forceAtlas2Based: {
                gravitationalConstant: -50,
                springLength: 120,
                springConstant: 0.08
            },
            stabilization: {
                iterations: 200
            }
        },

        interaction: {
            hover: true
        }
    };

    window.network = new vis.Network(container, data, options);
    // =========================
    // CENTER GRAPH
    // =========================
    network.once("stabilized", function () {
    setTimeout(() => {
        if (graphData.center_id) {
            network.focus(graphData.center_id, {
                scale: 1.2,
                animation: true
            });
        } else {
            network.fit({
                animation: true
            });
        }
    }, 100);
});


    // =========================
    // CLICK → POPUP
    // =========================
    network.on("click", async (params) => {

        if (!params.nodes.length) return;

        const node = nodes.get(params.nodes[0]);
        if (!node) return;

        const type = node.group;
        const id = node.id;

        const popup = document.getElementById("graph-popup");
        popup.classList.remove("hidden");

        document.getElementById("popup-title").innerText = node.label.replace(/\n/g, " ");

        try {
            const res = await fetch(`/api/preview/${type}/${id}`);
            const data = await res.json();

            let html = "";

            if (data.documents && data.documents.length > 0) {
                data.documents.forEach(d => {
                    html += `<div class="popup-item">${d.title}</div>`;
                });
            } else {
                html = "<p>Không có dữ liệu</p>";
            }

            document.getElementById("popup-content").innerHTML = html;

        } catch (err) {
            document.getElementById("popup-content").innerHTML = "Lỗi tải dữ liệu";
        }

        document.getElementById("popup-view-btn").onclick = () => {
            window.location.href = `/explore/${type}/${id}`;
        };
    });


    // =========================
    // DOUBLE CLICK → EXPLORE
    // =========================
    network.on("doubleClick", (params) => {

        if (!params.nodes.length) return;

        const node = nodes.get(params.nodes[0]);
        if (!node) return;

        window.location.href = `/explore/${node.group}/${node.id}`;
    });

});