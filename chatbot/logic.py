import os
import json
from openai import OpenAI

# Load your OpenAI API key from an environment variable
# It is recommended to use a .env file and a library like python-dotenv for managing environment variables
# For example, you can add OPENAI_API_KEY='your-api-key' to a .env file in your project root
# and then use `pip install python-dotenv` and `from dotenv import load_dotenv; load_dotenv()`
# from dotenv import load_dotenv
# load_dotenv() # Add this line to load variables from a .env file

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

# Load leads data from leads.json
def load_leads_data(filepath="leads.json"):
    try:
        # Construct the absolute path to leads.json assuming it's in the workspace root
        # You might need to adjust this path based on where the script is run from
        # If running from chatbot/, the path should be ../leads.json
        # Let's assume the script is run from the workspace root for now.
        # If you run it from the chatbot directory, change filepath to "../leads.json"
        absolute_filepath = os.path.join(os.path.dirname(__file__), "..", filepath)
        with open(absolute_filepath, 'r') as f:
            leads_data = json.load(f)
        print(f"Successfully loaded {len(leads_data)} leads from {filepath}")
        return leads_data
    except FileNotFoundError:
        print(f"Error: {filepath} not found. Make sure leads.json is in the workspace root.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred loading leads: {e}")
        return []

leads_data = load_leads_data()

chat_history = []

def generate_response(user_input):
    # Check if the user query is related to leads
    lead_keywords = ["leads", "call leads", "sales leads", "bookings", "customers", "data"]
    is_lead_query = any(keyword in user_input.lower() for keyword in lead_keywords)

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Include leads data in the message if it's a lead-related query and data is available
    if is_lead_query and leads_data:
        # Convert leads_data to a string format that can be included in the message
        # A simple JSON string representation might work, but can be verbose.
        # For better results, you might need to format it more human-readable.
        leads_context = f"\n\nAvailable leads data:\n{json.dumps(leads_data, indent=2)}"
        user_message_content = f"{user_input}{leads_context}"
        messages.append({"role": "user", "content": user_message_content})
        # Append the original user input to chat_history for continuity, but the API gets the enhanced message
        chat_history.append({"role": "user", "content": user_input})
    else:
        messages.append({"role": "user", "content": user_input})
        chat_history.append({"role": "user", "content": user_input})

    # Include previous chat history
    # Note: When including leads_data, the current user message might be quite long.
    # You might need to manage history length to avoid exceeding token limits.
    # We'll append the chat history *after* the initial system and potentially enhanced user message
    messages.extend(chat_history)

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
        # Consider adding more specific error handling for API errors (e.g., authentication, rate limits, token limits)
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
