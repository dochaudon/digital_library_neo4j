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
        .replace(/`(.*?)`/g, "<code>$1</code>");
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
async function addBotResponse(text, docs, keyword, intent) {

    // Không pre-render ở đây nữa, typeText sẽ tự xử lý
    const bubble = createMessage(`<p class="message-text"></p>`, "bot");
    const textEl = bubble.querySelector(".message-text");

    await typeText(textEl, text);

    // render documents
    if (docs && docs.length) {
        renderDocuments(docs, intent);
    }
}

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
        html += `
            <a class="chat-doc-item" href="/document/${doc.id}">
                <span class="doc-type">${doc.type || "Document"}</span>
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

        await addBotResponse(answer, docs, question, intent);

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