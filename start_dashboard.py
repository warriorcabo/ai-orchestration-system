import logging
import sys
from flask import Flask, jsonify, render_template_string

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# HTML template
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Orchestration System Dashboard</title>
    <style>
        body { font-family: Arial; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; }
        h1 { color: #333; }
        .status { padding: 10px; background: #e9f7ef; border-left: 5px solid #27ae60; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Orchestration System Dashboard</h1>
        <div class="status">
            <h2>System Status: Online</h2>
            <p>Dashboard is working correctly!</p>
        </div>
        <p>This dashboard confirms that the AI Orchestration System is operational.</p>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def status():
    return jsonify({"status": "online"})

if __name__ == '__main__':
    logger.info("Starting dashboard on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
