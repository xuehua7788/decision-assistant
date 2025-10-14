from typing import Optional

import requests

from app.core.config import get_settings


settings = get_settings()


class AIService:
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.ai_available = bool(self.api_key)

        if not self.ai_available:
            print(
                "DeepSeek API key not configured; AI responses will fall back to the mock generator."
            )

    def get_response(self, message: str, context: Optional[list] = None) -> str:
        """Return an AI-generated reply for the provided message."""
        if not self.ai_available:
            return self._get_mock_response(message)

        try:
            messages = self._build_messages(message, context)

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
            }

            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"DeepSeek API error: {response.status_code} - {response.text}")
                return self._get_mock_response(message)

        except Exception as exc:
            print(f"AI API error: {exc}")
            return self._get_mock_response(message)

    def _build_messages(self, message: str, context: Optional[list]) -> list:
        """Build the conversation payload expected by DeepSeek."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful decision-making assistant. "
                    "Help users think through their decisions clearly and analytically. "
                    "Provide structured advice, consider pros and cons, and ask clarifying questions when needed. "
                    "Be supportive but analytical. Respond in the same language as the user."
                ),
            }
        ]

        if context:
            for msg in context[-6:]:
                if msg.get("role") and msg.get("content"):
                    messages.append(
                        {
                            "role": msg["role"],
                            "content": msg["content"],
                        }
                    )

        messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

        return messages

    def _get_mock_response(self, message: str) -> str:
        """Return a deterministic mock response when the API key is missing."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["decision", "decide", "choose", "option", "help"]):
            return (
                "I understand you're facing a decision. While I'm currently in demo mode, "
                "I can help you think through your options. Could you tell me more about "
                "what specific decision you're trying to make?"
            )

        if any(word in message_lower for word in ["career", "job", "work", "employment"]):
            return (
                "Career decisions are important choices that can impact your future. "
                "Consider factors like your interests, growth opportunities, work-life balance, "
                "and long-term goals. What specific aspect of your career decision concerns you most?"
            )

        if any(word in message_lower for word in ["house", "housing", "buy", "rent", "apartment", "home"]):
            return (
                "Housing decisions involve many factors: budget, location, size, and timing. "
                "It's helpful to list your priorities and constraints. "
                "Are you considering buying versus renting, or evaluating specific properties?"
            )

        if any(word in message_lower for word in ["invest", "investment", "money", "finance", "financial"]):
            return (
                "Investment decisions require careful consideration of risk tolerance, "
                "time horizon, and financial goals. It's always wise to research thoroughly "
                "and perhaps consult with financial advisors. What's your main investment goal?"
            )

        if "?" in message or "what" in message_lower or "how" in message_lower:
            return (
                "That's a great question. In making any decision, it helps to: "
                "1) Clearly define your goals, 2) List all options, "
                "3) Consider pros and cons, 4) Think about long-term impacts. "
                "What matters most to you in this situation?"
            )

        return (
            "I'm here to help you think through your decisions. "
            "Could you share more details about what you're trying to decide? "
            "The more context you provide, the better I can assist you in "
            "organizing your thoughts and evaluating your options."
        )


ai_service = AIService()
