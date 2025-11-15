"""检查 ML 数据完整性"""
import psycopg2
import pandas as pd

DATABASE_URL = 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l'

def check_ml_data():
    print("="*80)
    print("🔍 检查 ML 数据完整性")
    print("="*80)
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # 1. 检查视图是否存在
    print("\n1️⃣ 检查 ml_training_data 视图...")
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.views 
            WHERE table_name = 'ml_training_data'
        )
    """)
    view_exists = cur.fetchone()[0]
    print(f"   视图存在: {'✅' if view_exists else '❌'}")
    
    if not view_exists:
        print("   ❌ 视图不存在！需要运行 setup_ml_database.py")
        return False
    
    # 2. 检查视图数据
    print("\n2️⃣ 检查视图数据...")
    try:
        df = pd.read_sql("SELECT * FROM ml_training_data LIMIT 5", conn)
        print(f"   ✅ 视图可查询，列数: {len(df.columns)}")
        print(f"   列名: {list(df.columns)}")
        print(f"   总行数: ", end="")
        cur.execute("SELECT COUNT(*) FROM ml_training_data")
        total = cur.fetchone()[0]
        print(f"{total}")
    except Exception as e:
        print(f"   ❌ 查询失败: {e}")
        return False
    
    # 3. 检查关键字段
    print("\n3️⃣ 检查关键字段...")
    required_fields = ['user_choice', 'optimal_choice', 'current_price', 'volatility', 
                       'rsi', 'available_cash', 'actual_return', 'user_id']
    
    for field in required_fields:
        if field in df.columns:
            null_count = df[field].isnull().sum()
            print(f"   ✅ {field}: 存在 (空值: {null_count})")
        else:
            print(f"   ❌ {field}: 不存在！")
    
    # 4. 检查用户数据
    print("\n4️⃣ 检查各用户数据量...")
    cur.execute("""
        SELECT u.username, COUNT(*) as count
        FROM ml_training_data m
        JOIN users u ON m.user_id = u.id
        GROUP BY u.username
        ORDER BY count DESC
        LIMIT 10
    """)
    
    users = cur.fetchall()
    if users:
        for username, count in users:
            print(f"   {username}: {count} 条")
    else:
        print("   ⚠️ 没有任何用户数据")
    
    # 5. 检查 positions 表
    print("\n5️⃣ 检查 positions 表...")
    cur.execute("SELECT COUNT(*) FROM positions WHERE status = 'CLOSED'")
    closed_count = cur.fetchone()[0]
    print(f"   已平仓: {closed_count} 条")
    
    cur.execute("SELECT COUNT(*) FROM positions WHERE status != 'CLOSED'")
    open_count = cur.fetchone()[0]
    print(f"   未平仓: {open_count} 条")
    
    # 6. 检查 strategies 表
    print("\n6️⃣ 检查 strategies 表...")
    cur.execute("SELECT COUNT(*) FROM strategies")
    strategy_count = cur.fetchone()[0]
    print(f"   策略数: {strategy_count} 条")
    
    # 7. 检查 user_profiles 表结构
    print("\n7️⃣ 检查 user_profiles 表结构...")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'user_profiles'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    print(f"   字段数: {len(columns)}")
    for col_name, col_type in columns:
        print(f"   - {col_name}: {col_type}")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*80)
    print("✅ 检查完成")
    print("="*80)
    
    return True

if __name__ == "__main__":
    try:
        check_ml_data()
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

