from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# Load locally if offline
# tokenizer = GPT2Tokenizer.from_pretrained("./model")
# model = GPT2LMHeadModel.from_pretrained("./model")

# Online version
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

model.eval()

chat_history = []

def generate_response(user_input, max_length=100):
    chat_history.append(f"User: {user_input}")
    prompt = "\n".join(chat_history) + "\nBot:"
    inputs = tokenizer(prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            max_length=inputs.input_ids.shape[1] + max_length,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    bot_reply = response.split("Bot:")[-1].strip()
    chat_history.append(f"Bot: {bot_reply}")
    return bot_reply

# Demo loop
if __name__ == "__main__":
    print("🧠 GPT-2 Chatbot Ready (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        reply = generate_response(user_input)
        print("Bot:", reply)
