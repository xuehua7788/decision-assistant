#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像驱动的策略优化器
结合用户画像和实时意图，优化期权策略参数
"""

from typing import Dict, Optional
import copy

class ProfileBasedStrategyOptimizer:
    """画像驱动的策略优化器"""
    
    def optimize_strategy(self, 
                         base_strategy: Dict,
                         user_profile: Dict,
                         parsed_intent: Dict) -> Dict:
        """
        基于用户画像优化策略参数
        
        Args:
            base_strategy: 基础策略（AI #1生成）
            user_profile: 用户画像（AI #3分析）
            parsed_intent: 用户意图（AI #1解析）
        
        Returns:
            优化后的策略
        """
        
        print("🎯 开始策略优化...")
        
        if not user_profile or user_profile.get('status') in ['insufficient_data', 'error']:
            # 没有画像数据，返回原策略
            print("   ⚠️ 没有用户画像数据，使用默认策略")
            return base_strategy
        
        # 深拷贝策略，避免修改原对象
        optimized_strategy = copy.deepcopy(base_strategy)
        
        # 提取画像特征
        inv_pref = user_profile.get('investment_preferences', {})
        knowledge = user_profile.get('knowledge_level', {})
        emotion = user_profile.get('emotional_traits', {})
        behav = user_profile.get('behavioral_traits', {})
        recommendations = user_profile.get('recommendations', {})
        
        # 提取策略参数
        parameters = optimized_strategy.get('parameters', {})
        adjustment_reasons = []
        
        print(f"   📊 用户画像:")
        print(f"      风险偏好: {inv_pref.get('risk_tolerance', 'unknown')}")
        print(f"      期权经验: {knowledge.get('option_experience', 'unknown')}")
        print(f"      投资风格: {inv_pref.get('investment_style', 'unknown')}")
        
        # 1. 根据风险偏好调整仓位大小
        risk_tolerance = inv_pref.get('risk_tolerance', 'moderate')
        if 'quantity' in parameters:
            original_qty = parameters['quantity']
            
            if risk_tolerance == 'conservative':
                # 保守型：减少仓位30%
                parameters['quantity'] = max(1, int(original_qty * 0.7))
                adjustment_reasons.append(
                    f"根据保守风险偏好，将仓位从 {original_qty} 手调整为 {parameters['quantity']} 手"
                )
            elif risk_tolerance == 'aggressive':
                # 激进型：增加仓位30%（但有上限）
                parameters['quantity'] = min(10, int(original_qty * 1.3))
                adjustment_reasons.append(
                    f"根据激进风险偏好，将仓位从 {original_qty} 手调整为 {parameters['quantity']} 手"
                )
        
        # 2. 根据期权经验调整策略复杂度和行权价
        option_exp = knowledge.get('option_experience', 'basic')
        if option_exp in ['none', 'basic']:
            # 新手：选择更保守的行权价
            if 'strike' in parameters and 'current_price' in parameters:
                current_price = parameters['current_price']
                original_strike = parameters['strike']
                direction = parsed_intent.get('direction', 'bullish')
                
                if direction == 'bullish':
                    # 看涨：选择更接近平值的行权价（降低风险）
                    parameters['strike'] = current_price * 1.02  # 2% OTM
                    adjustment_reasons.append(
                        f"考虑到期权经验有限，将看涨行权价从 ${original_strike:.2f} 调整为 ${parameters['strike']:.2f}（更接近平值，提高成功率）"
                    )
                elif direction == 'bearish':
                    # 看跌：选择更接近平值的行权价
                    parameters['strike'] = current_price * 0.98  # 2% OTM
                    adjustment_reasons.append(
                        f"考虑到期权经验有限，将看跌行权价从 ${original_strike:.2f} 调整为 ${parameters['strike']:.2f}（更接近平值，提高成功率）"
                    )
            
            # 新手：添加风险提示
            adjustment_reasons.append(
                "建议先用小仓位熟悉期权交易，并关注Greeks（Delta、Theta等）的变化"
            )
        
        # 3. 根据时间偏好调整到期时间
        time_horizon = inv_pref.get('time_horizon', 'medium')
        if 'days_to_expiry' in parameters:
            original_days = parameters['days_to_expiry']
            
            if time_horizon == 'short':
                parameters['days_to_expiry'] = 30  # 1个月
            elif time_horizon == 'medium':
                parameters['days_to_expiry'] = 45  # 1.5个月
            elif time_horizon == 'long':
                parameters['days_to_expiry'] = 60  # 2个月
            
            if original_days != parameters['days_to_expiry']:
                adjustment_reasons.append(
                    f"根据您的 {self._translate_horizon(time_horizon)} 投资偏好，将到期时间从 {original_days} 天调整为 {parameters['days_to_expiry']} 天"
                )
        
        # 4. 根据信心水平调整
        confidence = emotion.get('confidence_level', 0.5)
        if confidence < 0.5:
            # 信心不足：建议更保守的策略
            adjustment_reasons.append(
                f"检测到您的信心水平较低（{confidence:.1%}），建议采用更保守的参数设置，或等待更明确的信号"
            )
        elif confidence > 0.8:
            adjustment_reasons.append(
                f"您对此次交易信心较高（{confidence:.1%}），但仍建议控制仓位，避免过度自信"
            )
        
        # 5. 根据决策速度调整
        decision_speed = behav.get('decision_speed', 'moderate')
        if decision_speed == 'fast':
            adjustment_reasons.append(
                "您倾向于快速决策，建议设置止损点，避免冲动交易"
            )
        elif decision_speed == 'slow':
            adjustment_reasons.append(
                "您倾向于深思熟虑，这是好习惯。建议关注时间价值衰减（Theta）"
            )
        
        # 6. 应用AI #3的个性化建议
        param_adjustments = recommendations.get('parameter_adjustments', {})
        personalization_notes = recommendations.get('personalization_notes', '')
        
        if personalization_notes:
            adjustment_reasons.append(f"AI画像分析: {personalization_notes}")
        
        # 7. 更新策略描述
        if adjustment_reasons:
            print(f"   ✅ 应用了 {len(adjustment_reasons)} 项个性化调整")
            
            personalization_section = "\n\n**🎯 个性化调整说明**:\n" + "\n".join(
                f"{i+1}. {reason}" for i, reason in enumerate(adjustment_reasons)
            )
            
            optimized_strategy['description'] = optimized_strategy.get('description', '') + personalization_section
        else:
            print("   ℹ️ 无需调整，策略已适合用户画像")
        
        # 8. 更新参数
        optimized_strategy['parameters'] = parameters
        
        # 9. 添加优化元数据
        optimized_strategy['optimization_metadata'] = {
            'optimized': len(adjustment_reasons) > 0,
            'adjustment_count': len(adjustment_reasons),
            'user_profile_applied': True,
            'risk_tolerance': risk_tolerance,
            'option_experience': option_exp
        }
        
        return optimized_strategy
    
    def _translate_horizon(self, horizon: str) -> str:
        """翻译时间范围"""
        mapping = {
            'short': '短期',
            'medium': '中期',
            'long': '长期'
        }
        return mapping.get(horizon, horizon)
    
    def save_recommendation_to_db(self, db_conn, username: str, 
                                 user_intent: Dict, user_profile: Dict,
                                 original_strategy: Dict, optimized_strategy: Dict) -> bool:
        """
        保存策略推荐到数据库
        
        Args:
            db_conn: 数据库连接
            username: 用户名
            user_intent: 用户意图
            user_profile: 用户画像
            original_strategy: 原始策略
            optimized_strategy: 优化后策略
        
        Returns:
            是否保存成功
        """
        if not db_conn:
            return False
        
        try:
            cursor = db_conn.cursor()
            
            # 提取调整原因
            description = optimized_strategy.get('description', '')
            adjustment_section = description.split('**🎯 个性化调整说明**:')
            adjustment_reason = adjustment_section[1] if len(adjustment_section) > 1 else ''
            
            cursor.execute("""
                INSERT INTO strategy_recommendations (
                    username,
                    user_intent,
                    user_profile_snapshot,
                    strategy_type,
                    strategy_name,
                    strategy_parameters,
                    confidence_score,
                    adjustment_reason,
                    original_parameters,
                    adjusted_parameters,
                    personalization_notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                username,
                json.dumps(user_intent, ensure_ascii=False),
                json.dumps(user_profile, ensure_ascii=False),
                optimized_strategy.get('type'),
                optimized_strategy.get('name'),
                json.dumps(optimized_strategy.get('parameters', {}), ensure_ascii=False),
                user_profile.get('emotional_traits', {}).get('confidence_level', 0.5),
                adjustment_reason.strip(),
                json.dumps(original_strategy.get('parameters', {}), ensure_ascii=False),
                json.dumps(optimized_strategy.get('parameters', {}), ensure_ascii=False),
                user_profile.get('recommendations', {}).get('personalization_notes', '')
            ))
            
            db_conn.commit()
            cursor.close()
            print("   ✅ 策略推荐已保存到数据库")
            return True
            
        except Exception as e:
            print(f"   ❌ 保存策略推荐失败: {e}")
            db_conn.rollback()
            return False


# 测试代码
if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("画像驱动的策略优化器 - 测试")
    print("=" * 60)
    print()
    
    # 模拟基础策略
    base_strategy = {
        "name": "Bull Call Spread",
        "type": "bull_call_spread",
        "description": "适合看涨但想控制风险的投资者",
        "risk_level": "medium",
        "parameters": {
            "ticker": "TSLA",
            "current_price": 250.0,
            "strike": 260.0,
            "quantity": 5,
            "days_to_expiry": 45
        }
    }
    
    # 模拟用户画像
    user_profile = {
        "investment_preferences": {
            "risk_tolerance": "conservative",
            "investment_style": "value",
            "time_horizon": "short"
        },
        "knowledge_level": {
            "financial_knowledge": "intermediate",
            "option_experience": "basic"
        },
        "emotional_traits": {
            "sentiment_tendency": "cautious",
            "confidence_level": 0.4
        },
        "behavioral_traits": {
            "decision_speed": "slow",
            "information_depth": "deep"
        },
        "recommendations": {
            "personalization_notes": "用户对风险敏感，建议提供详细的风险说明"
        }
    }
    
    # 模拟用户意图
    parsed_intent = {
        "ticker": "TSLA",
        "direction": "bullish",
        "strength": "moderate"
    }
    
    # 执行优化
    optimizer = ProfileBasedStrategyOptimizer()
    optimized = optimizer.optimize_strategy(base_strategy, user_profile, parsed_intent)
    
    print("\n" + "=" * 60)
    print("优化结果:")
    print("=" * 60)
    print(json.dumps(optimized, ensure_ascii=False, indent=2))

