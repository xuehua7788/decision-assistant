"""
测试 ML 分析完整集成流程
"""
import requests
import json

API_URL = "https://decision-assistant-backend.onrender.com"
# API_URL = "http://localhost:10000"  # 本地测试

def test_ml_integration():
    """测试 ML 分析 → 更新画像 → 聊天记录 → Profile显示"""
    
    print("="*60)
    print("🧪 测试 ML 分析完整集成流程")
    print("="*60)
    
    username = "alice"  # 使用已有数据的用户
    
    # 1. 训练模型
    print("\n1️⃣ 训练决策树模型...")
    response = requests.post(
        f"{API_URL}/api/ml/decision-tree/train",
        json={},
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 模型训练成功")
        print(f"   📊 样本数: {data.get('training_samples', 0)}")
        print(f"   🎯 准确率: {data.get('accuracy', 0):.2%}")
    else:
        print(f"   ❌ 训练失败: {response.status_code}")
        print(f"   {response.text}")
        return False
    
    # 2. Tom 分析
    print("\n2️⃣ 让 Tom 分析交易行为...")
    response = requests.post(
        f"{API_URL}/api/ml/tom-analyze",
        json={
            "username": username,
            "model_type": "decision_tree"
        },
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Tom 分析成功")
        print(f"   📝 分析长度: {len(data.get('tom_analysis', ''))} 字符")
        print(f"\n   Tom 的分析摘要:")
        print(f"   {data.get('tom_analysis', '')[:200]}...")
    else:
        print(f"   ❌ 分析失败: {response.status_code}")
        print(f"   {response.text}")
        return False
    
    # 3. 检查用户画像是否更新
    print("\n3️⃣ 检查用户画像是否更新...")
    response = requests.get(f"{API_URL}/api/profile/{username}")
    
    if response.status_code == 200:
        data = response.json()
        profile = data.get('profile', {})
        
        if profile.get('ai_analysis'):
            ai_analysis = profile['ai_analysis']
            if isinstance(ai_analysis, str):
                ai_analysis = json.loads(ai_analysis)
            
            print(f"   ✅ 用户画像已更新")
            print(f"   🎯 数据来源: {ai_analysis.get('source')}")
            print(f"   📊 风险偏好: {profile.get('risk_tolerance')}")
            print(f"   💼 投资风格: {profile.get('investment_style')}")
            print(f"   📈 期权偏好: {ai_analysis.get('option_preference_pct', 0):.1f}%")
            print(f"   💰 期权收益: {ai_analysis.get('avg_option_return', 0):.2%}")
            print(f"   📉 股票收益: {ai_analysis.get('avg_stock_return', 0):.2%}")
            
            if ai_analysis.get('source') != 'ml_analysis':
                print(f"   ⚠️ 数据来源不是 ml_analysis，可能是旧数据")
        else:
            print(f"   ⚠️ 用户画像未更新（ai_analysis 为空）")
    else:
        print(f"   ❌ 获取画像失败: {response.status_code}")
    
    # 4. 检查聊天记录（需要数据库直接查询，这里跳过）
    print("\n4️⃣ 聊天记录检查...")
    print("   ℹ️ 需要直接查询数据库，请手动检查 chat_messages 表")
    print(f"   查询: SELECT * FROM chat_messages WHERE content LIKE '%交易行为分析%' ORDER BY created_at DESC LIMIT 2;")
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)
    
    return True


if __name__ == "__main__":
    try:
        test_ml_integration()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

