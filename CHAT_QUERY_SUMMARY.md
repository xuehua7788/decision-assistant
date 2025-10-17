# 🔍 查看用户聊天记录 - 快速指南

## 📋 **方法1: 快速列表 (推荐)**

### **查看所有用户和会话**
```bash
python list_users.py
```

**输出：**
- ✅ 所有用户列表
- ✅ 所有会话ID
- ✅ 每个会话的消息数和首条消息预览

---

## 📝 **方法2: 查看详细对话**

### **查看特定会话的完整内容**
```bash
python quick_view_chat.py <session_id>
```

**示例：**
```bash
# 查看test会话
python quick_view_chat.py test

# 查看UUID会话
python quick_view_chat.py 4e37bb85-c3a6-4eaf-9ec7-b81ce6ca5d5f
```

**输出：**
- ✅ 完整的对话内容
- ✅ 每条消息的时间戳
- ✅ 用户和AI的所有交互

---

## 🌐 **方法3: 直接使用API**

### **查看所有会话**
```bash
curl https://decision-assistant-backend.onrender.com/api/admin/chats
```

### **查看所有用户**
```bash
curl https://decision-assistant-backend.onrender.com/api/admin/users
```

### **查看特定用户的聊天**
```bash
curl https://decision-assistant-backend.onrender.com/api/admin/chats/<username>
```

---

## 💻 **Python示例**

```python
import requests

# 1. 获取所有会话
r = requests.get('https://decision-assistant-backend.onrender.com/api/admin/chats')
chats = r.json()

# 2. 查看每个会话
for session_id, info in chats['chats'].items():
    print(f"会话: {session_id}")
    print(f"消息数: {info['total_messages']}")
    
    # 3. 查看消息内容
    for msg in info['last_messages']:
        if 'role' in msg:
            print(f"  {msg['role']}: {msg['content'][:50]}...")
```

---

## 📊 **当前数据统计**

运行 `python list_users.py` 可以看到：

```
👥 所有用户: 1
💬 所有聊天会话: 5

会话列表:
  - test (2条消息)
  - 4e37bb85-c3a6-4eaf-9ec7-b81ce6ca5d5f (2条消息)
  - 57e56767-4088-4d2a-9206-64ad27232b15 (8条消息)
  - 5cc3fa14-db83-4efc-8952-299ddcf71ad2 (2条消息)
  - test-session-123 (2条消息)
```

---

## 🛠️ **工具文件**

| 文件 | 用途 |
|------|------|
| `list_users.py` | 列出所有用户和会话概览 |
| `quick_view_chat.py` | 查看特定会话的详细内容 |
| `view_user_chat.py` | 交互式查看工具 (带菜单) |

---

## ✨ **最佳实践**

1. **日常查看**: 使用 `list_users.py` 快速浏览
2. **详细分析**: 使用 `quick_view_chat.py <session_id>` 查看完整对话
3. **自动化**: 使用API集成到监控系统
4. **备份**: 定期备份 `chat_data/` 目录

---

## 🔒 **安全提示**

⚠️ Admin API目前**没有认证**，建议添加：
- API密钥验证
- IP白名单
- 访问日志

---

**快速开始**: `python list_users.py`

