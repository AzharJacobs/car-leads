# car-leads

car-leads-demo/
│
├── leads.json                 # Fake leads data (output from "phone call")
│
├── app.py                     # Python chatbot demo script (reads JSON, responds)
│
├── chatbot/
│   ├── __init__.py
│   └── logic.py               # Functions to handle lead queries
│
├── audio/
│   └── sample-call.mp3        # Optional: mock customer call recording (fake)
│
├── ui/                        # (Optional) If you want a basic web UI later
│   ├── index.html             # Simple chat interface
│   ├── script.js              # JS logic to simulate chatbot
│   └── style.css              # Basic styling
│
├── README.md                  # Short explanation for client/demo notes