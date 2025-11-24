// frontend/static/js/response.js


const inputEl = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const windowEl = document.getElementById("response-window");
let messages = [];

// MAIN SEND HANDLER
async function handleResponse() {
  const userText = inputEl.value.trim();
  if (!userText) return;

  addUserMessage(userText);
  inputEl.value = "";

  messages.push({ role: "user", content: userText });

  // --- Get board ---
  const boardStr = window.BoardUtils.getBoardString(
    document.getElementById("board")
  );

  const payload = { messages, board: boardStr };
  console.log("REQUEST PAYLOAD:", payload);

  // --- Add placeholder AI bubble ---
  const thinkingBubble = addThinkingBubble();

  try {
    const res = await fetch("/ai/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    console.log("SERVER RESPONSE:", data);

    const reply = data.reply || "(no reply)";
    messages.push({ role: "assistant", content: reply });

    updateThinkingBubble(thinkingBubble, reply);
  } catch (err) {
    console.error("ERROR:", err);
    updateThinkingBubble(thinkingBubble, "Error contacting server.");
  }
}

function addUserMessage(text) {
  const msg = document.createElement("div");
  msg.className = "chat-bubble user-bubble";
  msg.textContent = text;
  windowEl.appendChild(msg);
  windowEl.scrollTop = windowEl.scrollHeight;
}

function addThinkingBubble() {
  const msg = document.createElement("div");
  msg.className = "chat-bubble ai-bubble";
  msg.textContent = "Thinking...";
  windowEl.appendChild(msg);
  windowEl.scrollTop = windowEl.scrollHeight;
  return msg;  // return DOM element so we can update it later
}

function updateThinkingBubble(el, newText) {
  el.textContent = newText;
  windowEl.scrollTop = windowEl.scrollHeight;
}

// click + Enter
sendBtn.addEventListener("click", handleResponse);
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    handleResponse();
  }
});

// buttons
document.getElementById("btn-hint").addEventListener("click", () => {
    const hintStr = "Give me a single cell hint for the current board.";
    console.log("Hint button clicked");

    inputEl.value = hintStr;
    handleResponse();
});

document.getElementById("btn-clear").addEventListener("click", () => {
    console.log("Clear button clicked");
    clearBoard();
});