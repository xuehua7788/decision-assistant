"""
Decision Making Algorithms Module
包含多种决策分析算法
"""

import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class DecisionCriteria:
    """决策标准"""
    name: str
    weight: float
    description: str

@dataclass
class Option:
    """决策选项"""
    name: str
    scores: Dict[str, float]
    
class WeightedScoreAnalysis:
    """加权评分决策算法"""
    
    def __init__(self):
        self.default_criteria = [
            DecisionCriteria("cost_effectiveness", 0.25, "成本效益"),
            DecisionCriteria("time_efficiency", 0.20, "时间效率"),
            DecisionCriteria("risk_level", 0.20, "风险水平"),
            DecisionCriteria("long_term_benefit", 0.20, "长期收益"),
            DecisionCriteria("feasibility", 0.15, "可行性")
        ]
    
    def analyze(self, options: List[str], context: str = "") -> Dict[str, Any]:
        """分析决策选项"""
        results = {}
        
        for option in options:
            # 基于选项文本生成模拟评分
            scores = self._generate_scores(option, context)
            weighted_score = self._calculate_weighted_score(scores)
            
            results[option] = {
                "total_score": round(weighted_score, 2),
                "scores": scores,
                "rank": 0  # 将在后面计算
            }
        
        # 计算排名
        sorted_options = sorted(results.items(), key=lambda x: x[1]["total_score"], reverse=True)
        for rank, (option, data) in enumerate(sorted_options, 1):
            results[option]["rank"] = rank
            
        return {
            "algorithm": "Weighted Score Analysis",
            "results": results,
            "recommendation": sorted_options[0][0] if sorted_options else None,
            "criteria_used": [c.name for c in self.default_criteria]
        }
    
    def _generate_scores(self, option: str, context: str) -> Dict[str, float]:
        """生成评分（实际应用中应基于更复杂的逻辑）"""
        # 这里使用简单的规则生成评分
        base_score = 5.0
        
        scores = {}
        for criteria in self.default_criteria:
            # 基于选项文本特征调整评分
            score = base_score
            
            if criteria.name == "cost_effectiveness":
                if "cheap" in option.lower() or "budget" in option.lower():
                    score += 3
                elif "expensive" in option.lower() or "high-end" in option.lower():
                    score -= 2
                    
            elif criteria.name == "time_efficiency":
                if "now" in option.lower() or "immediate" in option.lower():
                    score += 2
                elif "wait" in option.lower() or "later" in option.lower():
                    score -= 1
                    
            elif criteria.name == "risk_level":
                if "safe" in option.lower() or "secure" in option.lower():
                    score += 2
                elif "risky" in option.lower():
                    score -= 3
                    
            scores[criteria.name] = min(10, max(1, score))
            
        return scores
    
    def _calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """计算加权总分"""
        total = 0
        for criteria in self.default_criteria:
            total += scores.get(criteria.name, 5) * criteria.weight
        return total

class ProsConsAnalysis:
    """优缺点分析算法"""
    
    def analyze(self, options: List[str], description: str) -> Dict[str, Any]:
        """分析每个选项的优缺点"""
        results = {}
        
        for option in options:
            pros, cons = self._extract_pros_cons(option, description)
            results[option] = {
                "pros": pros,
                "cons": cons,
                "pros_count": len(pros),
                "cons_count": len(cons),
                "balance": len(pros) - len(cons)
            }
        
        # 找出最平衡的选项
        best_option = max(results.items(), key=lambda x: x[1]["balance"])
        
        return {
            "algorithm": "Pros and Cons Analysis",
            "results": results,
            "recommendation": best_option[0],
            "reasoning": f"Based on pros/cons balance: {best_option[1]['balance']}"
        }
    
    def _extract_pros_cons(self, option: str, context: str) -> tuple:
        """提取优缺点（简化版本）"""
        pros = []
        cons = []
        
        # 基于关键词分析
        positive_keywords = ["good", "best", "now", "immediate", "save", "efficient"]
        negative_keywords = ["wait", "expensive", "risk", "delay", "costly"]
        
        option_lower = option.lower()
        
        for keyword in positive_keywords:
            if keyword in option_lower:
                pros.append(f"Indicates {keyword}")
                
        for keyword in negative_keywords:
            if keyword in option_lower:
                cons.append(f"Involves {keyword}")
        
        # 默认优缺点
        if not pros:
            pros = ["Viable option", "Worth considering"]
        if not cons:
            cons = ["Requires evaluation", "May have hidden costs"]
            
        return pros, cons

class DecisionMatrix:
    """决策矩阵算法"""
    
    def analyze(self, options: List[str], criteria: List[str] = None) -> Dict[str, Any]:
        """使用决策矩阵分析"""
        if not criteria:
            criteria = ["Cost", "Time", "Quality", "Risk", "Impact"]
        
        matrix = {}
        for option in options:
            matrix[option] = {}
            for criterion in criteria:
                # 生成评分（1-10）
                score = np.random.randint(3, 10)
                matrix[option][criterion] = score
        
        # 计算总分
        totals = {}
        for option, scores in matrix.items():
            totals[option] = sum(scores.values())
        
        best_option = max(totals.items(), key=lambda x: x[1])
        
        return {
            "algorithm": "Decision Matrix",
            "matrix": matrix,
            "totals": totals,
            "recommendation": best_option[0],
            "criteria": criteria
        }

# 主分析器
class DecisionAnalyzer:
    """综合决策分析器"""
    
    def __init__(self):
        self.weighted_score = WeightedScoreAnalysis()
        self.pros_cons = ProsConsAnalysis()
        self.decision_matrix = DecisionMatrix()
    
    def comprehensive_analysis(self, description: str, options: List[str]) -> Dict[str, Any]:
        """执行综合分析"""
        
        # 运行所有算法
        weighted_result = self.weighted_score.analyze(options, description)
        pros_cons_result = self.pros_cons.analyze(options, description)
        matrix_result = self.decision_matrix.analyze(options)
        
        # 综合推荐
        recommendations = [
            weighted_result.get("recommendation"),
            pros_cons_result.get("recommendation"),
            matrix_result.get("recommendation")
        ]
        
        # 投票机制
        from collections import Counter
        vote_counts = Counter(recommendations)
        final_recommendation = vote_counts.most_common(1)[0][0] if recommendations else options[0]
        
        return {
            "description": description,
            "options": options,
            "algorithms_used": {
                "weighted_score": weighted_result,
                "pros_cons": pros_cons_result,
                "decision_matrix": matrix_result
            },
            "final_recommendation": final_recommendation,
            "confidence": f"{(vote_counts[final_recommendation] / len(recommendations) * 100):.0f}%",
            "summary": self._generate_summary(final_recommendation, weighted_result, pros_cons_result)
        }
    
    def _generate_summary(self, recommendation: str, weighted: Dict, pros_cons: Dict) -> str:
        """生成可读的总结"""
        summary = f"Based on comprehensive analysis, '{recommendation}' is recommended.\n\n"
        
        # 添加评分信息
        if "results" in weighted and recommendation in weighted["results"]:
            score = weighted["results"][recommendation]["total_score"]
            summary += f"• Weighted Score: {score}/10\n"
        
        # 添加优缺点
        if "results" in pros_cons and recommendation in pros_cons["results"]:
            pros = pros_cons["results"][recommendation]["pros"]
            cons = pros_cons["results"][recommendation]["cons"]
            summary += f"• Pros: {len(pros)} identified\n"
            summary += f"• Cons: {len(cons)} identified\n"
        
        return summary
