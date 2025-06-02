import os
from openai import OpenAI

# Load your OpenAI API key from an environment variable
# It is recommended to use a .env file and a library like python-dotenv for managing environment variables
# For example, you can add OPENAI_API_KEY='your-api-key' to a .env file in your project root
# and then use `pip install python-dotenv` and `from dotenv import load_dotenv; load_dotenv()`
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

system_prompt = """
You are CarGPT, a professional AI assistant built specifically for automotive businesses. Your job is to help staff access daily operational information such as customer call leads, appointment bookings, test drive schedules, sales inquiries, and other internal business data.

You respond clearly and efficiently, providing summaries or specific details when requested. If a user asks for "today's call leads," "test drive bookings," or "sales leads for this week," you return the relevant data in a clean, structured format.

If data is not available or the request is unclear, ask follow-up questions to clarify. If a request falls outside of your role (e.g., asking about unrelated topics), respond with:
"I'm here to assist with business operations and customer data for the dealership. Please ask something related to leads, bookings, or internal processes."

Your tone is professional, concise, and helpful. Format responses in easy-to-read bullet points or tables when appropriate.
"""

chat_history = []

def generate_response(user_input):
    chat_history.append({"role": "user", "content": user_input})

    messages = [
        {"role": "system", "content": system_prompt}
    ] + chat_history

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or another suitable OpenAI model
            messages=messages
        )
        bot_reply = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": bot_reply})
        return bot_reply
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, I am unable to process your request at the moment."

# Demo loop
if __name__ == "__main__":
    print("🚗 CarGPT Chatbot Ready (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        reply = generate_response(user_input)
        print("Bot:", reply)
