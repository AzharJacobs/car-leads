const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");
const chatBox = document.getElementById("chatBox");

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keydown", function (e) {
  if (e.key === "Enter") sendMessage();
});

function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  // Add user message
  addMessage(text, "user");

  // Fake bot response (for now)
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
  // This is just placeholder logic
  if (text.toLowerCase().includes("lead")) {
    return "You currently have 5 leads. Would you like to filter by date or car model?";
  } else {
    return "Thanks for your question. I’ll get that information for you.";
  }
}
