#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI #3: 用户画像分析器
分析用户的历史聊天记录，生成详细的用户画像
用于个性化投资建议和策略优化
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class UserProfileAnalyzer:
    """AI #3: 用户画像分析器"""
    
    def __init__(self, deepseek_api_key: str):
        self.api_key = deepseek_api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
    
    def analyze_user_profile(self, username: str, chat_history: List[Dict], 
                            days: int = 30) -> Dict:
        """
        分析用户画像
        
        Args:
            username: 用户名
            chat_history: 聊天历史 [{"role": "user/assistant", "content": "...", "timestamp": "..."}]
            days: 分析最近N天的记录
        
        Returns:
            用户画像字典
        """
        
        print(f"🔍 开始分析用户 {username} 的画像...")
        print(f"   时间范围: 最近 {days} 天")
        print(f"   消息总数: {len(chat_history)} 条")
        
        # 1. 过滤时间范围
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_messages = []
        
        for msg in chat_history:
            try:
                timestamp_str = msg.get('timestamp', '')
                if timestamp_str:
                    # 尝试解析时间戳
                    if isinstance(timestamp_str, str):
                        msg_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        msg_time = timestamp_str
                    
                    if msg_time > cutoff_date:
                        recent_messages.append(msg)
                else:
                    # 如果没有时间戳，也包含进来
                    recent_messages.append(msg)
            except:
                # 时间戳解析失败，也包含进来
                recent_messages.append(msg)
        
        if len(recent_messages) < 5:
            print(f"   ⚠️ 聊天记录不足（{len(recent_messages)} 条）")
            return {
                "status": "insufficient_data",
                "message": f"用户 {username} 的聊天记录不足（少于5条），无法进行画像分析"
            }
        
        print(f"   ✅ 筛选出 {len(recent_messages)} 条有效消息")
        
        # 2. 构建分析提示词
        system_prompt = self._build_analysis_prompt()
        
        # 3. 准备聊天历史摘要
        chat_summary = self._summarize_chat_history(recent_messages)
        
        # 4. 调用DeepSeek API
        user_prompt = f"""请分析以下用户的聊天记录，生成用户画像：

**用户名**: {username}
**分析时间范围**: 最近 {days} 天
**消息总数**: {len(recent_messages)} 条

**聊天记录摘要**:
{chat_summary}

请按照系统提示的JSON格式返回分析结果。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            print("   🤖 调用DeepSeek API进行分析...")
            
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.3,  # 降低温度，提高一致性
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                print("   ✅ AI分析完成")
                print(f"   响应长度: {len(ai_response)} 字符")
                
                # 解析JSON
                try:
                    profile = json.loads(ai_response.strip())
                except json.JSONDecodeError as e:
                    print(f"   ⚠️ JSON解析失败，尝试提取JSON部分...")
                    # 尝试提取JSON部分
                    import re
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        profile = json.loads(json_match.group())
                    else:
                        raise e
                
                # 添加元数据
                profile["metadata"] = {
                    "username": username,
                    "analyzed_at": datetime.now().isoformat(),
                    "analysis_period_days": days,
                    "total_messages_analyzed": len(recent_messages),
                    "analysis_version": "1.0"
                }
                
                print("   ✅ 用户画像生成成功")
                return profile
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ AI #3 分析失败: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _build_analysis_prompt(self) -> str:
        """构建AI #3的系统提示词"""
        return """你是一个专业的用户行为分析专家，专注于投资者画像分析。

**你的任务**：
分析用户的聊天记录，生成详细的用户画像，用于个性化投资建议。

**分析维度**：

1. **投资偏好**
   - risk_tolerance: conservative（保守）/ moderate（中等）/ aggressive（激进）
   - investment_style: value（价值投资）/ growth（成长投资）/ momentum（动量投资）/ contrarian（逆向投资）
   - time_horizon: short（短期，<3个月）/ medium（中期，3-12个月）/ long（长期，>1年）

2. **行为特征**
   - decision_speed: fast（快速决策）/ moderate（谨慎决策）/ slow（深思熟虑）
   - information_depth: shallow（浅层了解）/ moderate（适度研究）/ deep（深度研究）
   - chat_frequency: 聊天频率（次/周）

3. **知识水平**
   - financial_knowledge: beginner（初学者）/ intermediate（中级）/ advanced（高级）
   - option_experience: none（无经验）/ basic（基础）/ experienced（有经验）

4. **情绪特征**
   - sentiment_tendency: optimistic（乐观）/ pessimistic（悲观）/ balanced（平衡）
   - confidence_level: 0.0-1.0（信心水平）

5. **关键洞察**
   - key_interests: [关注的股票/行业列表]
   - common_questions: [常见问题类型]
   - decision_patterns: [决策模式描述]
   - risk_concerns: [风险关注点]

6. **推荐参数**
   - recommended_strategy_types: [适合的策略类型]
   - parameter_adjustments: {参数调整建议}
   - personalization_notes: "个性化建议"

**输出格式**（严格JSON）：
{
  "investment_preferences": {
    "risk_tolerance": "moderate",
    "investment_style": "growth",
    "time_horizon": "medium"
  },
  "behavioral_traits": {
    "decision_speed": "moderate",
    "information_depth": "moderate",
    "chat_frequency": 5
  },
  "knowledge_level": {
    "financial_knowledge": "intermediate",
    "option_experience": "basic"
  },
  "emotional_traits": {
    "sentiment_tendency": "optimistic",
    "confidence_level": 0.7
  },
  "key_insights": {
    "key_interests": ["TSLA", "NVDA", "AI sector"],
    "common_questions": ["technical analysis", "earnings impact"],
    "decision_patterns": "倾向于在财报前建仓，关注技术面突破",
    "risk_concerns": ["市场波动", "黑天鹅事件"]
  },
  "recommendations": {
    "recommended_strategy_types": ["bull_call_spread", "covered_call"],
    "parameter_adjustments": {
      "strike_selection": "略保守，选择更接近平值的行权价",
      "position_sizing": "建议单笔不超过总资金的10%",
      "time_decay_preference": "适合30-45天到期的期权"
    },
    "personalization_notes": "用户对技术分析有一定了解，但对期权Greeks理解有限，建议推荐简单策略并提供详细解释。"
  },
  "analysis_summary": "该用户是一位中等风险偏好的成长型投资者，对科技股特别是AI领域有浓厚兴趣。决策较为谨慎，会在行动前进行适度研究。期权经验有限，适合推荐风险可控的简单策略。"
}

**分析原则**：
1. 基于实际聊天内容，不要臆测
2. 如果某个维度信息不足，标注为"unknown"
3. 提供具体的、可操作的建议
4. 分析要客观、专业

请用中文分析，JSON键名用英文。"""
    
    def _summarize_chat_history(self, messages: List[Dict]) -> str:
        """
        将聊天历史转换为可分析的摘要
        """
        summary_lines = []
        
        # 最多取最近50条消息
        recent_msgs = messages[-50:] if len(messages) > 50 else messages
        
        for i, msg in enumerate(recent_msgs, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', 'N/A')
            
            # 截断过长的消息
            if len(content) > 200:
                content = content[:200] + "..."
            
            # 格式化时间戳
            if timestamp != 'N/A':
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            summary_lines.append(f"{i}. [{timestamp}] {role}: {content}")
        
        return "\n".join(summary_lines)
    
    def update_user_profile_in_db(self, db_conn, username: str, profile: Dict) -> bool:
        """
        将用户画像保存到数据库
        
        Args:
            db_conn: 数据库连接对象
            username: 用户名
            profile: 用户画像字典
        
        Returns:
            是否保存成功
        """
        if not db_conn:
            print("   ⚠️ 数据库连接不可用")
            return False
        
        try:
            cursor = db_conn.cursor()
            
            # 提取画像数据
            inv_pref = profile.get('investment_preferences', {})
            behav = profile.get('behavioral_traits', {})
            knowledge = profile.get('knowledge_level', {})
            emotion = profile.get('emotional_traits', {})
            metadata = profile.get('metadata', {})
            
            # 检查用户画像是否存在
            cursor.execute("SELECT id FROM user_profiles WHERE username = %s", (username,))
            result = cursor.fetchone()
            
            if result:
                # 更新现有画像
                print(f"   📝 更新用户 {username} 的画像...")
                cursor.execute("""
                    UPDATE user_profiles SET
                        risk_tolerance = %s,
                        investment_style = %s,
                        time_horizon = %s,
                        chat_frequency = %s,
                        decision_speed = %s,
                        information_depth = %s,
                        financial_knowledge = %s,
                        option_experience = %s,
                        sentiment_tendency = %s,
                        confidence_level = %s,
                        ai_analysis = %s,
                        analysis_summary = %s,
                        last_analyzed_at = %s,
                        total_messages_analyzed = %s,
                        updated_at = %s
                    WHERE username = %s
                """, (
                    inv_pref.get('risk_tolerance'),
                    inv_pref.get('investment_style'),
                    inv_pref.get('time_horizon'),
                    behav.get('chat_frequency'),
                    behav.get('decision_speed'),
                    behav.get('information_depth'),
                    knowledge.get('financial_knowledge'),
                    knowledge.get('option_experience'),
                    emotion.get('sentiment_tendency'),
                    emotion.get('confidence_level'),
                    json.dumps(profile, ensure_ascii=False),
                    profile.get('analysis_summary'),
                    metadata.get('analyzed_at'),
                    metadata.get('total_messages_analyzed'),
                    datetime.now(),
                    username
                ))
            else:
                # 插入新画像
                print(f"   ✨ 创建用户 {username} 的画像...")
                cursor.execute("""
                    INSERT INTO user_profiles (
                        username, risk_tolerance, investment_style, time_horizon,
                        chat_frequency, decision_speed, information_depth,
                        financial_knowledge, option_experience,
                        sentiment_tendency, confidence_level,
                        ai_analysis, analysis_summary,
                        last_analyzed_at, total_messages_analyzed
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    username,
                    inv_pref.get('risk_tolerance'),
                    inv_pref.get('investment_style'),
                    inv_pref.get('time_horizon'),
                    behav.get('chat_frequency'),
                    behav.get('decision_speed'),
                    behav.get('information_depth'),
                    knowledge.get('financial_knowledge'),
                    knowledge.get('option_experience'),
                    emotion.get('sentiment_tendency'),
                    emotion.get('confidence_level'),
                    json.dumps(profile, ensure_ascii=False),
                    profile.get('analysis_summary'),
                    metadata.get('analyzed_at'),
                    metadata.get('total_messages_analyzed')
                ))
            
            db_conn.commit()
            cursor.close()
            print(f"   ✅ 用户画像已保存到数据库")
            return True
            
        except Exception as e:
            print(f"   ❌ 保存用户画像失败: {e}")
            db_conn.rollback()
            import traceback
            traceback.print_exc()
            return False


# 全局单例
_profile_analyzer = None

def get_profile_analyzer():
    """获取用户画像分析器实例"""
    global _profile_analyzer
    if _profile_analyzer is None:
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        if not deepseek_api_key:
            raise Exception("DEEPSEEK_API_KEY not configured")
        _profile_analyzer = UserProfileAnalyzer(deepseek_api_key)
    return _profile_analyzer


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("AI #3 用户画像分析器 - 测试")
    print("=" * 60)
    print()
    
    # 模拟聊天历史
    test_chat_history = [
        {"role": "user", "content": "我想了解特斯拉的投资机会", "timestamp": datetime.now().isoformat()},
        {"role": "assistant", "content": "特斯拉是一家电动汽车公司...", "timestamp": datetime.now().isoformat()},
        {"role": "user", "content": "我比较保守，不想冒太大风险", "timestamp": datetime.now().isoformat()},
        {"role": "assistant", "content": "理解，那我们可以考虑一些保守的策略...", "timestamp": datetime.now().isoformat()},
        {"role": "user", "content": "期权是什么？我不太懂", "timestamp": datetime.now().isoformat()},
        {"role": "assistant", "content": "期权是一种金融衍生品...", "timestamp": datetime.now().isoformat()},
    ]
    
    try:
        analyzer = get_profile_analyzer()
        profile = analyzer.analyze_user_profile(
            username="test_user",
            chat_history=test_chat_history,
            days=30
        )
        
        print("\n" + "=" * 60)
        print("分析结果:")
        print("=" * 60)
        print(json.dumps(profile, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

