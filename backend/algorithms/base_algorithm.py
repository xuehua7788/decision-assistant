#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础算法接口 - 所有决策分析算法的基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseAlgorithm(ABC):
    """决策分析算法基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.description = ""
    
    @abstractmethod
    def analyze(self, question: str, options: List[Dict[str, Any]], criteria: List[str] = None) -> Dict[str, Any]:
        """
        分析决策问题
        
        参数:
            question: 决策问题描述
            options: 选项列表，每个选项是一个字典
            criteria: 评估标准列表（可选）
        
        返回:
            分析结果字典，包含:
            - recommendation: 推荐的选项
            - scores: 各选项得分
            - analysis: 详细分析
            - summary: 总结
        """
        pass
    
    def get_info(self) -> Dict[str, str]:
        """获取算法信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description
        }
    
    def validate_input(self, options: List[Dict[str, Any]]) -> bool:
        """验证输入数据"""
        if not options or len(options) < 2:
            raise ValueError("至少需要2个选项进行比较")
        return True

