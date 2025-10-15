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
