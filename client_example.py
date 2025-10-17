#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python客户端调用示例
"""

import requests
import json

API_URL = "https://decision-assistant-backend.onrender.com"


class DecisionAssistantClient:
    """决策助手客户端"""
    
    def __init__(self, api_url=API_URL):
        self.api_url = api_url
    
    def list_algorithms(self):
        """获取所有可用算法"""
        response = requests.get(f"{self.api_url}/api/algorithms/list")
        return response.json()
    
    def analyze(self, algorithm_id, question, options, criteria=None):
        """
        使用指定算法分析
        
        参数:
            algorithm_id: 算法ID ('weighted_scoring' 或 'pros_cons')
            question: 决策问题
            options: 选项列表
            criteria: 评估标准（可选）
        
        返回:
            分析结果
        """
        data = {
            "algorithm_id": algorithm_id,
            "question": question,
            "options": options
        }
        
        if criteria:
            data["criteria"] = criteria
        
        response = requests.post(
            f"{self.api_url}/api/algorithms/analyze",
            json=data
        )
        return response.json()
    
    def compare_algorithms(self, question, options, algorithms=None):
        """
        使用多个算法对比分析
        
        参数:
            question: 决策问题
            options: 选项列表
            algorithms: 算法ID列表（可选，默认使用所有）
        """
        if algorithms is None:
            algorithms = ['weighted_scoring', 'pros_cons']
        
        data = {
            "question": question,
            "options": options,
            "algorithms": algorithms
        }
        
        response = requests.post(
            f"{self.api_url}/api/algorithms/compare",
            json=data
        )
        return response.json()


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建客户端
    client = DecisionAssistantClient()
    
    print("=" * 80)
    print("🎯 决策助手客户端示例")
    print("=" * 80)
    
    # 示例1: 列出所有算法
    print("\n1. 获取可用算法...")
    result = client.list_algorithms()
    if result['status'] == 'success':
        print(f"   可用算法数: {result['total']}")
        for algo in result['algorithms']:
            print(f"   - {algo['id']}: {algo['name']}")
    
    # 示例2: 加权评分法 - 选择笔记本电脑
    print("\n2. 使用加权评分法分析...")
    options = [
        {"name": "MacBook Pro", "价格": 7, "性能": 10, "便携性": 8, "续航": 9},
        {"name": "ThinkPad X1", "价格": 8, "性能": 8, "便携性": 9, "续航": 8},
        {"name": "Dell XPS 13", "价格": 9, "性能": 7, "便携性": 10, "续航": 7}
    ]
    
    result = client.analyze(
        algorithm_id="weighted_scoring",
        question="选择哪款笔记本电脑？",
        options=options
    )
    
    if result['status'] == 'success':
        res = result['result']
        print(f"   推荐: {res['recommendation']}")
        print(f"   得分:")
        for option, score in res['scores'].items():
            print(f"     - {option}: {score:.2f}")
    
    # 示例3: 优劣势分析法 - 工作选择
    print("\n3. 使用优劣势分析法...")
    options = [
        {
            "name": "远程工作",
            "pros": ["灵活的工作时间", "节省通勤时间", "舒适的工作环境"],
            "cons": ["社交机会减少", "沟通成本增加"]
        },
        {
            "name": "办公室工作",
            "pros": ["面对面沟通", "团队协作更容易"],
            "cons": ["通勤时间长", "固定的工作时间", "办公环境噪音"]
        }
    ]
    
    result = client.analyze(
        algorithm_id="pros_cons",
        question="选择工作方式",
        options=options
    )
    
    if result['status'] == 'success':
        res = result['result']
        print(f"   推荐: {res['recommendation']}")
        print(f"   净得分:")
        for option, score in res['scores'].items():
            print(f"     - {option}: {score}")
    
    # 示例4: 对比多个算法
    print("\n4. 对比多个算法...")
    options = [
        {"name": "股票", "收益": 9, "风险": 8, "流动性": 10},
        {"name": "房产", "收益": 7, "风险": 5, "流动性": 3},
        {"name": "基金", "收益": 8, "风险": 6, "流动性": 8}
    ]
    
    result = client.compare_algorithms(
        question="选择投资方案",
        options=options,
        algorithms=['weighted_scoring']
    )
    
    if result['status'] == 'success':
        print(f"   对比了 {len(result['results'])} 个算法:")
        for algo_id, res in result['results'].items():
            if 'error' not in res:
                print(f"     - {algo_id}: 推荐 {res['recommendation']}")
    
    print("\n" + "=" * 80)
    print("✅ 示例完成！")
    print("=" * 80)

