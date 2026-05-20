let network = null;
let nodes = null;
let edges = null;

let currentType = null;
let currentId = null;

// =========================
// HISTORY STACK & BACK NAVIGATION
// =========================
let exploreHistory = [];
let originalDocUrl = "";

// Capture referrer document or initial document state
if (document.referrer && document.referrer.includes("/document/")) {
    originalDocUrl = document.referrer;
} else if (ENTITY_TYPE === "document") {
    originalDocUrl = `/document/${ENTITY_ID}`;
}

// =========================
// INIT
// =========================
document.addEventListener("DOMContentLoaded", () => {
    loadEntity(ENTITY_TYPE, ENTITY_ID);

    // Bind custom Back button
    const btnBack = document.getElementById("btn-back");
    if (btnBack) {
        btnBack.addEventListener("click", handleBackClick);
    }
});

function handleBackClick() {
    if (exploreHistory.length > 0) {
        const prev = exploreHistory.pop();
        loadEntity(prev.type, prev.id, 1, true);
    } else {
        if (originalDocUrl) {
            window.location.href = originalDocUrl;
        } else {
            // Fallback to home page if no history
            window.location.href = "/";
        }
    }
}

// =========================
// LOAD ENTITY
// =========================
async function loadEntity(type, id, page = 1, isBack = false) {

    type = type?.toLowerCase();

    // Push the current entity to history BEFORE updating it (if not backtrack)
    if (!isBack && currentType && currentId) {
        exploreHistory.push({ type: currentType, id: currentId });
    }

    currentType = type;
    currentId = id;

    // Dynamically replace the browser URL so refresh/copy works
    window.history.replaceState(null, "", `/explore/${type}/${id}`);

    closePopup();

    await loadLeft(type, id, page);
    await loadGraph(type, id);
}


// =========================
// LEFT PANEL
// =========================
async function loadLeft(type, id, page = 1) {

    const container = document.getElementById("explore-left");
    container.innerHTML = "Đang tải...";

    const res = await fetch(`/api/entity/${type}/${id}?page=${page}`);
    const data = await res.json();

    const entityType = data.type?.toLowerCase();

    let html = "";

    // ===== ENTITY LIST =====
    if (["author", "subject", "keyword", "publisher", "university", "journal"].includes(entityType)) {

        const titleMap = {
            author: "📚 Tác giả",
            subject: "📂 Chủ đề",
            keyword: "🏷️ Từ khóa",
            publisher: "🏢 Nhà xuất bản",
            university: "🎓 Trường đại học",
            journal: "📰 Tạp chí"
        };

        const displayName = data.name || "N/A";
        html += `<h3>${titleMap[entityType] || "Chi tiết"}: <span style="color:#2563eb">${displayName}</span></h3>`;

        if (!data.documents || data.documents.length === 0) {
            html += `<p>Không có tài liệu</p>`;
        } else {
            data.documents.forEach(d => {
                html += `
                    <div class="item-card"
                         onclick="loadEntity('document','${d.id}')">
                        <div class="item-title">${truncate(d.title)}</div>
                        <div class="item-meta">📅 ${d.year || "N/A"}</div>
                    </div>
                `;
            });
        }

        html += renderPagination(type, id, data.page, data.total);
    }

    // ===== DOCUMENT =====
    else if (entityType === "document") {

        const d = data.data;

        html += `<h3 style="margin-bottom: 15px; color: #1e293b; font-size: 1.25rem;">${d.title || "Tài liệu không tên"}</h3>`;

        if (d.journal && d.journal !== "N/A") {
            html += `<p style="margin-bottom: 8px;">📰 <strong>Tạp chí:</strong> ${d.journal}</p>`;
        }
        if (d.year && d.year !== "N/A") {
            html += `<p style="margin-bottom: 8px;">📅 <strong>Năm:</strong> ${d.year}</p>`;
        }

        const cleanAuthors = d.authors ? d.authors.filter(x => x && x !== "N/A") : [];
        if (cleanAuthors.length > 0) {
            html += `<p style="margin-bottom: 8px;">👤 <strong>Tác giả:</strong> ${cleanAuthors.join(", ")}</p>`;
        }

        const cleanSubjects = d.subjects ? d.subjects.filter(x => x && x !== "N/A") : [];
        if (cleanSubjects.length > 0) {
            html += `<p style="margin-bottom: 8px;">📂 <strong>Chủ đề:</strong> ${cleanSubjects.join(", ")}</p>`;
        }

        const cleanPublishers = d.publishers ? d.publishers.filter(x => x && x !== "N/A") : [];
        if (cleanPublishers.length > 0) {
            html += `<p style="margin-bottom: 8px;">🏢 <strong>Nhà xuất bản:</strong> ${cleanPublishers.join(", ")}</p>`;
        }

        const cleanUniversities = d.universities ? d.universities.filter(x => x && x !== "N/A") : [];
        if (cleanUniversities.length > 0) {
            html += `<p style="margin-bottom: 8px;">🎓 <strong>Trường đại học:</strong> ${cleanUniversities.join(", ")}</p>`;
        }

        html += `
            <br>
            <a class="btn-detail" href="/document/${d.id}">
                Xem chi tiết
            </a>
        `;
    }

    container.innerHTML = html;
}


// =========================
// LOAD GRAPH
// =========================
async function loadGraph(type, id) {

    const res = await fetch(`/api/graph/${type}/${id}`);
    const graphData = await res.json();

    renderGraph(graphData);
}


// =========================
// RENDER GRAPH
// =========================
function renderGraph(graphData) {

    const container = document.getElementById("explore-graph");

    const centerId = graphData.center_id;
    const radius = 180;

    const mappedNodes = graphData.nodes.map((n, index) => {
        const group = n.group?.toLowerCase();
        const nodeCount = graphData.nodes.length;
        const radius = 180;

        let x = 0;
        let y = 0;
        let fixed = false;

        if (n.id === centerId) {
            x = 0;
            y = 0;
            fixed = { x: true, y: true };
            return {
                ...n,
                group,
                x, y, fixed,
                label: getLabel({ ...n, group }),
                size: 30
            };
        }

        // OCD-friendly circle
        const angle = (2 * Math.PI * (index - 1)) / (nodeCount - 1);
        x = radius * Math.cos(angle);
        y = radius * Math.sin(angle);

        return {
            ...n,
            group,
            x, y, fixed,
            label: getLabel({ ...n, group })
        };
    });

    nodes = new vis.DataSet(mappedNodes);
    edges = new vis.DataSet(graphData.edges);

    const data = { nodes, edges };

    const options = {
        nodes: {
            shape: "dot",
            size: 20,
            font: {
                size: 14,
                color: "#333",
                vadjust: 35,
                multi: "html"
            },
            borderWidth: 2,
            shadow: {
                enabled: true,
                color: "rgba(0,0,0,0.2)",
                size: 10,
                x: 3,
                y: 3
            }
        },

        edges: {
            width: 2,
            color: { color: "#cbd5e1", hover: "#64748b", highlight: "#2563eb" },
            smooth: { type: "continuous", roundness: 0.5 }
        },

        groups: {
            book: { shape: "dot", color: { background: "#2563eb", border: "#1e40af" } },
            article: { shape: "square", color: { background: "#10b981", border: "#059669" } },
            thesis: { shape: "triangle", color: { background: "#8b5cf6", border: "#7c3aed" } },
            author: { shape: "dot", color: { background: "#fbbf24", border: "#d97706" } },
            subject: { shape: "diamond", color: { background: "#f97316", border: "#ea580c" } },
            keyword: { shape: "star", color: { background: "#ec4899", border: "#be185d" } },
            publisher: { shape: "triangleDown", color: { background: "#06b6d4", border: "#0891b2" } },
            university: { shape: "hexagon", color: { background: "#6366f1", border: "#4f46e5" } },
            journal: {
                shape: "image",
                image: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30" width="30" height="30"><polygon points="15,3 27,12 22,26 8,26 3,12" fill="%23ef4444" stroke="%23b91c1c" stroke-width="2"/></svg>'
            },
            category: { shape: "box", color: { background: "#14b8a6", border: "#0d9488" } },
            language: { shape: "ellipse", color: { background: "#64748b", border: "#475569" } }
        },

        physics: {
            enabled: true,
            solver: "forceAtlas2Based",
            forceAtlas2Based: {
                gravitationalConstant: -100,
                springLength: 150,
                springConstant: 0.05,
                damping: 0.4
            },
            stabilization: {
                iterations: 150,
                updateInterval: 25
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            zoomView: true,
            dragNodes: true
        }
    };

    if (!network) {
        network = new vis.Network(container, data, options);

        network.on("click", onNodeClick);
        network.on("doubleClick", onNodeDoubleClick);

    } else {
        network.setData(data);
    }

    setTimeout(() => {
        network.fit({ animation: true });
    }, 100);
}


// =========================
// LABEL FIX
// =========================
function getLabel(node) {

    const group = node.group?.toLowerCase();

    if (group === "author") {
        return node.name || node.label;
    }

    if (["book", "article", "thesis"].includes(group)) {
        return truncate(node.title || node.label);
    }

    if (["subject", "keyword", "publisher", "university", "journal", "category", "language"].includes(group)) {
        return node.name || node.label;
    }

    return node.label;
}


// =========================
// CLICK NODE (POPUP)
// =========================
async function onNodeClick(params) {

    if (!params.nodes.length) return;

    const node = nodes.get(params.nodes[0]);
    if (!node) return;

    const type = node.group?.toLowerCase();
    const id = node.id;

    const popup = document.getElementById("graph-popup");
    popup.classList.remove("hidden");

    const titleEl = document.getElementById("popup-title");
    const contentEl = document.getElementById("popup-content");
    const btn = document.getElementById("popup-view-btn");

    // ===== DOCUMENT =====
    if (["book", "article", "thesis"].includes(type)) {

        titleEl.innerText = "Thông tin tài liệu";

        const res = await fetch(`/api/preview/document/${id}`);
        const data = await res.json();

        contentEl.innerHTML = `
            <div class="popup-item">
                <b>${truncate(data.data?.title)}</b>
                <div style="font-size:12px;color:#888">
                    📅 ${data.data?.year || "N/A"}
                </div>
            </div>
        `;

        btn.style.display = "block";
        btn.innerText = "Xem chi tiết";

        btn.onclick = () => {
            window.location.href = `/document/${id}`;
        };

        return;
    }

    // ===== ENTITY =====
    titleEl.innerText = "Tài liệu liên quan";
    contentEl.innerHTML = "Đang tải...";
    btn.style.display = "none";

    const res = await fetch(`/api/preview/${type}/${id}`);
    const data = await res.json();

    let html = "";

    if (data.documents && data.documents.length > 0) {
        data.documents.forEach(d => {
            html += `
                <div class="popup-item"
                     onclick="loadEntity('document','${d.id}')">
                    📄 ${truncate(d.title)}
                </div>
            `;
        });
    } else {
        html = "<p>Không có dữ liệu</p>";
    }

    contentEl.innerHTML = html;
}


// =========================
// DOUBLE CLICK
// =========================
function onNodeDoubleClick(params) {

    if (!params.nodes.length) return;

    const node = nodes.get(params.nodes[0]);
    if (!node) return;

    const type = node.group?.toLowerCase();
    const id = node.id;

    loadEntity(type, id);
}


// =========================
// CLOSE POPUP
// =========================
function closePopup() {
    document.getElementById("graph-popup")?.classList.add("hidden");
}


// =========================
// PAGINATION
// =========================
function renderPagination(type, id, page, total) {

    const totalPages = Math.ceil((total || 0) / 10);
    if (totalPages <= 1) return "";

    let html = `<div class="pagination">`;

    if (page > 1) {
        html += `<button onclick="loadEntity('${type}','${id}',${page - 1})">«</button>`;
    }

    html += `<span>Trang ${page} / ${totalPages}</span>`;

    if (page < totalPages) {
        html += `<button onclick="loadEntity('${type}','${id}',${page + 1})">»</button>`;
    }

    html += `</div>`;

    return html;
}


// =========================
// UTILS
// =========================
function truncate(text, max = 60) {
    if (!text) return "";
    return text.length > max ? text.substring(0, max) + "..." : text;
}