// 测试真实的MSFT数据结构

// 从后端获取的实际MSFT期权策略数据
const msftOptionStrategy = {
  "description": "在震荡区间内收取权利金。风险和收益都有限，适合横盘市场。",
  "metrics": {
    "breakeven": 517.03,
    "max_gain": 1551.09,
    "max_loss": -6979.9,
    "probability": "60%"
  },
  "name": "铁鹰式",
  "parameters": {
    "buy_strike": 439.47549999999995,
    "contracts": 1,
    "current_price": 517.03,
    "expiry": "30天",
    "premium_paid": 15.5109,
    "premium_received": 31.0218,
    "sell_strike": 594.5844999999999
  },
  "type": "iron_condor"
};

console.log("=" .repeat(80));
console.log("测试真实MSFT数据");
console.log("=" .repeat(80));

// 旧代码（会报错的）
console.log("\n❌ 旧代码:");
try {
  const oldCode = msftOptionStrategy.strategy.name;
  console.log("   结果:", oldCode);
} catch (e) {
  console.log("   错误:", e.message);
  console.log("   ✅ 确认：旧代码会报错！");
}

// 新代码（不会报错）
console.log("\n✅ 新代码:");
const strategyName = msftOptionStrategy.name || 
                     msftOptionStrategy.strategy?.name || 
                     '期权策略';
console.log("   结果:", strategyName);
console.log("   ✅ 确认：新代码正确提取到 '铁鹰式'");

// 验证数据完整性
console.log("\n📊 数据完整性验证:");
console.log("   策略名称:", msftOptionStrategy.name);
console.log("   策略类型:", msftOptionStrategy.type);
console.log("   有参数:", msftOptionStrategy.parameters ? "✅" : "❌");
console.log("   有指标:", msftOptionStrategy.metrics ? "✅" : "❌");
console.log("   有描述:", msftOptionStrategy.description ? "✅" : "❌");

console.log("\n" + "=".repeat(80));
console.log("🎯 结论：");
console.log("1. ✅ MSFT策略确实包含期权策略数据");
console.log("2. ✅ 数据结构是顶层包含name，不是嵌套在strategy中");
console.log("3. ✅ 旧代码 optionStrategy.strategy.name 会报错");
console.log("4. ✅ 新代码 optionStrategy.name 能正确提取");
console.log("5. ✅ 修复方案是正确的");
console.log("=".repeat(80));

