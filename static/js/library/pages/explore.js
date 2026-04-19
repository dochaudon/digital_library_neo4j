let network = null;
let nodes = null;
let edges = null;

let currentType = null;
let currentId = null;


// =========================
// INIT
// =========================
document.addEventListener("DOMContentLoaded", () => {
    loadEntity(ENTITY_TYPE, ENTITY_ID);
});


// =========================
// LOAD ENTITY
// =========================
async function loadEntity(type, id, page = 1) {

    currentType = type;
    currentId = id;

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

    let html = "";

    if (data.type === "author" || data.type === "subject") {

        html += `<h3>${data.type === "author" ? "📚 Tài liệu của tác giả" : "📂 Tài liệu theo chủ đề"}</h3>`;

        data.documents.forEach(d => {
            html += `
                <div class="item-card"
                     onclick="loadEntity('document','${d.id}')">
                    <div class="item-title">${truncate(d.title)}</div>
                    <div class="item-meta">📅 ${d.year || "N/A"}</div>
                </div>
            `;
        });

        html += renderPagination(type, id, data.page, data.total);
    }

    else if (data.type === "document") {

        const d = data.data;

        html += `
            <h3>${d.title}</h3>
            <p>📅 ${d.year || "N/A"}</p>
            <p>👤 ${d.authors?.join(", ") || "N/A"}</p>
            <p>📂 ${d.subjects?.join(", ") || "N/A"}</p>
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

    const radius = 180; // khoảng cách vòng tròn

    const mappedNodes = graphData.nodes.map((n, index) => {

        // 🎯 NODE TRUNG TÂM
        if (n.id === centerId) {
            return {
                ...n,
                x: 0,
                y: 0,
                fixed: true,
                label: getLabel(n)
            };
        }

        // 🎯 NODE XUNG QUANH (vòng tròn)
        const angle = (2 * Math.PI * index) / graphData.nodes.length;

        return {
            ...n,
            x: radius * Math.cos(angle),
            y: radius * Math.sin(angle),
            fixed: true,
            label: getLabel(n)
        };
    });

    nodes = new vis.DataSet(mappedNodes);
    edges = new vis.DataSet(graphData.edges);

    const data = { nodes, edges };

    const options = {

        nodes: {
            shape: "dot",
            size: 18,
            font: {
                size: 13,
                vadjust: 25
            }
        },

        edges: {
            smooth: false,
            width: 1.5,
            color: "#aaa"
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

        physics: false // 🔥 TẮT physics để giữ layout
    };

    if (!network) {
        network = new vis.Network(container, data, options);

        network.on("click", onNodeClick);
        network.on("doubleClick", onNodeDoubleClick);

    } else {
        network.setData(data);
    }

    // 🔥 luôn fit
    setTimeout(() => {
        network.fit({
            animation: true
        });
    }, 100);
}
function getLabel(node) {

    if (node.group === "author") {
        return node.name || node.label;
    }

    if (["book", "article", "thesis"].includes(node.group)) {
        return truncate(node.title || node.label);
    }

    if (node.group === "subject") {
        return node.name || node.label;
    }

    if (node.group === "keyword") {
        return node.name || node.label;
    }

    if (node.group === "publisher") {
        return node.name || node.label;
    }

    return node.label;
}

// =========================
// CLICK NODE
// =========================
async function onNodeClick(params) {

    if (!params.nodes.length) return;

    const node = nodes.get(params.nodes[0]);
    if (!node) return;

    const type = node.group;
    const id = node.id;

    const popup = document.getElementById("graph-popup");
    popup.classList.remove("hidden");

    const titleEl = document.getElementById("popup-title");
    const contentEl = document.getElementById("popup-content");
    const btn = document.getElementById("popup-view-btn");

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

    titleEl.innerText = "Tài liệu liên quan";
    contentEl.innerHTML = "Đang tải...";
    btn.style.display = "none";

    const res = await fetch(`/api/preview/${type}/${id}`);
    const data = await res.json();

    let html = "";

    if (data.documents) {
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

    window.location.href = `/explore/${node.group}/${node.id}`;
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

    const totalPages = Math.ceil(total / 10);
    if (totalPages <= 1) return "";

    let html = `<div class="pagination">`;

    if (page > 1) {
        html += `<button onclick="loadEntity('${type}','${id}',${page-1})">«</button>`;
    }

    html += `<span>Trang ${page} / ${totalPages}</span>`;

    if (page < totalPages) {
        html += `<button onclick="loadEntity('${type}','${id}',${page+1})">»</button>`;
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