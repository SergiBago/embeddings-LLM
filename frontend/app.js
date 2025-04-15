document.getElementById("user-input").addEventListener("keypress", function (e) {
  if(e.key==="Enter"){
    sendQuery()
  }
});

document.getElementById("url-input").addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    const url = document.getElementById("url-input").value.trim();
    if (url) {
      processUrl(url);
    }
  }
});


async function processUrl(url) {
  console.log("Sending URL:", url);
  if (!url) {
    console.log("URL is empty or not provided");
    return;  // Stop if there's no URL
  }
  
  const chatBox = document.getElementById("chat-box");
  
  // Mostrar mensaje de carga
  const agentMessage = document.createElement("div");
  agentMessage.className = "chat-message agent";
  agentMessage.textContent = "Processing URL...";
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
    console.log("Response Data:", data);
    
    if (response.ok) {
      agentMessage.textContent = "URL processed successfully!";
    } else {
      agentMessage.textContent = "Error processing URL: " + data.error;
    }
  } catch (error) {
    agentMessage.textContent = "Error processing URL.";
    console.error(error);
  }

  // Scroll to bottom
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