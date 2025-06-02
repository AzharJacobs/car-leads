const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");
const chatBox = document.getElementById("chatBox");
const chatForm = document.getElementById("chatForm");

// Prevent default form submit (page reload)
chatForm.addEventListener("submit", function (e) {
  e.preventDefault();
  sendMessage();
});

// Optionally keep this if you want button click support
sendBtn.addEventListener("click", sendMessage);

function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  addMessage(text, "user");

  setTimeout(() => {
    const botResponse = generateFakeBotReply(text);
    addMessage(botResponse, "bot");
  }, 600);

  userInput.value = "";
}

function addMessage(message, sender) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);
  msgDiv.innerText = message;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function generateFakeBotReply(text) {
  if (text.toLowerCase().includes("lead")) {
    return "You currently have 5 leads. Would you like to filter by date or car model?";
  } else {
    return "Thanks for your question. I’ll get that information for you.";
  }
}
