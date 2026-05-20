// =============================================
// SUBJECT GROUP GRAPH  –  group.js
// =============================================

document.addEventListener("DOMContentLoaded", () => {
    loadSubjectGraph();
    initKeyboardNav();
});

let network = null;
let nodes   = null;
let edges   = null;

// ─────────────────────────────────────────────
// CUSTOM MODAL  (replaces browser confirm())
// Avoids blocking vis-network's callback chain
// ─────────────────────────────────────────────
function sgConfirm(title, body, isDanger) {
    return new Promise(function (resolve) {
        const overlay  = document.getElementById("sg-modal-overlay");
        const titleEl  = document.getElementById("sg-modal-title");
        const bodyEl   = document.getElementById("sg-modal-body");
        const btnOk    = document.getElementById("sg-modal-confirm");
        const btnCancel= document.getElementById("sg-modal-cancel");

        titleEl.textContent = title;
        bodyEl.textContent  = body;
        btnOk.className     = isDanger ? "danger" : "";

        overlay.classList.add("active");

        function cleanup(result) {
            overlay.classList.remove("active");
            btnOk.removeEventListener("click", onOk);
            btnCancel.removeEventListener("click", onCancel);
            resolve(result);
        }
        function onOk()     { cleanup(true);  }
        function onCancel() { cleanup(false); }

        btnOk.addEventListener("click", onOk);
        btnCancel.addEventListener("click", onCancel);
    });
}

// ─────────────────────────────────────────────
// KEYBOARD NAVIGATION  (WASD + Arrow keys)
// ─────────────────────────────────────────────
const keysDown    = new Set();
let   panAnimFrame = null;

function initKeyboardNav() {
    document.addEventListener("keydown", function (e) {
        const tag = document.activeElement.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

        const navKeys = [
            "ArrowUp","ArrowDown","ArrowLeft","ArrowRight",
            "w","a","s","d","W","A","S","D",
            "=","+","-","_"
        ];
        if (navKeys.includes(e.key)) e.preventDefault();

        keysDown.add(e.key.toLowerCase());
        if (!panAnimFrame) panAnimFrame = requestAnimationFrame(doPan);
    });

    document.addEventListener("keyup", function (e) {
        keysDown.delete(e.key.toLowerCase());
        if (keysDown.size === 0 && panAnimFrame) {
            cancelAnimationFrame(panAnimFrame);
            panAnimFrame = null;
        }
    });

    window.addEventListener("blur", function () {
        keysDown.clear();
        if (panAnimFrame) { cancelAnimationFrame(panAnimFrame); panAnimFrame = null; }
    });
}

function doPan() {
    if (!network) { panAnimFrame = null; return; }

    const SPEED       = keysDown.has("shift") ? 24 : 10;
    const ZOOM_FACTOR = keysDown.has("shift") ? 0.08 : 0.03;
    let dx = 0, dy = 0;

    if (keysDown.has("w") || keysDown.has("arrowup"))    dy -= SPEED;
    if (keysDown.has("s") || keysDown.has("arrowdown"))  dy += SPEED;
    if (keysDown.has("a") || keysDown.has("arrowleft"))  dx -= SPEED;
    if (keysDown.has("d") || keysDown.has("arrowright")) dx += SPEED;

    if (dx !== 0 || dy !== 0) {
        const pos   = network.getViewPosition();
        const scale = network.getScale();
        network.moveTo({ position: { x: pos.x + dx / scale, y: pos.y + dy / scale }, animation: false });
    }
    if (keysDown.has("=") || keysDown.has("+")) {
        network.moveTo({ scale: Math.min(network.getScale() * (1 + ZOOM_FACTOR), 5), animation: false });
    }
    if (keysDown.has("-") || keysDown.has("_")) {
        network.moveTo({ scale: Math.max(network.getScale() * (1 - ZOOM_FACTOR), 0.05), animation: false });
    }

    panAnimFrame = keysDown.size > 0 ? requestAnimationFrame(doPan) : null;
}

// ─────────────────────────────────────────────
// LOAD  &  RENDER
// ─────────────────────────────────────────────
async function loadSubjectGraph() {
    const container = document.getElementById("subject-graph");
    container.innerHTML = "<div style='padding:20px'>Đang tải dữ liệu đồ thị...</div>";

    try {
        const res  = await fetch("/api/graph/subject-group");
        const data = await res.json();
        if (data.success) {
            renderGraph(data.nodes, data.edges);
        } else {
            container.innerHTML = `<div style='padding:20px;color:red'>Lỗi: ${data.message}</div>`;
        }
    } catch (e) {
        console.error(e);
        container.innerHTML = "<div style='padding:20px;color:red'>Lỗi kết nối API.</div>";
    }
}

function renderGraph(nodeData, edgeData) {
    const container = document.getElementById("subject-graph");
    container.innerHTML = "";

    nodes = new vis.DataSet(nodeData);
    edges = new vis.DataSet(edgeData);

    const options = {
        nodes: {
            shape: "dot",
            size: 20,
            font:  { size: 14, color: "#333", vadjust: -35 },
            borderWidth: 2,
            shadow: true,
            color: { background: "#f97316", border: "#ea580c" }
        },
        edges: {
            width: 2,
            color: { color: "#cbd5e1", hover: "#64748b", highlight: "#2563eb" },
            smooth: { type: "continuous", roundness: 0.5 },
            arrows: { to: { enabled: true, scaleFactor: 0.5 } }
        },
        physics: {
            enabled: true,
            solver: "forceAtlas2Based",
            forceAtlas2Based: {
                gravitationalConstant: -50,
                springLength: 200,
                springConstant: 0.05,
                damping: 0.4
            },
            stabilization: { iterations: 150 }
        },
        interaction: {
            hover: true,
            zoomView: true,
            dragNodes: true
        },
        manipulation: {
            enabled: true,
            initiallyActive: true,
            addNode: false,
            editNode: function (nodeData, callback) {
                callback(null);
            },
            deleteNode: false,

            // editEdge: cần có object để vis không tạo button "Edit Edge"
            // nhưng vẫn không cho phép kéo lại endpoint
            editEdge: {
                editWithoutDrag: function (edgeData, callback) {
                    callback(null);
                }
            },

            // ── DELETE EDGE ──────────────────────────────
            deleteEdge: function (edgeData, callback) {
                if (!edgeData.edges || edgeData.edges.length === 0) {
                    callback(null);
                    return;
                }

                const edgeId = edgeData.edges[0];
                const edge   = edges.get(edgeId);

                if (!edge) { callback(null); return; }

                // Bỏ qua anchor edges (invisible layout edges)
                if (String(edge.from).startsWith("anchor_") ||
                    String(edge.to).startsWith("anchor_")) {
                    callback(null);
                    return;
                }

                // Dùng custom modal thay vì confirm()
                sgConfirm("Xóa liên kết", "Bạn có chắc chắn muốn xóa liên kết này?", true)
                .then(function (ok) {
                    if (!ok) { callback(null); return; }

                    fetch("/api/graph/subject-group/unrelate", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ source_id: edge.from, target_id: edge.to })
                    })
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (data.success) {
                            callback(edgeData);
                        } else {
                            alert("Lỗi khi xóa liên kết: " + (data.message || ""));
                            callback(null);
                        }
                    })
                    .catch(function (e) {
                        console.error(e);
                        alert("Lỗi kết nối API.");
                        callback(null);
                    });
                });
            },

            // ── ADD EDGE ─────────────────────────────────
            addEdge: function (edgeData, callback) {
                // Self-loop
                if (edgeData.from === edgeData.to) {
                    alert("Không thể liên kết chủ đề với chính nó.");
                    callback(null);
                    return;
                }

                // Anchor nodes (invisible)
                if (String(edgeData.from).startsWith("anchor_") ||
                    String(edgeData.to).startsWith("anchor_")) {
                    callback(null);
                    return;
                }

                // Duplicate check
                const existing = edges.get({
                    filter: function (item) {
                        return (item.from === edgeData.from && item.to === edgeData.to) ||
                               (item.from === edgeData.to   && item.to === edgeData.from);
                    }
                });
                if (existing.length > 0) {
                    alert("Hai chủ đề này đã được liên kết với nhau.");
                    callback(null);
                    return;
                }

                // Lấy tên node để hiển thị trong modal
                const fromNode = nodes.get(edgeData.from);
                const toNode   = nodes.get(edgeData.to);
                const fromName = fromNode ? fromNode.label : edgeData.from;
                const toName   = toNode   ? toNode.label   : edgeData.to;

                // Dùng custom modal thay vì confirm()
                sgConfirm(
                    "Tạo liên kết",
                    `Tạo liên kết RELATED_TO giữa:\n"${fromName}" ↔ "${toName}"?`,
                    false
                )
                .then(function (ok) {
                    if (!ok) { callback(null); return; }

                    fetch("/api/graph/subject-group/relate", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ source_id: edgeData.from, target_id: edgeData.to })
                    })
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (data.success) {
                            edgeData.label = "RELATED_TO";
                            callback(edgeData);
                        } else {
                            alert("Lỗi khi lưu liên kết: " + (data.message || ""));
                            callback(null);
                        }
                    })
                    .catch(function (e) {
                        console.error(e);
                        alert("Lỗi kết nối API.");
                        callback(null);
                    });
                });
            }
        }
    };

    network = new vis.Network(container, { nodes, edges }, options);

    // Focus container để nhận keydown navigation
    container.setAttribute("tabindex", "0");
    container.addEventListener("click", function () { container.focus(); });
}
