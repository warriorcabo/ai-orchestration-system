# monitoring_dashboard.py

import os
import json
import logging
import datetime
from flask import Flask, render_template_string, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# HTML template for the dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Orchestration System - Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        h1, h2, h3 {
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .error {
            color: #dc3545;
        }
        .success {
            color: #28a745;
        }
        .warning {
            color: #ffc107;
        }
        .refresh-btn {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
    <script>
        function refreshData() {
            fetch('/api/system-status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('last-refresh').textContent = new Date().toLocaleString();
                    document.getElementById('api-status').innerHTML = '';
                    
                    // Update API status
                    for (const [api, status] of Object.entries(data.apis)) {
                        const row = document.createElement('tr');
                        const apiCell = document.createElement('td');
                        apiCell.textContent = api;
                        
                        const statusCell = document.createElement('td');
                        statusCell.textContent = status.status;
                        statusCell.className = status.status === 'OK' ? 'success' : 'error';
                        
                        const messageCell = document.createElement('td');
                        messageCell.textContent = status.message || '';
                        
                        row.appendChild(apiCell);
                        row.appendChild(statusCell);
                        row.appendChild(messageCell);
                        document.getElementById('api-status').appendChild(row);
                    }
                    
                    // Update storage status
                    document.getElementById('drive-status').textContent = 
                        data.storage.available ? 'Connected' : 'Disconnected';
                    document.getElementById('drive-status').className = 
                        data.storage.available ? 'success' : 'error';
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });
        }
        
        // Refresh on load and every 30 seconds
        window.onload = function() {
            refreshData();
            setInterval(refreshData, 30000);
        };
    </script>
</head>
<body>
    <div class="container">
        <h1>AI Orchestration System - Dashboard</h1>
        <p>Last refreshed: <span id="last-refresh">Loading...</span> 
           <button class="refresh-btn" onclick="refreshData()">Refresh</button>
        </p>
        
        <div class="card">
            <h2>API Status</h2>
            <table>
                <thead>
                    <tr>
                        <th>API</th>
                        <th>Status</th>
                        <th>Message</th>
                    </tr>
                </thead>
                <tbody id="api-status">
                    <tr>
                        <td colspan="3">Loading...</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h2>Storage Status</h2>
            <p>Google Drive: <span id="drive-status">Checking...</span></p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/dashboard')
def dashboard():
    """Render the monitoring dashboard"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/system-status')
def system_status():
    """API endpoint for system status"""
    try:
        # Import services (only when needed)
        from src.utils.google_drive_storage import GoogleDriveStorage
        
        # Check API status
        apis_status = {
            "Telegram Bot": check_telegram_status(),
            "OpenAI API": check_openai_status(),
            "Gemini API": check_gemini_status(),
            "Google Drive API": check_google_drive_status()
        }
        
        # Check storage status
        google_drive = GoogleDriveStorage()
        storage_status = {
            "available": google_drive.is_available
        }
        
        return jsonify({
            "timestamp": datetime.datetime.now().isoformat(),
            "apis": apis_status,
            "storage": storage_status
        })
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return jsonify({
            "timestamp": datetime.datetime.now().isoformat(),
            "error": str(e)
        }), 500

def check_telegram_status():
    """Check Telegram Bot status"""
    telegram_token = os.environ.get("TELEGRAM_TOKEN")
    if not telegram_token:
        return {"status": "ERROR", "message": "Telegram token not configured"}
    
    return {"status": "OK", "message": "Token configured"}

def check_openai_status():
    """Check OpenAI API status"""
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        return {"status": "ERROR", "message": "OpenAI API key not configured"}
    
    return {"status": "OK", "message": "API key configured"}

def check_gemini_status():
    """Check Gemini API status"""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        return {"status": "ERROR", "message": "Gemini API key not configured"}
    
    return {"status": "OK", "message": "API key configured"}

def check_google_drive_status():
    """Check Google Drive status"""
    drive_folder = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
    credentials = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    
    if not drive_folder:
        return {"status": "ERROR", "message": "Drive folder ID not configured"}
    
    if not credentials:
        return {"status": "ERROR", "message": "Credentials not configured"}
    
    return {"status": "OK", "message": "Drive configured"}

# Add route to main app.py
@app.route('/webhook/<token>', methods=['POST'])
def webhook(token):
    """Handle webhook requests from Telegram"""
    if token != os.environ.get("TELEGRAM_TOKEN"):
        return jsonify({"status": "error", "message": "Invalid token"}), 403
    
    # Process the webhook request
    return jsonify({"status": "success"})

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=port)
