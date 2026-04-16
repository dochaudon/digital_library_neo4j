const chatForm = document.getElementById("chatForm");
const chatBox = document.getElementById("chatBox");
const questionInput = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");
const suggestionButtons = document.querySelectorAll(".chat-chip");

const conversationHistory = [];

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function scrollChatToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addMessage(content, type) {
    const wrapper = document.createElement("div");
    wrapper.className = `chat-message ${type}`;

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML = content;

    wrapper.appendChild(bubble);
    chatBox.appendChild(wrapper);
    scrollChatToBottom();
}

function buildCitationHtml(citations) {
    if (!citations || citations.length === 0) {
        return "";
    }

    const items = citations.map((citation) => {
        const label = escapeHtml(citation.label || "Nguon");
        const title = escapeHtml(citation.title || "");
        const detail = escapeHtml(citation.detail || "");
        const url = citation.url ? escapeHtml(citation.url) : "";

        if (url) {
            return `
                <li class="citation-item">
                    <a href="${url}" class="citation-link">
                        <span class="citation-label">${label}</span>
                        <span class="citation-title">${title}</span>
                    </a>
                    ${detail ? `<span class="citation-detail">${detail}</span>` : ""}
                </li>
            `;
        }

        return `
            <li class="citation-item">
                <span class="citation-label">${label}</span>
                <span class="citation-title">${title}</span>
                ${detail ? `<span class="citation-detail">${detail}</span>` : ""}
            </li>
        `;
    }).join("");

    return `
        <div class="message-citations">
            <p class="citation-heading">Nguon du lieu</p>
            <ul class="citation-list">${items}</ul>
        </div>
    `;
}

function addUserMessage(text) {
    addMessage(`<p class="message-text">${escapeHtml(text)}</p>`, "user");
}

function addBotMessage(text) {
    addMessage(`<p class="message-text">${escapeHtml(text)}</p>`, "bot");
}

function addBotResponse(text, citations) {
    const citationHtml = buildCitationHtml(citations);
    addMessage(
        `<p class="message-text">${escapeHtml(text)}</p>${citationHtml}`,
        "bot"
    );
}

function addTypingMessage() {
    const wrapper = document.createElement("div");
    wrapper.className = "chat-message bot";
    wrapper.id = "typing-message";
    wrapper.innerHTML = `
        <div class="message-bubble">
            <p class="message-text">Dang phan tich cau hoi...</p>
        </div>
    `;
    chatBox.appendChild(wrapper);
    scrollChatToBottom();
}

function removeTypingMessage() {
    const typing = document.getElementById("typing-message");
    if (typing) {
        typing.remove();
    }
}

function getDocumentUrl(doc) {
    if (doc.url) {
        return doc.url;
    }

    const type = String(doc.type || "").toLowerCase();
    return `/${encodeURIComponent(type)}/${encodeURIComponent(doc.id)}`;
}

function getTypeLabel(type) {
    if (type === "Book") return "Sach";
    if (type === "Article") return "Bai bao";
    if (type === "Thesis") return "Luan van";
    return "Tai lieu";
}

function renderDocuments(docs) {
    if (!docs || docs.length === 0) {
        return;
    }

    let html = "<div class='chat-docs'>";

    docs.forEach((doc) => {
        const meta = doc.year ? ` <span class="doc-year">(${escapeHtml(doc.year)})</span>` : "";

        html += `
            <a class="chat-doc-item" href="${escapeHtml(getDocumentUrl(doc))}">
                <span class="doc-type">${escapeHtml(getTypeLabel(doc.type))}</span>
                <span class="doc-title">${escapeHtml(doc.title || "Khong co tieu de")}</span>${meta}
            </a>
        `;
    });

    html += "</div>";
    addMessage(html, "bot");
}

function setLoadingState(isLoading) {
    sendButton.disabled = isLoading;
    sendButton.textContent = isLoading ? "Dang gui..." : "Gửi";
}

function pushHistory(role, content, documents = []) {
    conversationHistory.push({ role, content, documents });

    if (conversationHistory.length > 8) {
        conversationHistory.splice(0, conversationHistory.length - 8);
    }
}

async function sendQuestion() {
    const q = questionInput.value.trim();
    if (!q) {
        questionInput.focus();
        return;
    }

    addUserMessage(q);
    pushHistory("user", q, []);

    questionInput.value = "";
    questionInput.style.height = "auto";
    setLoadingState(true);
    addTypingMessage();

    try {
        const response = await fetch("/api/qa", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: q,
                history: conversationHistory
            })
        });

        const data = await response.json();
        removeTypingMessage();

        const answer = data.answer || "Khong co cau tra loi.";
        const documents = data.documents || [];
        const citations = data.citations || [];

        addBotResponse(answer, citations);
        renderDocuments(documents);
        pushHistory("assistant", answer, documents);
    } catch (error) {
        removeTypingMessage();
        const message = "Da xay ra loi khi truy van du lieu. Vui long thu lai.";
        addBotMessage(message);
        pushHistory("assistant", message, []);
    } finally {
        setLoadingState(false);
        questionInput.focus();
    }
}

chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    sendQuestion();
});

questionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendQuestion();
    }
});

questionInput.addEventListener("input", () => {
    questionInput.style.height = "auto";
    questionInput.style.height = `${Math.min(questionInput.scrollHeight, 180)}px`;
});

suggestionButtons.forEach((button) => {
    button.addEventListener("click", () => {
        questionInput.value = button.textContent.trim();
        questionInput.focus();
    });
});

scrollChatToBottom();
