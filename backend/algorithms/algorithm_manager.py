#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算法管理器 - 统一管理所有决策分析算法
"""

from typing import Dict, List, Any, Optional
from .base_algorithm import BaseAlgorithm
from .weighted_scoring import WeightedScoringAlgorithm
from .pros_cons import ProsConsAlgorithm


class AlgorithmManager:
    """算法管理器 - 单例模式"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._algorithms: Dict[str, BaseAlgorithm] = {}
        self._register_default_algorithms()
        self._initialized = True
    
    def _register_default_algorithms(self):
        """注册默认算法"""
        self.register_algorithm("weighted_scoring", WeightedScoringAlgorithm())
        self.register_algorithm("pros_cons", ProsConsAlgorithm())
    
    def register_algorithm(self, algorithm_id: str, algorithm: BaseAlgorithm):
        """
        注册新算法
        
        参数:
            algorithm_id: 算法唯一标识
            algorithm: 算法实例
        """
        if not isinstance(algorithm, BaseAlgorithm):
            raise TypeError("算法必须继承自 BaseAlgorithm")
        
        self._algorithms[algorithm_id] = algorithm
        print(f"✅ 注册算法: {algorithm_id} - {algorithm.name}")
    
    def get_algorithm(self, algorithm_id: str) -> Optional[BaseAlgorithm]:
        """获取指定算法"""
        return self._algorithms.get(algorithm_id)
    
    def list_algorithms(self) -> List[Dict[str, str]]:
        """列出所有可用算法"""
        return [
            {
                "id": algo_id,
                **algorithm.get_info()
            }
            for algo_id, algorithm in self._algorithms.items()
        ]
    
    def analyze(self, algorithm_id: str, question: str, options: List[Dict[str, Any]], 
                criteria: List[str] = None) -> Dict[str, Any]:
        """
        使用指定算法进行分析
        
        参数:
            algorithm_id: 算法ID
            question: 决策问题
            options: 选项列表
            criteria: 评估标准（可选）
        
        返回:
            分析结果
        """
        algorithm = self.get_algorithm(algorithm_id)
        
        if not algorithm:
            raise ValueError(f"未找到算法: {algorithm_id}")
        
        try:
            result = algorithm.analyze(question, options, criteria)
            result['algorithm_id'] = algorithm_id
            return result
        except Exception as e:
            return {
                "error": str(e),
                "algorithm_id": algorithm_id
            }


# 全局单例
_manager = None

def get_algorithm_manager() -> AlgorithmManager:
    """获取算法管理器单例"""
    global _manager
    if _manager is None:
        _manager = AlgorithmManager()
    return _manager

