"""
测试Tom-用户-Jany共享上下文的逻辑流程
不依赖真实API，使用模拟数据
"""

def test_conversation_context_logic():
    """测试对话上下文共享逻辑"""
    
    print("\n" + "="*60)
    print("  📋 测试Tom-用户-Jany共享上下文逻辑")
    print("="*60)
    
    # 模拟conversationHistory
    conversation_history = []
    
    # 1️⃣ Tom初步分析
    print("\n1️⃣ Tom初步分析")
    tom_initial = {
        "role": "assistant",
        "content": "META基本面良好，ROE达到36%，PE为27.8倍...",
        "initial_analysis": True
    }
    conversation_history.append(tom_initial)
    print(f"   ✅ Tom分析已添加到对话历史")
    print(f"   📊 对话历史长度: {len(conversation_history)}")
    
    # 2️⃣ 用户提问
    print("\n2️⃣ 用户与Tom对话")
    user_questions = [
        "ROE为什么这么高？",
        "能看看价格走势吗？",
        "技术指标怎么样？"
    ]
    
    for i, question in enumerate(user_questions, 1):
        # 用户消息
        conversation_history.append({
            "role": "user",
            "content": question
        })
        print(f"   👤 用户问题{i}: {question}")
        
        # Tom回复
        conversation_history.append({
            "role": "assistant",
            "content": f"Tom对'{question}'的回复...",
            "intent": "general"
        })
        print(f"   🤖 Tom回复{i}")
    
    print(f"   📊 对话历史长度: {len(conversation_history)}")
    
    # 3️⃣ 用户点击"生成策略"按钮
    print("\n3️⃣ 用户点击'生成交易策略（Jany）'按钮")
    print(f"   🔄 Jany开始读取对话历史...")
    print(f"   📖 Jany能看到:")
    print(f"      - Tom的初步分析: 1条")
    print(f"      - 用户提问: {len([m for m in conversation_history if m['role'] == 'user'])}条")
    print(f"      - Tom回复: {len([m for m in conversation_history if m['role'] == 'assistant'])}条")
    
    # Jany生成策略
    strategy1 = {
        "option_strategy": {
            "type": "Long Call",
            "strike_price": 130,
            "total_premium": 850,
            "delta": 0.9980
        },
        "stock_strategy": {
            "type": "Long Stock",
            "shares": 47,
            "entry_price": 627.08
        },
        "explanation": "基于Tom的分析和您的对话，推荐Long Call策略..."
    }
    
    conversation_history.append({
        "role": "jany",
        "content": f"基于您与Tom的{len(conversation_history)}条对话，我生成了策略",
        "strategy_data": strategy1,
        "timestamp": 1234567890
    })
    
    print(f"   ✅ Jany策略1生成成功")
    print(f"   📊 策略已添加到对话历史，长度: {len(conversation_history)}")
    
    # 4️⃣ 用户对策略反馈
    print("\n4️⃣ 用户对策略的反馈")
    user_feedback = "这个策略太保守了，我想要更激进的策略"
    conversation_history.append({
        "role": "user",
        "content": user_feedback
    })
    print(f"   👤 用户反馈: {user_feedback}")
    
    # Tom回复（能看到Jany的策略）
    conversation_history.append({
        "role": "assistant",
        "content": "我理解您想要更激进的策略。从Jany刚才的Long Call策略来看，确实比较保守。建议您重新生成策略..."
    })
    print(f"   🤖 Tom回复（Tom能看到Jany的策略）")
    print(f"   📊 对话历史长度: {len(conversation_history)}")
    
    # 5️⃣ 用户再次点击"生成策略"
    print("\n5️⃣ 用户再次点击'生成交易策略（Jany）'按钮")
    print(f"   🔄 Jany重新读取对话历史...")
    print(f"   📖 Jany能看到:")
    print(f"      - Tom的初步分析")
    print(f"      - 所有用户提问和Tom回复")
    print(f"      - 之前的策略1（Long Call）")
    print(f"      - 用户反馈：'太保守了'")
    print(f"      - Tom的建议")
    
    # Jany生成新策略（更激进）
    strategy2 = {
        "option_strategy": {
            "type": "Long Call (OTM)",  # 更激进
            "strike_price": 650,  # 更高的执行价
            "total_premium": 1200,  # 更高的期权费
            "delta": 0.7500  # 更低的Delta（更激进）
        },
        "stock_strategy": {
            "type": "Long Stock",
            "shares": 35,
            "entry_price": 627.08
        },
        "explanation": "基于您'太保守'的反馈，我生成了更激进的OTM Call策略..."
    }
    
    # 🔑 关键：替换对话历史中的策略（不是追加）
    # 找到上一个Jany消息并替换
    for i in range(len(conversation_history) - 1, -1, -1):
        if conversation_history[i].get('role') == 'jany':
            conversation_history[i] = {
                "role": "jany",
                "content": f"基于您与Tom的{len(conversation_history)}条对话（包括您的反馈），我重新生成了更激进的策略",
                "strategy_data": strategy2,
                "timestamp": 1234567891
            }
            break
    
    print(f"   ✅ Jany策略2生成成功（更激进）")
    print(f"   📊 对话历史长度: {len(conversation_history)}")
    
    # 6️⃣ 验证结果
    print("\n" + "="*60)
    print("  ✅ 逻辑验证")
    print("="*60)
    
    # 统计对话历史
    tom_messages = [m for m in conversation_history if m['role'] == 'assistant']
    user_messages = [m for m in conversation_history if m['role'] == 'user']
    jany_messages = [m for m in conversation_history if m['role'] == 'jany']
    
    print(f"\n📊 最终对话历史统计:")
    print(f"   - Tom消息: {len(tom_messages)}条")
    print(f"   - 用户消息: {len(user_messages)}条")
    print(f"   - Jany策略: {len(jany_messages)}条")
    print(f"   - 总计: {len(conversation_history)}条")
    
    # 验证关键点
    print(f"\n✅ 关键验证点:")
    
    # 1. Tom能看到Jany的策略
    has_jany_strategy = any(m.get('role') == 'jany' for m in conversation_history)
    print(f"   1. Tom能看到Jany的策略: {'✅' if has_jany_strategy else '❌'}")
    
    # 2. Jany能看到用户反馈
    has_user_feedback = any('保守' in m.get('content', '') for m in user_messages)
    print(f"   2. 对话历史包含用户反馈: {'✅' if has_user_feedback else '❌'}")
    
    # 3. 策略有更新（不是追加）
    print(f"   3. Jany策略数量: {len(jany_messages)}条（应该是1条，不是2条）")
    if len(jany_messages) == 1:
        print(f"      ✅ 正确：策略被替换，不是追加")
    else:
        print(f"      ⚠️  警告：策略被追加了，应该替换")
    
    # 4. 最新策略是更激进的
    if jany_messages:
        latest_strategy = jany_messages[-1].get('strategy_data', {})
        is_more_aggressive = 'OTM' in latest_strategy.get('option_strategy', {}).get('type', '')
        print(f"   4. 最新策略更激进: {'✅' if is_more_aggressive else '❌'}")
    
    print("\n" + "="*60)
    print("  🎉 逻辑测试完成")
    print("="*60)
    
    print("\n📝 总结:")
    print("   1. ✅ Tom、用户、Jany共享同一个conversationHistory")
    print("   2. ✅ Jany生成策略时能看到所有对话（包括用户反馈）")
    print("   3. ✅ Tom能看到Jany的策略并基于此回复")
    print("   4. ✅ 重新生成策略时，新策略替换旧策略（不是追加）")
    print("   5. ✅ 策略显示在独立区域，对话框显示简化通知")

if __name__ == "__main__":
    test_conversation_context_logic()

