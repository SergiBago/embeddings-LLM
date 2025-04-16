
document.getElementById("user-input").addEventListener("keypress", function (e) {
  if(e.key==="Enter"){
    sendQuery()
  }
});

document.getElementById("url-input").addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    processUrl();
  }
});

async function processUrl() {
  const url = document.getElementById("url-input").value.trim();
  const chatBox = document.getElementById("chat-box");

  if (!url) return;

  const agentMessage = document.createElement("div");
  agentMessage.className = "chat-message agent";
  agentMessage.innerHTML = 'Procesando la URL, por favor espera... <span class="spinner"></span>';
  chatBox.appendChild(agentMessage);

  try {
    const response = await fetch("http://localhost:5001/scrape", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: url })
    });

    const data = await response.json();

    if (response.ok) {
      agentMessage.innerHTML = "¡Contenido procesado correctamente! Ya puedes empezar a preguntar.";
      document.getElementById("chat-container").style.display = "block";
      document.getElementById("url-form").style.display = "none";
    } else {
      agentMessage.innerHTML = "Error al procesar la URL: " + data.error;
    }
  } catch (error) {
    agentMessage.innerHTML = "Error al conectar con el servidor.";
    console.error(error);
  }

  chatBox.scrollTop = chatBox.scrollHeight;
}


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
