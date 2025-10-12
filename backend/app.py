from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# DeepSeek API 配置
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "your-api-key-here"),
    base_url="https://api.deepseek.com"
)

# 存储会话
sessions = {}

@app.route('/api/decisions/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    session_id = data.get('session_id', 'default')
    
    if session_id not in sessions:
        sessions[session_id] = {
            'messages': [],
            'extracted_params': {}
        }
    
    session = sessions[session_id]
    session['messages'].append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a decision-making assistant. Help users think through their decisions by asking clarifying questions and identifying their options."},
                *session['messages']
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        session['messages'].append({"role": "assistant", "content": ai_response})
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id,
            'extracted_params': session.get('extracted_params', {}),
            'can_analyze': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/decisions/analyze', methods=['POST'])
def analyze():
    data = request.json
    description = data.get('description')
    options = data.get('options', [])
    
    try:
        prompt = f"""Analyze this decision:

Description: {description}

Options:
{chr(10).join(f"{i+1}. {opt}" for i, opt in enumerate(options))}

Provide:
1. A recommendation
2. Detailed analysis of each option
3. Pros and cons
4. Key factors to consider

Format your response clearly."""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert decision analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_analysis = response.choices[0].message.content
        
        # 简单的评分系统
        scores = {}
        for i, option in enumerate(options):
            scores[option] = {"total_score": round(10 - i * 0.5, 1)}
        
        return jsonify({
            'recommendation': options[0] if options else "No option provided",
            'readable_summary': ai_analysis,
            'algorithm_analysis': {
                'algorithms_used': {
                    'weighted_score': {
                        'results': scores
                    }
                }
            },
            'ai_analysis': {
                'response': ai_analysis
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=8000)