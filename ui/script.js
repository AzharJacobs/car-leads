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

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  addMessage(text, "user");
  userInput.value = ""; // Clear input immediately

  // Add a loading indicator while waiting for the bot's response (Optional)
  const loadingMessage = addMessage("Typing...", "bot-loading"); // Use a valid class name

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: text })
    });

    // Remove the loading indicator
    loadingMessage.remove();

    if (!response.ok) {
      // Handle HTTP errors
      const errorData = await response.json();
      throw new Error(`HTTP error! status: ${response.status}, Details: ${errorData.error || response.statusText}`);
    }

    const data = await response.json();
    addMessage(data.reply, "bot");

  } catch (error) {
    // Remove the loading indicator if it still exists
     if(loadingMessage && loadingMessage.parentNode) {
         loadingMessage.remove();
     }
    console.error('Error sending message:', error);
    addMessage("Error: Could not get response from the bot.", "bot error"); // Display an error message
  }

  chatBox.scrollTop = chatBox.scrollHeight;
}

function addMessage(message, sender) {
  const msgDiv = document.createElement("div");
  // Split sender string by space to add multiple classes if needed, though for 'bot-loading' it's a single class
  const classes = sender.split(' ');
  msgDiv.classList.add("message", ...classes); // Use spread operator to add all classes
  // Handle potential HTML in message if needed, for now using innerText for safety
  msgDiv.innerText = message;
  chatBox.appendChild(msgDiv);
  // Autoscroll handled in sendMessage after receiving response
  return msgDiv; // Return the message element in case it's a loading message to be removed later
}

// Remove the fake bot reply function as we will now use the backend
// function generateFakeBotReply(text) {
//   if (text.toLowerCase().includes("lead")) {
//     return "You currently have 5 leads. Would you like to filter by date or car model?";
//   } else {
//     return "Thanks for your question. I'll get that information for you.";
//   }
// }
