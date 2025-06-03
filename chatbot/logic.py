import os
import json
from datetime import datetime, date
from openai import OpenAI

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Updated system prompt with better formatting instructions
system_prompt = """
You are CarGPT, a professional AI assistant built specifically for automotive businesses. Your job is to help staff access daily operational information such as customer call leads, appointment bookings, test drive schedules, sales inquiries, and other internal business data.

You now have access to TWO types of data:
1. LEADS DATA - Customer leads from various sources (phone, web, walk-in, etc.)
2. INQUIRIES DATA - Separate inquiry records with different structure and purpose

You are contextually aware and can understand when users are asking about leads vs inquiries. When someone asks about "leads", provide lead data. When they ask about "inquiries", provide inquiry data. If they ask about both or are unclear, clarify what they're looking for.

FORMATTING GUIDELINES:
- Use clear section headers with proper spacing
- Use consistent bullet points (either • or -) throughout
- Add blank lines between sections for readability
- Use numbers for ordered lists when appropriate
- Keep text aligned and well-structured
- Use simple, clean formatting without mixing styles
- Add summary totals at the top when showing breakdowns

Key behaviors:
- Distinguish between "leads" and "inquiries" requests
- When asked for "leads" without specification, show ALL leads
- When asked for "inquiries" without specification, show ALL inquiries
- Be conversational and maintain context from previous messages
- If someone asks for "today's leads/inquiries", filter by today's date
- Format responses clearly with summaries and details
- If data is not available, explain what data you do have access to
- Only ask for clarification when the request is genuinely ambiguous

Your tone is professional, helpful, and efficient. Always provide actionable information with clean, readable formatting.
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

def load_inquiries_data(filepath="inquiries.json"):
    """
    Load inquiries data from a JSON file, trying multiple common paths.
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
                    inquiries_data = json.load(f)
                print(f"✓ Loaded {len(inquiries_data)} inquiries from {path}")
                return inquiries_data

        print(f"⚠️ Could not find {filepath} in any expected location.")
        return []

    except Exception as e:
        print(f"Error loading inquiries data: {e}")
        return []

# Load both datasets at start
leads_data = load_leads_data()
inquiries_data = load_inquiries_data()
chat_history = []

# Conversation context tracks current query focus
conversation_context = {
    "current_topic": None,
    "data_type": None,  # "leads" or "inquiries"
    "lead_type_focus": None,
    "date_filter": None,
    "last_query_type": None
}

def get_today_leads():
    """Return leads from today's date."""
    today_str = str(date.today())
    return [lead for lead in leads_data if lead.get("timestamp", "").startswith(today_str)]

def get_today_inquiries():
    """Return inquiries from today's date."""
    today_str = str(date.today())
    return [inquiry for inquiry in inquiries_data if inquiry.get("timestamp", "").startswith(today_str)]

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

def format_leads_summary():
    """
    Returns a well-formatted summary of leads with improved layout.
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

    # Create formatted response
    formatted_response = f"""
LEADS OVERVIEW
==============
Total Leads: {total}
Today's Leads: {len(today_leads)}

LEAD SOURCES
------------"""
    
    for source, count in sorted(source_counts.items()):
        formatted_response += f"\n• {source}: {count}"
    
    formatted_response += f"""

CAR BRANDS
----------"""
    
    for brand, count in sorted(brand_counts.items()):
        formatted_response += f"\n• {brand}: {count}"
    
    # Add today's leads details if any exist
    if today_leads:
        formatted_response += f"""

TODAY'S LEAD DETAILS
-------------------"""
        for i, lead in enumerate(today_leads, 1):
            formatted_response += f"""

{i}. {lead.get('name', 'Unknown')}
   Source: {lead.get('lead_source', 'Unknown')}
   Interest: {lead.get('car_interest', 'Not specified')}
   Budget: {lead.get('budget', 'Not specified')}
   Contact: {lead.get('phone', 'N/A')} | {lead.get('email', 'N/A')}"""
            if lead.get('test_drive_date'):
                formatted_response += f"\n   Test Drive: {lead.get('test_drive_date')}"
    
    return formatted_response

def format_inquiries_summary():
    """
    Returns a well-formatted summary of inquiries with improved layout.
    Note: This is a template - adjust based on your actual inquiries.json structure
    """
    total = len(inquiries_data)
    today_inquiries = get_today_inquiries()

    # This section will need to be adjusted based on your actual inquiries.json structure
    # For now, using generic field names
    
    formatted_response = f"""
INQUIRIES OVERVIEW
==================
Total Inquiries: {total}
Today's Inquiries: {len(today_inquiries)}"""
    
    # Add today's inquiries details if any exist
    if today_inquiries:
        formatted_response += f"""

TODAY'S INQUIRY DETAILS
----------------------"""
        for i, inquiry in enumerate(today_inquiries, 1):
            formatted_response += f"""

{i}. {inquiry.get('name', 'Unknown')}"""
            # Add other fields based on your actual inquiries.json structure
            for key, value in inquiry.items():
                if key not in ['name', 'timestamp']:
                    formatted_response += f"\n   {key.replace('_', ' ').title()}: {value}"
    
    return formatted_response

def format_today_leads():
    """Format today's leads with improved layout."""
    today_leads = get_today_leads()
    
    if not today_leads:
        return "\nTODAY'S LEADS\n=============\nNo leads found for today."
    
    formatted_response = f"""
TODAY'S LEADS ({len(today_leads)})
{'=' * (15 + len(str(len(today_leads))))}"""
    
    for i, lead in enumerate(today_leads, 1):
        formatted_response += f"""

{i}. {lead.get('name', 'Unknown')}
   Source: {lead.get('lead_source', 'Unknown')}
   Interest: {lead.get('car_interest', 'Not specified')}
   Budget: {lead.get('budget', 'Not specified')}
   Phone: {lead.get('phone', 'N/A')}
   Email: {lead.get('email', 'N/A')}"""
        if lead.get('test_drive_date'):
            formatted_response += f"\n   Test Drive: {lead.get('test_drive_date')}"
    
    return formatted_response

def format_today_inquiries():
    """Format today's inquiries with improved layout."""
    today_inquiries = get_today_inquiries()
    
    if not today_inquiries:
        return "\nTODAY'S INQUIRIES\n=================\nNo inquiries found for today."
    
    formatted_response = f"""
TODAY'S INQUIRIES ({len(today_inquiries)})
{'=' * (19 + len(str(len(today_inquiries))))}"""
    
    for i, inquiry in enumerate(today_inquiries, 1):
        formatted_response += f"""

{i}. {inquiry.get('name', 'Unknown')}"""
        # Add other fields based on your actual inquiries.json structure
        for key, value in inquiry.items():
            if key not in ['name', 'timestamp']:
                formatted_response += f"\n   {key.replace('_', ' ').title()}: {value}"
    
    return formatted_response

def format_leads_by_source(source_name):
    """Format leads by source with improved layout."""
    source_leads = get_leads_by_source(source_name)
    
    if not source_leads:
        return f"\n{source_name.upper()} LEADS\n{'=' * (len(source_name) + 6)}\nNo {source_name} leads found."
    
    formatted_response = f"""
{source_name.upper()} LEADS ({len(source_leads)})
{'=' * (len(source_name) + 8 + len(str(len(source_leads))))}"""
    
    for i, lead in enumerate(source_leads, 1):
        formatted_response += f"""

{i}. {lead.get('name', 'Unknown')}
   Interest: {lead.get('car_interest', 'Not specified')}
   Budget: {lead.get('budget', 'Not specified')}
   Phone: {lead.get('phone', 'N/A')}
   Email: {lead.get('email', 'N/A')}"""
        if lead.get('test_drive_date'):
            formatted_response += f"\n   Test Drive: {lead.get('test_drive_date')}"
    
    return formatted_response

def format_leads_by_brand(brand):
    """Format leads by car brand with improved layout."""
    brand_leads = get_leads_by_car_interest(brand)
    
    if not brand_leads:
        return f"\n{brand.upper()} LEADS\n{'=' * (len(brand) + 6)}\nNo {brand} leads found."
    
    formatted_response = f"""
{brand.upper()} LEADS ({len(brand_leads)})
{'=' * (len(brand) + 8 + len(str(len(brand_leads))))}"""
    
    for i, lead in enumerate(brand_leads, 1):
        formatted_response += f"""

{i}. {lead.get('name', 'Unknown')}
   Source: {lead.get('lead_source', 'Unknown')}
   Car Model: {lead.get('car_interest', 'Not specified')}
   Budget: {lead.get('budget', 'Not specified')}
   Phone: {lead.get('phone', 'N/A')}
   Email: {lead.get('email', 'N/A')}"""
        if lead.get('test_drive_date'):
            formatted_response += f"\n   Test Drive: {lead.get('test_drive_date')}"
    
    return formatted_response

def analyze_user_intent(user_input):
    """
    Analyze the user input to update conversation context.
    Detects whether user is asking about leads or inquiries, plus other filters.
    """
    user_lower = user_input.lower()

    # Reset context on new input
    conversation_context["date_filter"] = None
    conversation_context["lead_type_focus"] = None
    conversation_context["current_topic"] = None
    conversation_context["last_query_type"] = None
    conversation_context["data_type"] = None

    # Determine if asking about leads or inquiries
    if any(word in user_lower for word in ["inquiry", "inquiries"]):
        conversation_context["data_type"] = "inquiries"
        conversation_context["current_topic"] = "all_inquiries"
    elif any(word in user_lower for word in ["leads", "lead"]):
        conversation_context["data_type"] = "leads"
        conversation_context["current_topic"] = "all_leads"

    # Date-related keywords
    if any(word in user_lower for word in ["today", "today's", "this morning", "this afternoon"]):
        conversation_context["date_filter"] = "today"

    # Car brands list - can be expanded (only relevant for leads)
    if conversation_context["data_type"] == "leads":
        car_brands = [
            "bmw", "toyota", "honda", "ford", "nissan", "mercedes",
            "volkswagen", "hyundai", "kia", "mazda", "chevrolet", "tesla"
        ]
        for brand in car_brands:
            if brand in user_lower:
                conversation_context["lead_type_focus"] = f"car_{brand}"
                break

        # Lead source detection (only relevant for leads)
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

    # Query type detection
    if any(word in user_lower for word in ["how many", "count", "number of"]):
        conversation_context["last_query_type"] = "count"
    elif any(word in user_lower for word in ["show", "list", "see", "give me", "what are"]):
        conversation_context["last_query_type"] = "list"
    else:
        conversation_context["last_query_type"] = "general"

def prepare_context_data(user_input):
    """
    Prepare and format relevant data based on analyzed context.
    Returns a formatted string to append to user input for better AI response.
    """
    analyze_user_intent(user_input)
    context_info = ""

    # Handle inquiries data
    if conversation_context["data_type"] == "inquiries":
        if conversation_context["date_filter"] == "today":
            context_info = format_today_inquiries()
        else:
            context_info = format_inquiries_summary()
    
    # Handle leads data (existing logic)
    elif conversation_context["data_type"] == "leads":
        # If filter for today's leads
        if conversation_context["date_filter"] == "today":
            context_info = format_today_leads()

        # Filter for specific car brand leads
        elif conversation_context["lead_type_focus"] and conversation_context["lead_type_focus"].startswith("car_"):
            brand = conversation_context["lead_type_focus"].replace("car_", "")
            context_info = format_leads_by_brand(brand)

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
            context_info = format_leads_by_source(source)

        # General leads summary
        else:
            context_info = format_leads_summary()

    return context_info

def generate_response(user_input):
    """
    Generate AI response based on user input combined with contextual data.
    """
    # Prepare enriched prompt with relevant data context
    enriched_user_input = user_input + prepare_context_data(user_input)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": enriched_user_input}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=800,
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
    print(f"Loaded {len(leads_data)} leads and {len(inquiries_data)} inquiries.")
    while True:
        user_msg = input("\nYou: ")
        if user_msg.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        answer = generate_response(user_msg)
        print(f"CarGPT: {answer}")