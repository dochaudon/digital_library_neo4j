
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
    } else {
        initGraph();
    }

    initCarousels();

    // Toggle Legend on click
    const toggleLegend = document.querySelector('.toggle-legend');
    if (toggleLegend) {
        const btn = toggleLegend.querySelector('.legend-btn');
        if (btn) {
            btn.addEventListener('click', function(e) {
                e.stopPropagation(); // prevent closing immediately if clicking outside is handled
                toggleLegend.classList.toggle('is-open');
            });
        }
    }
});

function initGraph() {
    const container = document.getElementById("graph-network");

    const centerId = graphData.center_id;
    const radius = 180;
    const nodeCount = graphData.nodes.length;

    const mappedNodes = graphData.nodes.map((n, index) => {
        const group = n.group?.toLowerCase();

        let x = 0;
        let y = 0;
        let fixed = false;

        if (n.id === centerId) {
            x = 0;
            y = 0;
            fixed = { x: true, y: true };
        } else {
            const angle = (2 * Math.PI * (index - 1)) / (nodeCount - 1);
            x = radius * Math.cos(angle);
            y = radius * Math.sin(angle);
        }

        return {
            ...n,
            group,
            x,
            y,
            fixed,
            label: formatLabel(n.label)
        };
    });

    const nodes = new vis.DataSet(mappedNodes);
    const edges = new vis.DataSet(graphData.edges);

    const data = { nodes, edges };

    const options = {
        nodes: {
            shape: "dot",
            size: 20,
            font: {
                size: 14,
                color: "#333",
                vadjust: 35,
                multi: "html",
                bold: { color: "#000" }
            },
            borderWidth: 2,
            shadow: { enabled: true, color: "rgba(0,0,0,0.2)", size: 10, x: 3, y: 3 },
            scaling: { label: { enabled: true, min: 14, max: 20 } }
        },
        edges: {
            width: 2,
            color: { color: "#cbd5e1", hover: "#64748b", highlight: "#2563eb" },
            smooth: { type: "continuous", roundness: 0.5 },
            arrows: { to: { enabled: false } },
            font: {
                size: 11,
                color: "#475569",
                face: "Inter, sans-serif",
                align: "middle"
            }
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
            forceAtlas2Based: { gravitationalConstant: -200, springLength: 250, springConstant: 0.03, damping: 0.4 },
            stabilization: { iterations: 150, updateInterval: 25 }
        },
        interaction: { hover: true, tooltipDelay: 200, zoomView: true, dragNodes: true }
    };

    window.network = new vis.Network(container, data, options);

    network.once("stabilized", function () {
        setTimeout(() => {
            if (graphData.center_id) {
                network.focus(graphData.center_id, { scale: 1.2, animation: true });
            } else {
                network.fit({ animation: true });
            }
        }, 100);
    });

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
            if (["book", "article", "thesis"].includes(type)) {
                html = `
                    <div class="popup-item" style="border-left: 3px solid #2563eb; padding-left: 10px; margin-bottom: 5px;">
                        <strong>Năm xuất bản:</strong> ${data.data ? (data.data.year || 'N/A') : 'N/A'}
                    </div>
                `;
            } else {
                if (data.documents && data.documents.length > 0) {
                    data.documents.forEach(d => { html += `<div class="popup-item">${d.title}</div>`; });
                } else {
                    html = "<p>Không có dữ liệu</p>";
                }
            }
            document.getElementById("popup-content").innerHTML = html;
        } catch (err) {
            document.getElementById("popup-content").innerHTML = "Lỗi tải dữ liệu";
        }

        document.getElementById("popup-view-btn").onclick = () => {
            if (["book", "article", "thesis"].includes(type)) {
                window.location.href = `/document/${id}`;
            } else {
                window.location.href = `/explore/${type}/${id}`;
            }
        };
    });

    network.on("doubleClick", (params) => {
        if (!params.nodes.length) return;
        const node = nodes.get(params.nodes[0]);
        if (!node) return;
        
        if (["book", "article", "thesis"].includes(node.group)) {
            window.location.href = `/document/${node.id}`;
        } else {
            window.location.href = `/explore/${node.group}/${node.id}`;
        }
    });
}

function initCarousels() {
    const containers = document.querySelectorAll('.carousel-container');
    containers.forEach(container => {
        const track = container.querySelector('.carousel-track');
        const nextBtn = container.querySelector('.carousel-control.next');
        const prevBtn = container.querySelector('.carousel-control.prev');

        if (!track || !nextBtn || !prevBtn) return;

        const slideWidth = 200; // 180 + 20 gap
        const totalSlides = track.children.length;

        const getVisibleCount = () => {
            const trackContainer = container.querySelector('.carousel-track-container');
            return trackContainer ? Math.floor(trackContainer.clientWidth / slideWidth) : 1;
        };

        const updateButtons = () => {
            const visibleCount = getVisibleCount();
            const canScroll = totalSlides > visibleCount;
            prevBtn.disabled = !canScroll;
            nextBtn.disabled = !canScroll;
        };

        let isAnimating = false;

        nextBtn.addEventListener('click', () => {
            const visibleCount = getVisibleCount();
            if (totalSlides <= visibleCount || isAnimating) return;
            isAnimating = true;

            track.style.transition = 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            track.style.transform = `translateX(-${slideWidth}px)`;

            setTimeout(() => {
                track.style.transition = 'none';
                track.appendChild(track.firstElementChild);
                track.style.transform = 'translateX(0)';
                // Force reflow
                track.offsetHeight;
                isAnimating = false;
            }, 500);
        });

        prevBtn.addEventListener('click', () => {
            const visibleCount = getVisibleCount();
            if (totalSlides <= visibleCount || isAnimating) return;
            isAnimating = true;

            track.style.transition = 'none';
            track.insertBefore(track.lastElementChild, track.firstElementChild);
            track.style.transform = `translateX(-${slideWidth}px)`;
            
            // Force reflow
            track.offsetHeight;

            track.style.transition = 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            track.style.transform = 'translateX(0)';

            setTimeout(() => {
                isAnimating = false;
            }, 500);
        });

        updateButtons();

        // Responsive update
        window.addEventListener('resize', () => {
            updateButtons();
        });
    });
}