const chatForm = document.getElementById("chatForm");
const chatBox = document.getElementById("chatBox");
const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");
const suggestionButtons = document.querySelectorAll(".chat-chip");

const conversationHistory = [];

// =========================
// UTILS
// =========================
function escapeHtml(text) {
    return String(text || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function scrollToBottom() {
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });
}

// =========================
// MARKDOWN
// =========================
function renderMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/`(.*?)`/g, "<code>$1</code>")
        .replace(/\[(.*?)\]\((https?:\/\/.*?)\)/g, '<a href="$2" target="_blank" class="chat-link">$1</a>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="chat-link">$1</a>');
}

// =========================
// HIGHLIGHT
// =========================
function highlight(text, keyword) {
    if (!keyword) return text;
    const regex = new RegExp(`(${keyword})`, "gi");
    return text.replace(regex, "<mark>$1</mark>");
}

// =========================
// MESSAGE
// =========================
function createMessage(content, type) {
    const wrapper = document.createElement("div");
    wrapper.className = `chat-message ${type}`;

    const avatar = document.createElement("div");
    if (type === "user") {
        avatar.className = "message-avatar user-avatar";
    } else {
        avatar.className = "message-avatar bot-avatar";
        avatar.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>`;
    }

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML = content;

    if (type === "user") {
        wrapper.appendChild(bubble);
        wrapper.appendChild(avatar);
    } else {
        wrapper.appendChild(avatar);
        wrapper.appendChild(bubble);
    }

    chatBox.appendChild(wrapper);
    
    // small delay to ensure DOM is updated and animation runs
    setTimeout(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 10);

    return bubble;
}

// =========================
// TYPING EFFECT
// =========================
async function typeText(element, rawText, speed = 15) {
    element.textContent = "";

    for (let i = 0; i < rawText.length; i++) {
        // Dùng textContent để tránh partial HTML tags xuất hiện
        element.textContent = rawText.slice(0, i + 1);
        await new Promise(r => setTimeout(r, speed));
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Khi typing xong, render toàn bộ Markdown thành HTML một lần
    element.innerHTML = renderMarkdown(rawText);
}

// =========================
// BOT RESPONSE (typing)
// =========================
async function addBotResponse(text, docs, keyword, intent, relatedSubjects = [], mainSubject = null, graphData = null) {

    // Không pre-render ở đây nữa, typeText sẽ tự xử lý
    const bubble = createMessage(`<p class="message-text"></p>`, "bot");
    const textEl = bubble.querySelector(".message-text");

    await typeText(textEl, text);

    // render documents
    if (docs && docs.length) {
        renderDocuments(docs, intent);
    }

    // render related subjects recommendation chips
    if (relatedSubjects && relatedSubjects.length) {
        renderRelatedSubjects(relatedSubjects, mainSubject);
    }

    // render graph
    if (graphData && graphData.nodes && graphData.nodes.length > 0) {
        renderGraph(graphData);
    }
}
// =========================
// GRAPH RENDER
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

let graphCounter = 0;

function renderGraph(graphData) {
    graphCounter++;
    const graphId = `chat-graph-${graphCounter}`;
    
    const html = `
        <div class="chat-graph-wrapper" style="margin-top: 10px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; background: #fff; position: relative;">
            <div class="graph-header" style="padding: 8px 12px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; font-size: 12px; font-weight: 600; color: #475569; display: flex; justify-content: space-between; align-items: center;">
                <span>Biểu đồ liên kết</span>
                <div>
                    <button onclick="const el = document.getElementById('legend-${graphId}'); el.style.display = el.style.display === 'none' ? 'block' : 'none';" style="background:none;border:none;cursor:pointer;color:#64748b; margin-right: 8px;" title="Chú thích">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg> Chú thích
                    </button>
                    <button onclick="document.getElementById('${graphId}').requestFullscreen()" style="background:none;border:none;cursor:pointer;color:#64748b;" title="Phóng to">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path></svg>
                    </button>
                </div>
            </div>
            
            <div id="legend-${graphId}" style="display: none; position: absolute; top: 40px; right: 10px; background: rgba(255, 255, 255, 0.95); border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; font-size: 11px; z-index: 10; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-height: 250px; overflow-y: auto; color: #333;">
                <div style="font-weight: bold; margin-bottom: 8px; color: #0f172a;">Tài liệu</div>
                <div style="display:flex; align-items:center; margin-bottom:6px;"><span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#2563eb; margin-right:8px; border: 1px solid #1e40af;"></span> Sách</div>
                <div style="display:flex; align-items:center; margin-bottom:6px;"><span style="display:inline-block; width:12px; height:12px; background:#10b981; margin-right:8px; border: 1px solid #059669;"></span> Bài báo</div>
                <div style="display:flex; align-items:center; margin-bottom:6px;"><span style="display:inline-block; width:0; height:0; border-left:6px solid transparent; border-right:6px solid transparent; border-bottom:12px solid #8b5cf6; margin-right:8px;"></span> Luận văn</div>
                <hr style="margin: 8px 0; border: none; border-top: 1px solid #e2e8f0;">
                <div style="font-weight: bold; margin-bottom: 8px; color: #0f172a;">Thực thể</div>
                <div style="display:flex; align-items:center; margin-bottom:6px;"><span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#fbbf24; margin-right:8px; border: 1px solid #d97706;"></span> Tác giả</div>
                <div style="display:flex; align-items:center; margin-bottom:6px;"><span style="display:inline-block; width:10px; height:10px; background:#f97316; transform: rotate(45deg); margin-right:9px; margin-left: 1px; border: 1px solid #ea580c;"></span> <span style="margin-left: 0px;">Chủ đề</span></div>
                <div style="display:flex; align-items:center; margin-bottom:6px;"><span style="display:inline-block; width:12px; height:12px; background:#ec4899; clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%); margin-right:8px;"></span> Từ khóa</div>
                <div style="display:flex; align-items:center; margin-bottom:6px;"><span style="display:inline-block; width:0; height:0; border-left:6px solid transparent; border-right:6px solid transparent; border-top:12px solid #06b6d4; margin-right:8px;"></span> Nhà xuất bản</div>
                <div style="display:flex; align-items:center; margin-bottom:6px;"><span style="display:inline-block; width:12px; height:12px; background:#6366f1; clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%); margin-right:8px;"></span> Trường đại học</div>
                <div style="display:flex; align-items:center; margin-bottom:6px;"><span style="display:inline-block; width:12px; height:12px; background:#14b8a6; margin-right:8px; border: 1px solid #0d9488;"></span> Danh mục</div>
                <div style="display:flex; align-items:center; margin-bottom:6px;"><span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#64748b; margin-right:8px; border: 1px solid #475569;"></span> Ngôn ngữ</div>
            </div>
            
            <div id="${graphId}" style="width: 100%; height: 300px; background: #fafafa;"></div>
        </div>
    `;
    
    createMessage(html, "bot");
    
    setTimeout(() => {
        const container = document.getElementById(graphId);
        if (!container || !window.vis) return;
        
        const mappedNodes = graphData.nodes.map(n => {
            return {
                ...n,
                label: formatLabel(n.label)
            };
        });

        const data = {
            nodes: new vis.DataSet(mappedNodes),
            edges: new vis.DataSet(graphData.edges)
        };

        const options = {
            nodes: {
                shape: "dot",
                size: 15,
                font: { size: 11, color: "#333", vadjust: 20 },
                borderWidth: 2,
                shadow: { enabled: true, color: "rgba(0,0,0,0.1)", size: 5, x: 2, y: 2 }
            },
            edges: {
                width: 1,
                color: { color: "#cbd5e1", hover: "#64748b", highlight: "#2563eb" },
                smooth: { type: "continuous" },
                arrows: { to: { enabled: false } }
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
                category: { shape: "box", color: { background: "#14b8a6", border: "#0d9488" } },
                language: { shape: "ellipse", color: { background: "#64748b", border: "#475569" } }
            },
            physics: {
                enabled: true,
                solver: "forceAtlas2Based",
                forceAtlas2Based: { gravitationalConstant: -100, springLength: 150 },
                stabilization: { iterations: 100 }
            },
            interaction: { hover: true, zoomView: true, dragNodes: true }
        };

        const network = new vis.Network(container, data, options);
        
        network.once("stabilized", function () {
            network.fit({ animation: true });
            scrollToBottom();
        });
        
        network.on("doubleClick", (params) => {
            if (!params.nodes.length) return;
            const node = data.nodes.get(params.nodes[0]);
            if (!node) return;
            
            if (["book", "article", "thesis"].includes(node.group)) {
                window.open(`/document/${node.id}`, '_blank');
            } else {
                window.open(`/explore/${node.group}/${node.id}`, '_blank');
            }
        });

    }, 100);
}


// =========================
// RELATED SUBJECTS CHIPS
// =========================
function renderRelatedSubjects(subjects, mainSubject) {
    if (!subjects || !subjects.length) return;

    let html = `
        <div class="chat-related-subjects">
            <div class="related-subjects-title">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sparkle-icon"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                Chủ đề liên quan từ Đồ thị tri thức (${escapeHtml(mainSubject)}):
            </div>
            <div class="related-subjects-chips">
    `;

    subjects.forEach(subj => {
        html += `<button type="button" class="related-subject-chip" onclick="submitChipQuestion('${escapeHtml(subj)}')">${escapeHtml(subj)}</button>`;
    });

    html += `
            </div>
        </div>
    `;

    createMessage(html, "bot");
}

window.submitChipQuestion = function(text) {
    questionInput.value = `tài liệu về ${text}`;
    sendQuestion();
};

// =========================
// USER MESSAGE
// =========================
function addUserMessage(text) {
    createMessage(`<p class="message-text">${escapeHtml(text)}</p>`, "user");
}

// =========================
// DOCUMENT LIST
// =========================
function renderDocuments(docs, intent) {

    let html = `<div class='chat-docs'>`;

    docs.slice(0, 5).forEach(doc => {
        const titleHtml = doc.title_highlighted || escapeHtml(doc.title);
        const authors = doc.authors && doc.authors.length
            ? `<span class="doc-authors">${doc.authors.slice(0, 2).join(", ")}</span>`
            : "";
        
        const link = doc.url || `/document/${doc.id}`;
        const target = doc.url ? 'target="_blank"' : '';
        const sourceLabel = doc.url ? '<span class="doc-source-tag">External</span>' : '';

        html += `
            <a class="chat-doc-item" href="${link}" ${target}>
                <span class="doc-type">${doc.type || "Document"} ${sourceLabel}</span>
                <span class="doc-title">${titleHtml}</span>
                ${doc.year ? `<span class="doc-year">(${doc.year})</span>` : ""}
                ${authors}
            </a>
        `;
    });

    html += `</div>`;

    createMessage(html, "bot");
}

// =========================
// LOADING
// =========================
function addLoading() {
    const bubble = createMessage(
        `<div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>`,
        "bot"
    );
    bubble.id = "loading-msg";
}

function removeLoading() {
    const loading = document.getElementById("loading-msg");
    if (loading) loading.parentElement.remove();
}

// =========================
// HISTORY
// =========================
function pushHistory(role, content) {
    conversationHistory.push({ role, content });

    if (conversationHistory.length > 10) {
        conversationHistory.shift();
    }
}

// =========================
// SEND
// =========================
async function sendQuestion() {

    const question = questionInput.value.trim();
    if (!question) return;

    addUserMessage(question);
    pushHistory("user", question);

    questionInput.value = "";
    questionInput.style.height = "auto";

    addLoading();
    sendButton.disabled = true;

    try {
        const res = await fetch("/qa/api", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                history: conversationHistory
            })
        });

        const data = await res.json();

        removeLoading();

        const answer = data.answer || "Không có câu trả lời.";
        const docs = data.documents || [];
        const intent = data.intent || "search";
        const relatedSubjects = data.related_subjects || [];
        const mainSubject = data.main_subject;
        const graphData = data.graph_data;

        await addBotResponse(answer, docs, question, intent, relatedSubjects, mainSubject, graphData);

        pushHistory("assistant", answer);

    } catch (err) {
        removeLoading();
        createMessage("Có lỗi xảy ra 😢", "bot");
    }

    sendButton.disabled = false;
    questionInput.focus();
}

// =========================
// EVENTS
// =========================
chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendQuestion();
});

questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendQuestion();
    }
});

questionInput.addEventListener("input", () => {
    questionInput.style.height = "auto";
    questionInput.style.height = Math.min(questionInput.scrollHeight, 180) + "px";
});

// suggestion
suggestionButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        questionInput.value = btn.textContent.trim();
        questionInput.focus();
    });
});