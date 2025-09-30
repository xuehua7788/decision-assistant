import os
from typing import Optional
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        # 使用 DeepSeek API
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "sk-d3196d8e68c44690998d79c715ce715d")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.ai_available = bool(self.api_key)
    
    def get_response(self, message: str, context: Optional[list] = None) -> str:
        """获取 AI 回复"""
        if not self.ai_available:
            return self._get_mock_response(message)
        
        try:
            # 构建消息列表
            messages = self._build_messages(message, context)
            
            # 调用 DeepSeek API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"DeepSeek API error: {response.status_code} - {response.text}")
                return self._get_mock_response(message)
                
        except Exception as e:
            print(f"AI API error: {e}")
            return self._get_mock_response(message)
    
    def _build_messages(self, message: str, context: Optional[list]) -> list:
        """构建 DeepSeek 消息格式"""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful decision-making assistant. "
                    "Help users think through their decisions clearly and analytically. "
                    "Provide structured advice, consider pros and cons, and ask clarifying questions when needed. "
                    "Be supportive but analytical. Respond in the same language as the user."
                )
            }
        ]
        
        # 添加历史上下文（如果有）
        if context:
            for msg in context[-6:]:  # 使用最近6条消息作为上下文
                if msg.get("role") and msg.get("content"):
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        
        # 添加当前消息
        messages.append({
            "role": "user",
            "content": message
        })
        
        return messages
    
    def _get_mock_response(self, message: str) -> str:
        """没有 API key 时的智能模拟回复"""
        message_lower = message.lower()
        
        # 决策相关的关键词
        if any(word in message_lower for word in ["decision", "decide", "choose", "option", "help", "决定", "选择", "帮助"]):
            return ("I understand you're facing a decision. While I'm currently in demo mode, "
                   "I can help you think through your options. Could you tell me more about "
                   "what specific decision you're trying to make?")
        
        elif any(word in message_lower for word in ["career", "job", "work", "职业", "工作"]):
            return ("Career decisions are important choices that can impact your future. "
                   "Consider factors like: your interests, growth opportunities, work-life balance, "
                   "and long-term goals. What specific aspect of your career decision concerns you most?")
        
        elif any(word in message_lower for word in ["house", "housing", "buy", "rent", "房", "买", "租"]):
            return ("Housing decisions involve many factors: budget, location, size, and timing. "
                   "It's helpful to list your priorities and constraints. "
                   "Are you considering buying vs renting, or looking at specific properties?")
        
        elif any(word in message_lower for word in ["invest", "investment", "money", "投资", "钱"]):
            return ("Investment decisions require careful consideration of risk tolerance, "
                   "time horizon, and financial goals. It's always wise to research thoroughly "
                   "and perhaps consult with financial advisors. What's your main investment goal?")
        
        elif "?" in message or "？" in message:
            return ("That's a great question. In making any decision, it helps to: "
                   "1) Clearly define your goals, 2) List all options, "
                   "3) Consider pros and cons, 4) Think about long-term impacts. "
                   "What matters most to you in this situation?")
        
        else:
            return ("I'm here to help you think through your decisions. "
                   "Could you share more details about what you're trying to decide? "
                   "The more context you provide, the better I can assist you in "
                   "organizing your thoughts and evaluating your options.")

# 创建全局实例
ai_service = AIService()
