// frontend/static/js/response.js

const sessionID = Math.random().toString(36).slice(2);

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

  // --- get board ---
  const boardStr = window.BoardUtils.getBoardString(
    document.getElementById("board")
  );

  const payload = { messages: messages, board: boardStr, puzzle_id: puzzle_id, session_id: sessionID };
  console.log("REQUEST PAYLOAD:", payload);

  // --- add placeholder AI bubble ---
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
    window.BoardUtils.highlightCell(data.r - 1, data.c - 1);  // convert to 0-based
  } catch (err) {
    console.error("ERROR:", err);
    updateThinkingBubble(thinkingBubble, "Error contacting server.");
  }
}

// adds the user message to the chat window
function addUserMessage(text) {
  const msg = document.createElement("div");
  msg.className = "chat-bubble user-bubble";
  msg.textContent = text;
  windowEl.appendChild(msg);
  windowEl.scrollTop = windowEl.scrollHeight;
}

// adds a "Thinking..." bubble to the chat window
function addThinkingBubble() {
  const msg = document.createElement("div");
  msg.className = "chat-bubble ai-bubble";
  msg.textContent = "Thinking...";
  windowEl.appendChild(msg);
  windowEl.scrollTop = windowEl.scrollHeight;
  return msg;  // return DOM element so we can update it later
}

// updates the thinking bubble with new text
function updateThinkingBubble(el, newText) {
  el.textContent = newText;
  windowEl.scrollTop = windowEl.scrollHeight;
}

// handles send button click or Enter key
sendBtn.addEventListener("click", handleResponse);
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    handleResponse();
  }
});

// hint button logic
document.getElementById("btn-hint").addEventListener("click", () => {
    const hintStr = "Give me a single cell hint for the current board.";
    console.log("Hint button clicked");

    inputEl.value = hintStr;
    handleResponse();
});

// clear button logic
document.getElementById("btn-clear").addEventListener("click", () => {
    console.log("Clear button clicked");
    window.BoardUtils.clearBoard();
});