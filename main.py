from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    # Process user_input here later
    bot_response = f"You said: {user_input}" # Placeholder
    return bot_response

if __name__ == '__main__':
    app.run(debug=True) 