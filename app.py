# Simple test app.py
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World! This is a test Flask app."

@app.route('/debug')
def debug():
    return f"ENV: {os.environ.get('DYNO', 'No dyno')}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
