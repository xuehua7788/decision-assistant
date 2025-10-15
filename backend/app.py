import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai

load_dotenv()

app = Flask(__name__)

# CORS configuration - allow frontend domains
CORS(app, origins=[
    "http://localhost:3000",
    "http://localhost:5173", 
    "https://*.vercel.app",
    "https://decision-assistant-git-main-bruces-projects-409b2d51.vercel.app",
    "https://decision-assistant-4rc7aai2-bruces-projects-409b2d51.vercel.app"
])

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def home():
    return jsonify({"status": "API is running", "version": "1.0"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/decision', methods=['POST', 'OPTIONS'])
def analyze_decision():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.json
        # Decision analysis logic
        result = {
            "analysis": "Decision analysis result",
            "recommendations": ["Recommendation 1", "Recommendation 2"],
            "risk_score": 0.7
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
