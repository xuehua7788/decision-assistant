"""
全链路测试：用户 bbb 的 ML 分析
"""
import psycopg2
import pandas as pd
import json

DATABASE_URL = 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l'

def test_bbb_fullchain():
    print("="*80)
    print("🔍 全链路测试：用户 bbb 的 ML 分析")
    print("="*80)
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    username = "bbb"
    
    # ===== 步骤 1: 检查用户是否存在 =====
    print(f"\n【步骤 1】检查用户 {username} 是否存在...")
    cur.execute("SELECT id, username FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    
    if not user:
        print(f"   ❌ 用户 {username} 不存在！")
        cur.close()
        conn.close()
        return False
    
    user_id = user[0]
    print(f"   ✅ 用户存在: ID={user_id}, username={user[1]}")
    
    # ===== 步骤 2: 检查 ml_training_data 视图 =====
    print(f"\n【步骤 2】检查 ml_training_data 视图...")
    try:
        cur.execute("""
            SELECT COUNT(*) 
            FROM ml_training_data 
            WHERE user_id = %s
        """, (user_id,))
        count = cur.fetchone()[0]
        print(f"   ✅ 视图查询成功: {username} 有 {count} 条数据")
    except Exception as e:
        print(f"   ❌ 视图查询失败: {e}")
        cur.close()
        conn.close()
        return False
    
    # ===== 步骤 3: 获取训练数据 =====
    print(f"\n【步骤 3】获取 {username} 的训练数据...")
    try:
        query = """
            SELECT * FROM ml_training_data
            WHERE user_choice IS NOT NULL
            AND user_id = %s
            ORDER BY decision_time DESC
        """
        df = pd.read_sql(query, conn, params=(user_id,))
        print(f"   ✅ 数据获取成功: {len(df)} 条")
        
        if len(df) > 0:
            print(f"\n   数据样本（前3条）:")
            print(f"   列名: {list(df.columns)}")
            print(f"\n   user_choice 分布:")
            print(df['user_choice'].value_counts())
            print(f"\n   actual_return 统计:")
            print(df['actual_return'].describe())
        else:
            print(f"   ⚠️ {username} 没有训练数据")
    except Exception as e:
        print(f"   ❌ 数据获取失败: {e}")
        import traceback
        traceback.print_exc()
        cur.close()
        conn.close()
        return False
    
    # ===== 步骤 4: 检查数据是否需要生成 =====
    MIN_SAMPLES = 20
    print(f"\n【步骤 4】检查数据量（最少需要 {MIN_SAMPLES} 条）...")
    
    if len(df) < MIN_SAMPLES:
        print(f"   ⚠️ 数据不足: {len(df)} < {MIN_SAMPLES}")
        print(f"   需要生成 {MIN_SAMPLES - len(df)} 条模拟数据")
        
        # 检查 strategies 表
        cur.execute("SELECT COUNT(*) FROM strategies")
        strategy_count = cur.fetchone()[0]
        print(f"   strategies 表有 {strategy_count} 条数据")
        
        if strategy_count == 0:
            print(f"   ⚠️ strategies 表为空，需要先生成策略")
    else:
        print(f"   ✅ 数据充足: {len(df)} >= {MIN_SAMPLES}")
    
    # ===== 步骤 5: 特征工程 =====
    print(f"\n【步骤 5】特征工程...")
    
    if len(df) >= 5:
        try:
            from ml_feature_extraction import prepare_features_for_decision_tree
            
            X, y, feature_names = prepare_features_for_decision_tree(df)
            print(f"   ✅ 特征准备成功")
            print(f"   特征数量: {X.shape[1]}")
            print(f"   样本数量: {X.shape[0]}")
            print(f"   特征名称: {feature_names}")
            print(f"   目标变量分布: {pd.Series(y).value_counts().to_dict()}")
        except Exception as e:
            print(f"   ❌ 特征工程失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"   ⚠️ 数据太少（{len(df)} < 5），跳过特征工程")
    
    # ===== 步骤 6: 模型训练 =====
    print(f"\n【步骤 6】模型训练...")
    
    if len(df) >= 5:
        try:
            from ml_decision_tree import DecisionTreeModel
            
            user_model = DecisionTreeModel(max_depth=5, min_samples_split=2, min_samples_leaf=1)
            performance = user_model.train(X, y, test_size=0.2)
            
            print(f"   ✅ 模型训练成功")
            print(f"   准确率: {performance['accuracy']:.2%}")
            print(f"   F1分数: {performance['f1_score']:.2%}")
            print(f"   特征重要性（Top 5）:")
            
            top_features = sorted(
                performance['feature_importance'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            for name, importance in top_features:
                print(f"     - {name}: {importance:.2%}")
                
        except Exception as e:
            print(f"   ❌ 模型训练失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"   ⚠️ 数据太少，跳过模型训练")
    
    # ===== 步骤 7: 统计分析 =====
    print(f"\n【步骤 7】统计分析...")
    
    if len(df) > 0:
        choice_counts = df['user_choice'].value_counts()
        option_count = int(choice_counts.get(1, 0))
        stock_count = int(choice_counts.get(2, 0))
        
        option_df = df[df['user_choice'] == 1]
        stock_df = df[df['user_choice'] == 2]
        
        option_return = float(option_df['actual_return'].mean()) if len(option_df) > 0 else 0.0
        stock_return = float(stock_df['actual_return'].mean()) if len(stock_df) > 0 else 0.0
        
        print(f"   ✅ 统计完成")
        print(f"   期权交易: {option_count} 次 ({option_count/len(df)*100:.1f}%)")
        print(f"   股票交易: {stock_count} 次 ({stock_count/len(df)*100:.1f}%)")
        print(f"   期权平均收益: {option_return:.2%}")
        print(f"   股票平均收益: {stock_return:.2%}")
    
    # ===== 步骤 8: 检查 user_profiles 表 =====
    print(f"\n【步骤 8】检查 user_profiles 表...")
    cur.execute("""
        SELECT 
            username,
            risk_tolerance,
            investment_style,
            ai_analysis,
            analysis_summary,
            last_analyzed_at
        FROM user_profiles
        WHERE username = %s
    """, (username,))
    
    profile = cur.fetchone()
    if profile:
        print(f"   ✅ 用户画像存在")
        print(f"   风险偏好: {profile[1]}")
        print(f"   投资风格: {profile[2]}")
        print(f"   ai_analysis: {'有数据' if profile[3] else '无数据'}")
        print(f"   analysis_summary: {'有数据' if profile[4] else '无数据'}")
        print(f"   最后分析: {profile[5]}")
        
        if profile[3]:
            ai_analysis = json.loads(profile[3]) if isinstance(profile[3], str) else profile[3]
            print(f"   数据来源: {ai_analysis.get('source', 'unknown')}")
    else:
        print(f"   ⚠️ 用户画像不存在")
    
    # ===== 步骤 9: 检查 chat_sessions =====
    print(f"\n【步骤 9】检查 chat_sessions...")
    cur.execute("""
        SELECT cs.id, cs.session_id, cs.created_at
        FROM chat_sessions cs
        WHERE cs.user_id = %s
        ORDER BY cs.created_at DESC
        LIMIT 1
    """, (user_id,))
    
    session = cur.fetchone()
    if session:
        session_pk = session[0]
        print(f"   ✅ Session 存在: ID={session_pk}, session_id={session[1]}")
        
        # 检查消息
        cur.execute("""
            SELECT role, LEFT(content, 100), created_at
            FROM chat_messages
            WHERE session_id = %s
            ORDER BY created_at DESC
            LIMIT 5
        """, (session_pk,))
        
        messages = cur.fetchall()
        print(f"   消息数: {len(messages)}")
        if messages:
            print(f"   最近消息:")
            for role, content, created_at in messages:
                print(f"     [{role}] {content}... ({created_at})")
    else:
        print(f"   ⚠️ 没有 session")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*80)
    print("✅ 全链路测试完成")
    print("="*80)
    
    return True

if __name__ == "__main__":
    try:
        test_bbb_fullchain()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

