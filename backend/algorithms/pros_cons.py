#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优劣势分析法 (Pros and Cons)
"""

from typing import Dict, List, Any
from .base_algorithm import BaseAlgorithm


class ProsConsAlgorithm(BaseAlgorithm):
    """优劣势分析算法"""
    
    def __init__(self):
        super().__init__(name="优劣势分析法", version="1.0.0")
        self.description = "列举每个选项的优势和劣势，帮助全面评估"
    
    def analyze(self, question: str, options: List[Dict[str, Any]], criteria: List[str] = None) -> Dict[str, Any]:
        """
        优劣势分析
        
        示例输入:
        options = [
            {
                "name": "选项A",
                "pros": ["优势1", "优势2"],
                "cons": ["劣势1"]
            }
        ]
        """
        self.validate_input(options)
        
        analysis_results = {}
        scores = {}
        
        for option in options:
            option_name = option.get('name', str(option))
            pros = option.get('pros', [])
            cons = option.get('cons', [])
            
            # 简单评分：优势-劣势
            score = len(pros) - len(cons)
            scores[option_name] = score
            
            analysis_results[option_name] = {
                "pros": pros,
                "cons": cons,
                "pros_count": len(pros),
                "cons_count": len(cons),
                "net_score": score
            }
        
        # 推荐得分最高的
        best_option = max(scores, key=scores.get)
        
        # 生成分析
        analysis = self._generate_analysis(analysis_results)
        
        return {
            "recommendation": best_option,
            "scores": scores,
            "analysis_details": analysis_results,
            "analysis": analysis,
            "summary": f"基于优劣势分析，推荐选择 '{best_option}'。该选项有 {analysis_results[best_option]['pros_count']} 个优势和 {analysis_results[best_option]['cons_count']} 个劣势，净得分为 {scores[best_option]}。",
            "algorithm": self.get_info()
        }
    
    def _generate_analysis(self, results: Dict[str, Dict]) -> str:
        """生成分析报告"""
        analysis = "## 优劣势对比分析\n\n"
        
        for option, data in results.items():
            analysis += f"### {option}\n"
            analysis += f"**净得分**: {data['net_score']} (优势 {data['pros_count']} - 劣势 {data['cons_count']})\n\n"
            
            if data['pros']:
                analysis += "**优势**:\n"
                for i, pro in enumerate(data['pros'], 1):
                    analysis += f"{i}. ✅ {pro}\n"
                analysis += "\n"
            
            if data['cons']:
                analysis += "**劣势**:\n"
                for i, con in enumerate(data['cons'], 1):
                    analysis += f"{i}. ❌ {con}\n"
                analysis += "\n"
        
        return analysis

