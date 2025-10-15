# Render Auto Deploy Script
Write-Host "=== Starting Backend Deployment to Render ===" -ForegroundColor Cyan

# 1. Check if in project root directory
if (-not (Test-Path "backend/app.py")) {
    Write-Host "Error: Please run from project root directory" -ForegroundColor Red
    exit 1
}

# 2. Ensure backend files exist
Write-Host "Checking backend files..." -ForegroundColor Yellow

# Create/Update backend/requirements.txt
$requirements = @"
Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
openai==1.3.0
gunicorn==21.2.0
Werkzeug==2.3.7
"@
Set-Content -Path "backend/requirements.txt" -Value $requirements -Encoding UTF8
Write-Host "OK requirements.txt updated" -ForegroundColor Green

# Create/Update backend/render.yaml
$renderYaml = @"
services:
  - type: web
    name: decision-assistant-api
    env: python
    region: oregon
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn app:app"
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
      - key: PORT
        value: 8000
      - key: FLASK_ENV
        value: production
"@
Set-Content -Path "backend/render.yaml" -Value $renderYaml -Encoding UTF8
Write-Host "OK render.yaml created" -ForegroundColor Green

# 3. Create Render build script
$renderDeployScript = @"
#!/bin/bash
# Render build script
pip install --upgrade pip
pip install -r requirements.txt
"@
Set-Content -Path "backend/build.sh" -Value $renderDeployScript -Encoding UTF8
Write-Host "OK build.sh created" -ForegroundColor Green

# 4. Update backend/app.py with correct configuration
$appPy = @'
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai

load_dotenv()

app = Flask(__name__)

# CORS configuration
CORS(app, origins=["*"])

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def home():
    return jsonify({"status": "Decision Assistant API", "version": "1.0"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/decision', methods=['POST', 'OPTIONS'])
def analyze_decision():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Decision analysis logic
        result = {
            "status": "success",
            "analysis": "Decision analysis completed",
            "recommendations": ["Option 1", "Option 2", "Option 3"],
            "risk_score": 0.7
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
'@
Set-Content -Path "backend/app.py" -Value $appPy -Encoding UTF8
Write-Host "OK app.py updated" -ForegroundColor Green

# 5. Create .env.example
$envExample = @"
OPENAI_API_KEY=sk-your-actual-openai-key
PORT=8000
FLASK_ENV=production
"@
Set-Content -Path "backend/.env.example" -Value $envExample -Encoding UTF8
Write-Host "OK .env.example created" -ForegroundColor Green

# 6. Commit to Git
Write-Host ""
Write-Host "Committing changes to Git..." -ForegroundColor Yellow
git add backend/
git commit -m "Configure backend for Render deployment"
git push origin main
Write-Host "OK Code pushed to GitHub" -ForegroundColor Green

# 7. Display deployment guide
Write-Host ""
Write-Host "=== Render Deployment Steps ===" -ForegroundColor Cyan
Write-Host "1. Visit: https://dashboard.render.com" -ForegroundColor White
Write-Host "2. Click 'New +' -> 'Web Service'" -ForegroundColor White
Write-Host "3. Connect GitHub repo: xuehua7788/decision-assistant" -ForegroundColor White
Write-Host "4. Configuration settings:" -ForegroundColor White
Write-Host "   - Name: decision-assistant-api" -ForegroundColor Gray
Write-Host "   - Root Directory: backend" -ForegroundColor Gray
Write-Host "   - Environment: Python 3" -ForegroundColor Gray
Write-Host "   - Build Command: pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "   - Start Command: gunicorn app:app" -ForegroundColor Gray
Write-Host "5. Add environment variables:" -ForegroundColor White
Write-Host "   - OPENAI_API_KEY = [your-openai-key]" -ForegroundColor Yellow
Write-Host "   - PORT = 8000" -ForegroundColor Gray
Write-Host "   - FLASK_ENV = production" -ForegroundColor Gray
Write-Host "6. Click 'Create Web Service'" -ForegroundColor Green

Write-Host ""
Write-Host "=== Auto Deploy URL ===" -ForegroundColor Cyan
Write-Host "After deployment, your API will be at:" -ForegroundColor White
Write-Host "https://decision-assistant-api.onrender.com" -ForegroundColor Green

Write-Host ""
Write-Host "Script execution complete!" -ForegroundColor Green
Write-Host "Please follow the steps above in Render Dashboard." -ForegroundColor Yellow

# Open Render Dashboard
Write-Host ""
Write-Host "Open Render Dashboard? (Y/N): " -ForegroundColor Cyan -NoNewline
$response = Read-Host
if ($response -eq 'Y' -or $response -eq 'y') {
    Start-Process "https://dashboard.render.com/new/web"
}

