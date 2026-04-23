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
    chatBox.scrollTop = chatBox.scrollHeight;
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
    avatar.className = `message-avatar ${type === "user" ? "user-avatar" : "bot-avatar"}`;

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
    scrollToBottom();

    return bubble;
}

// =========================
// TYPING EFFECT
// =========================
async function typeText(element, text, speed = 15) {
    element.innerHTML = "";

    for (let i = 0; i < text.length; i++) {
        element.innerHTML += text[i];
        await new Promise(r => setTimeout(r, speed));
        scrollToBottom();
    }
}

// =========================
// BOT RESPONSE (typing)
// =========================
async function addBotResponse(text, docs, keyword) {

    text = renderMarkdown(text);
    text = highlight(text, keyword);

    const bubble = createMessage(`<p class="message-text"></p>`, "bot");
    const textEl = bubble.querySelector(".message-text");

    await typeText(textEl, text);

    // render documents
    if (docs && docs.length) {
        renderDocuments(docs);
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
function renderDocuments(docs) {

    let html = "<div class='chat-docs'>";

    docs.slice(0, 3).forEach(doc => {
        html += `
            <a class="chat-doc-item" href="/document/${doc.id}">
                <span class="doc-type">${doc.type || "Document"}</span>
                <span class="doc-title">${doc.title}</span>
                ${doc.year ? `<span class="doc-year">(${doc.year})</span>` : ""}
            </a>
        `;
    });

    html += "</div>";

    createMessage(html, "bot");
}

// =========================
// LOADING
// =========================
function addLoading() {
    const bubble = createMessage(
        `<p class="message-text">Đang suy nghĩ...</p>`,
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

        await addBotResponse(answer, docs, question);

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