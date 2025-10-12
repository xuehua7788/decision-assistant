import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class ChatStorage:
    def __init__(self, storage_dir: str = "chat_data"):
        """初始化聊天存储"""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """添加消息到会话"""
        file_path = self.storage_dir / f"{session_id}.json"
        
        # 读取现有数据或创建新数据
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "messages": []
            }
        
        # 添加新消息
        data["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 更新最后活动时间
        data["last_activity"] = datetime.now().isoformat()
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话数据"""
        file_path = self.storage_dir / f"{session_id}.json"
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_all_sessions(self) -> List[Dict]:
        """获取所有会话摘要"""
        sessions = []
        
        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 创建摘要
                    summary = {
                        "session_id": data.get("session_id"),
                        "created_at": data.get("created_at"),
                        "last_activity": data.get("last_activity"),
                        "message_count": len(data.get("messages", [])),
                        "first_message": data.get("messages", [{}])[0].get("content", "")[:100] if data.get("messages") else ""
                    }
                    sessions.append(summary)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                
        # 按最后活动时间排序
        sessions.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        file_path = self.storage_dir / f"{session_id}.json"
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False

# 创建全局实例
chat_storage = ChatStorage()
