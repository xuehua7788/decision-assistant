"""
测试 Tom API 完整调用链路
"""
import requests
import json

# API_URL = "http://localhost:10000"
API_URL = "https://decision-assistant-backend.onrender.com"

def test_tom_api_chain():
    print("="*80)
    print("🔍 测试 Tom API 完整调用链路")
    print("="*80)
    
    username = "bbb"
    
    # ===== 步骤 1: 训练模型 =====
    print(f"\n【步骤 1】训练决策树模型...")
    try:
        response = requests.post(
            f"{API_URL}/api/ml/decision-tree/train",
            json={},
            timeout=60
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 训练成功")
            print(f"   样本数: {data.get('training_samples', 0)}")
            print(f"   准确率: {data.get('accuracy', 0):.2%}")
        else:
            print(f"   ❌ 训练失败")
            print(f"   响应: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return False
    
    # ===== 步骤 2: Tom 分析 =====
    print(f"\n【步骤 2】调用 Tom 分析 API...")
    try:
        response = requests.post(
            f"{API_URL}/api/ml/tom-analyze",
            json={
                "username": username,
                "model_type": "decision_tree"
            },
            timeout=60
        )
        
        print(f"   状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Tom 分析成功")
            print(f"\n   返回的数据结构:")
            print(f"   - success: {data.get('success')}")
            print(f"   - model_version: {data.get('model_version')}")
            print(f"   - summary: {type(data.get('summary'))}")
            print(f"   - tom_analysis: {len(data.get('tom_analysis', ''))} 字符")
            
            if data.get('summary'):
                summary = data['summary']
                print(f"\n   Summary 内容:")
                print(f"   - total_samples: {summary.get('total_samples')}")
                print(f"   - accuracy: {summary.get('accuracy')}")
                print(f"   - choice_distribution: {summary.get('choice_distribution')}")
                print(f"   - average_returns: {summary.get('average_returns')}")
                print(f"   - top_features 数量: {len(summary.get('top_features', []))}")
            
            if data.get('tom_analysis'):
                print(f"\n   Tom 分析内容（前200字）:")
                print(f"   {data['tom_analysis'][:200]}...")
                
        else:
            print(f"   ❌ Tom 分析失败")
            print(f"   响应: {response.text[:1000]}")
            return False
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ===== 步骤 3: 检查 Profile API =====
    print(f"\n【步骤 3】检查 Profile API...")
    try:
        response = requests.get(
            f"{API_URL}/api/profile/{username}",
            timeout=30
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profile 获取成功")
            
            profile = data.get('profile', {})
            print(f"\n   Profile 数据结构:")
            print(f"   - risk_tolerance: {profile.get('risk_tolerance')}")
            print(f"   - investment_style: {profile.get('investment_style')}")
            print(f"   - ai_analysis: {type(profile.get('ai_analysis'))}")
            print(f"   - analysis_summary: {len(profile.get('analysis_summary', ''))} 字符")
            
            if profile.get('ai_analysis'):
                ai_analysis = profile['ai_analysis']
                if isinstance(ai_analysis, str):
                    ai_analysis = json.loads(ai_analysis)
                
                print(f"\n   ai_analysis 内容:")
                print(f"   - source: {ai_analysis.get('source')}")
                print(f"   - option_preference_pct: {ai_analysis.get('option_preference_pct')}")
                print(f"   - avg_option_return: {ai_analysis.get('avg_option_return')}")
                print(f"   - avg_stock_return: {ai_analysis.get('avg_stock_return')}")
                
            if profile.get('analysis_summary'):
                print(f"\n   analysis_summary（前200字）:")
                print(f"   {profile['analysis_summary'][:200]}...")
                
        else:
            print(f"   ❌ Profile 获取失败")
            print(f"   响应: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        return False
    
    print("\n" + "="*80)
    print("✅ 完整链路测试通过")
    print("="*80)
    
    return True

if __name__ == "__main__":
    try:
        success = test_tom_api_chain()
        if not success:
            print("\n❌ 测试失败，请检查上述错误")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

