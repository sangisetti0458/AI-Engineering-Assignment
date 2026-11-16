
const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChatBtn");


// ======================================
// 1. Display and format chat messages
// ======================================

function escapeHTML(text) {
    return String(text).replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}


function formatInlineMarkdown(text) {
    let safe = escapeHTML(text);

    // Inline code
    safe = safe.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Bold text
    safe = safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Italic text
    safe = safe.replace(/\*(.*?)\*/g, "<em>$1</em>");

    // Strikethrough
    safe = safe.replace(/~~(.*?)~~/g, "<del>$1</del>");

    return safe;
}


function renderMarkdown(message) {
    const lines = String(message).split("\n");

    let html = "";
    let inList = false;
    let listType = "";

    function closeList() {
        if (inList) {
            html += listType === "ul" ? "</ul>" : "</ol>";
            inList = false;
            listType = "";
        }
    }

    for (const line of lines) {
        const trimmed = line.trim();

        if (!trimmed) {
            closeList();
            continue;
        }

        // Headings: #, ##, ###
        const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);

        if (heading) {
            closeList();

            const level = heading[1].length;

            html += `<h${level}>${formatInlineMarkdown(heading[2])}</h${level}>`;
            continue;
        }

        // Bullet points
        const bullet = trimmed.match(/^[-*]\s+(.+)$/);

        if (bullet) {
            if (!inList || listType !== "ul") {
                closeList();

                html += "<ul>";

                inList = true;
                listType = "ul";
            }

            html += `<li>${formatInlineMarkdown(bullet[1])}</li>`;
            continue;
        }

        // Numbered lists
        const numbered = trimmed.match(/^\d+[.)]\s+(.+)$/);

        if (numbered) {
            if (!inList || listType !== "ol") {
                closeList();

                html += "<ol>";

                inList = true;
                listType = "ol";
            }

            html += `<li>${formatInlineMarkdown(numbered[1])}</li>`;
            continue;
        }

        closeList();

        // Horizontal divider
        if (/^---+$/.test(trimmed)) {
            html += "<hr>";
            continue;
        }

        // Normal paragraph
        html += `<p>${formatInlineMarkdown(trimmed)}</p>`;
    }

    closeList();

    return html;
}


function addMessage(message, sender) {
    const messageElement = document.createElement("div");

    messageElement.classList.add(
        "message",
        sender === "user" ? "user-message" : "assistant-message"
    );

    if (sender === "assistant") {
        messageElement.innerHTML = renderMarkdown(message);
    } else {
        messageElement.textContent = message;
    }

    chatMessages.appendChild(messageElement);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageElement;
}


// ======================================
// 2. Load hardware information
// ======================================

async function loadHardwareInfo() {
    try {
        const response = await fetch("/api/hardware");

        if (!response.ok) {
            throw new Error("Unable to load hardware information.");
        }

        const data = await response.json();

        const environment = data.environment;
        const hardware = data.hardware;

        // Environment badge
        document.getElementById("environmentBadge").textContent =
            environment.environment_type;

        // CPU
        const cpu = hardware.cpu;

        document.getElementById("cpuInfo").textContent =
            cpu.status === "success"
                ? `${cpu.cpu_model} (${cpu.physical_cores} cores)`
                : "Information unavailable";

        // Memory
        const memory = hardware.memory;

        document.getElementById("memoryInfo").textContent =
            memory.status === "success"
                ? `${memory.total_ram_gb} GB allocated (${memory.ram_usage_percent}% used)`
                : "Information unavailable";

        // Storage
        const storage = hardware.storage;

        if (storage.status === "success") {
            const devices = storage.block_devices || [];

            document.getElementById("storageInfo").textContent =
                devices.length > 0
                    ? `${devices.length} detected block devices`
                    : "No storage devices detected";
        } else {
            document.getElementById("storageInfo").textContent =
                "Information unavailable";
        }

        // GPU
        const gpu = hardware.gpu;

        document.getElementById("gpuInfo").textContent =
            gpu.status === "success" && gpu.gpus.length > 0
                ? gpu.gpus[0].split(": ").pop()
                : "No GPU information available";

        // WSL accuracy note
        const note = document.getElementById("hardwareNote");

        if (environment.is_wsl) {
            note.textContent =
                "WSL2 detected. RAM and storage readings describe the " +
                "virtualized Linux environment, not necessarily your " +
                "laptop's complete physical hardware.";
        } else {
            note.textContent =
                "Hardware readings are collected from the detected " +
                "Linux environment.";
        }

    } catch (error) {
        console.error("Hardware loading error:", error);

        document.getElementById("environmentBadge").textContent =
            "Environment unavailable";

        document.getElementById("hardwareNote").textContent =
            "Unable to retrieve hardware information. Check the backend.";
    }
}


// ======================================
// 3. Send question to Gemini
// ======================================

async function sendMessage(message) {
    if (!message.trim()) {
        return;
    }

    addMessage(message, "user");

    messageInput.value = "";

    sendBtn.disabled = true;
    sendBtn.textContent = "Thinking...";

    const loadingMessage = addMessage(
        "Checking your hardware and preparing an answer...",
        "assistant"
    );

    try {
        const response = await fetch("/api/chat", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Something went wrong."
            );
        }

        // Render Gemini response as formatted Markdown
        loadingMessage.innerHTML = renderMarkdown(data.answer);

        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {
        loadingMessage.textContent =
            "Error: " + error.message;

    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = "Send";

        messageInput.focus();
    }
}


// ======================================
// 4. Chat form submission
// ======================================

chatForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    await sendMessage(message);
});


// ======================================
// 5. Reset conversation
// ======================================

newChatBtn.addEventListener("click", async function() {
    try {
        const response = await fetch("/api/reset", {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Unable to reset conversation.");
        }

        chatMessages.innerHTML = "";

        addMessage(
            "Hello! I'm your Linux Hardware Assistant. What would you like to know?",
            "assistant"
        );

    } catch (error) {
        addMessage(
            "Unable to reset conversation: " + error.message,
            "assistant"
        );
    }
});


// ======================================
// 6. Initialize application
// ======================================

loadHardwareInfo();

messageInput.focus();
