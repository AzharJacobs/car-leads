import os
import json
from datetime import datetime, date
from openai import OpenAI

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# System prompt defines CarGPT's role and behavior
system_prompt = """
You are CarGPT, a professional AI assistant built specifically for automotive businesses. Your job is to help staff access daily operational information such as customer call leads, appointment bookings, test drive schedules, sales inquiries, and other internal business data.

You are contextually aware and can understand when users are asking about leads in general or specific types. When someone asks "how many leads came in today" or "show me today's leads", provide ALL leads unless they specifically ask for a particular type.

Key behaviors:
- When asked for "leads" without specification, show ALL leads
- Be conversational and maintain context from previous messages
- If someone asks for "today's leads", filter by today's date
- Format responses clearly with summaries and details
- If data is not available, explain what data you do have access to
- Only ask for clarification when the request is genuinely ambiguous

Your tone is professional, helpful, and efficient. Always provide actionable information.
"""

def load_leads_data(filepath="leads.json"):
    """
    Load leads data from a JSON file, trying multiple common paths.
    Returns an empty list if file not found or error occurs.
    """
    try:
        possible_paths = [
            filepath,
            os.path.join(os.path.dirname(__file__), filepath),
            os.path.join(os.path.dirname(__file__), "..", filepath),
            os.path.join("data", filepath),
            os.path.join("..", "data", filepath),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    leads_data = json.load(f)
                print(f"✓ Loaded {len(leads_data)} leads from {path}")
                return leads_data

        print(f"⚠️ Could not find {filepath} in any expected location.")
        return []

    except Exception as e:
        print(f"Error loading leads data: {e}")
        return []

# Load leads at start
leads_data = load_leads_data()
chat_history = []

# Conversation context tracks current query focus
conversation_context = {
    "current_topic": None,
    "lead_type_focus": None,
    "date_filter": None,
    "last_query_type": None
}

def get_today_leads():
    """Return leads from today's date."""
    today_str = str(date.today())
    return [lead for lead in leads_data if lead.get("timestamp", "").startswith(today_str)]

def get_leads_by_source(source_name):
    """Return leads filtered by lead source."""
    source_name_lower = source_name.lower()
    return [lead for lead in leads_data if lead.get("lead_source", "").lower() == source_name_lower]

def get_leads_by_car_interest(brand):
    """Return leads interested in a specific car brand."""
    brand_lower = brand.lower()
    return [
        lead for lead in leads_data
        if brand_lower in lead.get("car_interest", "").lower()
    ]

def get_leads_summary():
    """
    Returns an aggregated summary of leads:
    - Total leads count
    - Today's leads count
    - Breakdown by lead source
    - Breakdown by car brand
    """
    total = len(leads_data)
    today_leads = get_today_leads()

    source_counts = {}
    brand_counts = {}

    for lead in leads_data:
        # Count source
        source = lead.get("lead_source", "Unknown")
        source_counts[source] = source_counts.get(source, 0) + 1

        # Count brand from first word in car_interest if available
        car_interest = lead.get("car_interest", "").strip()
        if car_interest:
            brand = car_interest.split()[0]
            brand_counts[brand] = brand_counts.get(brand, 0) + 1

    return {
        "total_leads": total,
        "today_leads": len(today_leads),
        "source_breakdown": source_counts,
        "brand_breakdown": brand_counts,
        "today_leads_data": today_leads,
    }

def analyze_user_intent(user_input):
    """
    Analyze the user input to update conversation context.
    Detects date filters, lead type focus (brand/source), and query type (count/list/general).
    """
    user_lower = user_input.lower()

    # Reset context on new input
    conversation_context["date_filter"] = None
    conversation_context["lead_type_focus"] = None
    conversation_context["current_topic"] = None
    conversation_context["last_query_type"] = None

    # Date-related keywords
    if any(word in user_lower for word in ["today", "today's", "this morning", "this afternoon"]):
        conversation_context["date_filter"] = "today"

    # Car brands list - can be expanded
    car_brands = [
        "bmw", "toyota", "honda", "ford", "nissan", "mercedes",
        "volkswagen", "hyundai", "kia", "mazda", "chevrolet", "tesla"
    ]
    for brand in car_brands:
        if brand in user_lower:
            conversation_context["lead_type_focus"] = f"car_{brand}"
            break

    # Lead source detection
    if any(word in user_lower for word in ["phone", "call"]):
        conversation_context["lead_type_focus"] = "phone_call"
    elif any(word in user_lower for word in ["web", "form", "online"]):
        conversation_context["lead_type_focus"] = "web_form"
    elif any(word in user_lower for word in ["walk", "walk-in", "walkin"]):
        conversation_context["lead_type_focus"] = "walk-in"
    elif "email" in user_lower:
        conversation_context["lead_type_focus"] = "email"
    elif any(word in user_lower for word in ["test drive", "testdrive"]):
        conversation_context["lead_type_focus"] = "test_drive"
    elif any(word in user_lower for word in ["social", "media"]):
        conversation_context["lead_type_focus"] = "social_media"

    # General lead query detection
    if any(word in user_lower for word in ["leads", "lead"]) and not conversation_context["lead_type_focus"]:
        conversation_context["current_topic"] = "all_leads"

    # Query type detection
    if any(word in user_lower for word in ["how many", "count", "number of"]):
        conversation_context["last_query_type"] = "count"
    elif any(word in user_lower for word in ["show", "list", "see", "give me", "what are"]):
        conversation_context["last_query_type"] = "list"
    else:
        conversation_context["last_query_type"] = "general"

def prepare_context_data(user_input):
    """
    Prepare and format relevant lead data based on analyzed context.
    Returns a formatted string to append to user input for better AI response.
    """
    analyze_user_intent(user_input)
    context_info = ""

    # If filter for today's leads
    if conversation_context["date_filter"] == "today" or "today" in user_input.lower():
        today_leads = get_today_leads()
        if today_leads:
            context_info += f"\n\n📊 TODAY'S LEADS ({len(today_leads)}):\n"
            for i, lead in enumerate(today_leads, 1):
                context_info += (
                    f"\n{i}. {lead.get('name', 'Unknown')} - {lead.get('lead_source', 'Unknown')}\n"
                    f"   • Interested in: {lead.get('car_interest', 'Not specified')}\n"
                    f"   • Budget: {lead.get('budget', 'Not specified')}\n"
                    f"   • Phone: {lead.get('phone', 'N/A')}\n"
                    f"   • Email: {lead.get('email', 'N/A')}"
                )
                if lead.get('test_drive_date'):
                    context_info += f"\n   • Test Drive Date: {lead.get('test_drive_date')}"
        else:
            context_info += "\n\n📊 No leads found for today."

    # Filter for specific car brand leads
    elif conversation_context["lead_type_focus"] and conversation_context["lead_type_focus"].startswith("car_"):
        brand = conversation_context["lead_type_focus"].replace("car_", "")
        brand_leads = get_leads_by_car_interest(brand)
        if brand_leads:
            context_info += f"\n\n📊 {brand.upper()} LEADS ({len(brand_leads)}):\n"
            for i, lead in enumerate(brand_leads, 1):
                context_info += (
                    f"\n{i}. {lead.get('name', 'Unknown')} - {lead.get('lead_source', 'Unknown')}\n"
                    f"   • Car: {lead.get('car_interest', 'Not specified')}\n"
                    f"   • Budget: {lead.get('budget', 'Not specified')}\n"
                    f"   • Phone: {lead.get('phone', 'N/A')}\n"
                    f"   • Email: {lead.get('email', 'N/A')}"
                )
                if lead.get('test_drive_date'):
                    context_info += f"\n   • Test Drive Date: {lead.get('test_drive_date')}"
        else:
            context_info += f"\n\n📊 No {brand.upper()} leads found."

    # Filter for lead source
    elif conversation_context["lead_type_focus"] and not conversation_context["lead_type_focus"].startswith("car_"):
        source_map = {
            "phone_call": "Phone Call",
            "web_form": "Web Form",
            "walk-in": "Walk-in",
            "email": "Email",
            "test_drive": "Test Drive",
            "social_media": "Social Media"
        }
        source = source_map.get(conversation_context["lead_type_focus"], conversation_context["lead_type_focus"])
        source_leads = get_leads_by_source(source)
        if source_leads:
            context_info += f"\n\n📊 {source.upper()} LEADS ({len(source_leads)}):\n"
            for i, lead in enumerate(source_leads, 1):
                context_info += (
                    f"\n{i}. {lead.get('name', 'Unknown')}\n"
                    f"   • Car: {lead.get('car_interest', 'Not specified')}\n"
                    f"   • Budget: {lead.get('budget', 'Not specified')}\n"
                    f"   • Phone: {lead.get('phone', 'N/A')}\n"
                    f"   • Email: {lead.get('email', 'N/A')}"
                )
                if lead.get('test_drive_date'):
                    context_info += f"\n   • Test Drive Date: {lead.get('test_drive_date')}"
        else:
            context_info += f"\n\n📊 No {source} leads found."

    # General leads summary
    elif conversation_context["current_topic"] == "all_leads":
        summary = get_leads_summary()
        context_info += (
            f"\n\n📊 LEADS SUMMARY:\n"
            f"• Total leads: {summary['total_leads']}\n"
            f"• Today's leads: {summary['today_leads']}\n\n"
            "Breakdown by lead source:\n"
        )
        for source, count in summary['source_breakdown'].items():
            context_info += f"• {source}: {count}\n"

        context_info += "\nBreakdown by car brand:\n"
        for brand, count in summary['brand_breakdown'].items():
            context_info += f"• {brand}: {count}\n"

        if summary['today_leads_data']:
            context_info += "\n📝 Details of Today's Leads:\n"
            for i, lead in enumerate(summary['today_leads_data'], 1):
                context_info += (
                    f"\n{i}. {lead.get('name', 'Unknown')} ({lead.get('lead_source', 'Unknown')})\n"
                    f"   • Car: {lead.get('car_interest', 'Not specified')}\n"
                    f"   • Budget: {lead.get('budget', 'Not specified')}"
                )

    return context_info

def generate_response(user_input):
    """
    Generate AI response based on user input combined with contextual leads data.
    """

    # Prepare enriched prompt with leads data context
    enriched_user_input = user_input + prepare_context_data(user_input)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": enriched_user_input}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=600,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    # Extract text response
    answer = response.choices[0].message.content.strip()

    # Optionally store conversation history for context (not yet used)
    chat_history.append({"user": user_input, "assistant": answer})

    return answer

# Example usage:
if __name__ == "__main__":
    print("CarGPT Assistant started. Type your query or 'exit' to quit.")
    while True:
        user_msg = input("\nYou: ")
        if user_msg.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        answer = generate_response(user_msg)
        print(f"CarGPT: {answer}")
