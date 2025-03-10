# AI Orchestration System

A system that integrates Gemini and ChatGPT through a central orchestrator, accessible via Telegram bot interface.

## Features
- AI model orchestration
- Telegram bot interface (warriorautomate_bot)
- Error handling system
- Monitoring dashboard

## Setup
1. Clone the repository
2. Create a virtual environment: python -m venv venv
3. Activate it: env\Scripts\activate
4. Install dependencies: pip install -r requirements.txt
5. Copy .env.template to .env and add your API keys
6. Run the dashboard: .\run_dashboard.bat
7. Run the system: .\run_system.bat

## Architecture
- AI Orchestrator coordinates between Gemini and ChatGPT
- Telegram bot provides user interface
- Dashboard monitors system status
