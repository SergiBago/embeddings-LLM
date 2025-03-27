
document.getElementById("user-input").addEventListener("keypress", function (e) {
  if(e.key==="Enter"){
    sendQuery()
  }
});

async function sendQuery() {
  const inputEl = document.getElementById("user-input");
  const input = inputEl.value.trim();
  const chatBox = document.getElementById("chat-box");

  if (!input) return;

  // Add user message
  const userMessage = document.createElement("div");
  userMessage.className = "chat-message user";
  userMessage.textContent = `${input}`;
  chatBox.appendChild(userMessage);

  // Add agent placeholder
  const agentMessage = document.createElement("div");
  agentMessage.className = "chat-message agent";
  agentMessage.textContent = "Thinking...";
  chatBox.appendChild(agentMessage);

  // Scroll to bottom
  chatBox.scrollTop = chatBox.scrollHeight;

  inputEl.value = "";

  try {
    const url = `${window.location.origin}/query?query=${encodeURIComponent(input)}`;
    const response = await fetch(url);
    const data = await response.text();

    agentMessage.textContent = `${data}`;
  } catch (error) {
    agentMessage.textContent = "Error - Could not reach the server.";
    console.error(error);
  }

  // Scroll again in case message overflows
  chatBox.scrollTop = chatBox.scrollHeight;
}
