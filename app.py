from flask import Flask, render_template, request, jsonify
import sys
import os

# Add the chatbot directory to the Python path so we can import logic
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'chatbot')))

from logic import generate_response

app = Flask(__name__, static_folder='ui', template_folder='ui')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    bot_reply = generate_response(user_input)
    return jsonify({'reply': bot_reply})

if __name__ == '__main__':
    # Ensure the environment variable is set before running
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it before running the app.")
        # Example for PowerShell:
        # $env:OPENAI_API_KEY = 'your-api-key'
        # Example for Linux/macOS:
        # export OPENAI_API_KEY='your-api-key'
        sys.exit(1)

    # In a production environment, you would use a production-ready WSGI server like Gunicorn or uWSGI
    # For development, debug=True is useful but should be disabled in production
    app.run(debug=True)
