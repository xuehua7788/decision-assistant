#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加权评分法 - 最常用的决策分析算法
"""

from typing import Dict, List, Any
from .base_algorithm import BaseAlgorithm


class WeightedScoringAlgorithm(BaseAlgorithm):
    """加权评分算法"""
    
    def __init__(self):
        super().__init__(name="加权评分法", version="1.0.0")
        self.description = "基于多个标准对选项进行加权评分，计算综合得分"
    
    def analyze(self, question: str, options: List[Dict[str, Any]], criteria: List[str] = None) -> Dict[str, Any]:
        """
        使用加权评分法分析决策
        
        示例输入:
        options = [
            {"name": "选项A", "价格": 8, "性能": 9, "外观": 7},
            {"name": "选项B", "价格": 9, "性能": 7, "外观": 8}
        ]
        criteria = ["价格", "性能", "外观"]
        """
        self.validate_input(options)
        
        # 自动提取标准（如果未提供）
        if not criteria:
            criteria = self._extract_criteria(options)
        
        # 默认权重（平均分配）
        weights = {criterion: 1.0 / len(criteria) for criterion in criteria}
        
        # 计算每个选项的加权得分
        scores = {}
        detailed_scores = {}
        
        for option in options:
            option_name = option.get('name', str(option))
            total_score = 0
            detail = {}
            
            for criterion in criteria:
                if criterion in option and criterion != 'name':
                    score = float(option[criterion])
                    weighted_score = score * weights[criterion]
                    total_score += weighted_score
                    detail[criterion] = {
                        "score": score,
                        "weight": weights[criterion],
                        "weighted_score": weighted_score
                    }
            
            scores[option_name] = total_score
            detailed_scores[option_name] = detail
        
        # 找出最佳选项
        best_option = max(scores, key=scores.get)
        
        # 生成分析报告
        analysis = self._generate_analysis(scores, detailed_scores, criteria)
        
        return {
            "recommendation": best_option,
            "scores": scores,
            "detailed_scores": detailed_scores,
            "analysis": analysis,
            "summary": f"基于加权评分分析，推荐选择 '{best_option}'。该选项的综合得分为 {scores[best_option]:.2f}，在 {len(criteria)} 个评估标准中表现最优。",
            "algorithm": self.get_info()
        }
    
    def _extract_criteria(self, options: List[Dict[str, Any]]) -> List[str]:
        """自动提取评估标准"""
        criteria = set()
        for option in options:
            for key in option.keys():
                if key != 'name' and isinstance(option[key], (int, float)):
                    criteria.add(key)
        return list(criteria)
    
    def _generate_analysis(self, scores: Dict[str, float], detailed_scores: Dict[str, Dict], criteria: List[str]) -> str:
        """生成详细分析报告"""
        analysis = "## 加权评分分析\n\n"
        
        # 排序
        sorted_options = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        analysis += "### 综合得分排名:\n"
        for i, (option, score) in enumerate(sorted_options, 1):
            analysis += f"{i}. **{option}**: {score:.2f}分\n"
        
        analysis += "\n### 各项指标详情:\n"
        for option, details in detailed_scores.items():
            analysis += f"\n**{option}**:\n"
            for criterion, data in details.items():
                analysis += f"  - {criterion}: {data['score']:.1f} (权重 {data['weight']:.2%}) = {data['weighted_score']:.2f}\n"
        
        return analysis

