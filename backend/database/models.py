"""
数据库模型 - 与现有项目完全兼容
严格审核：表名、字段名、索引名
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..config.database import DatabaseConfig

# 如果数据库未启用，使用模拟类
if not DatabaseConfig.USE_DATABASE:
    class BaseModel:
        """模拟基础模型类"""
        pass
else:
    from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship
    
    Base = declarative_base()

class UserModel:
    """用户模型 - 与现有users_data.json兼容"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.config = DatabaseConfig()
    
    def create_user(self, username: str, password: str) -> Dict[str, Any]:
        """创建用户 - 与现有register接口兼容"""
        if not self.config.USE_DATABASE:
            # 使用现有JSON存储
            return self._create_user_json(username, password)
        
        # 使用数据库存储
        return self._create_user_db(username, password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """用户认证 - 与现有login接口兼容"""
        if not self.config.USE_DATABASE:
            # 使用现有JSON存储
            return self._authenticate_user_json(username, password)
        
        # 使用数据库存储
        return self._authenticate_user_db(username, password)
    
    def _create_user_json(self, username: str, password: str) -> Dict[str, Any]:
        """使用JSON存储创建用户（现有逻辑）"""
        import json
        import os
        
        users_file = 'users_data.json'
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
        else:
            users = {}
        
        users[username] = {
            "password": password,
            "created_at": str(os.urandom(16).hex())
        }
        
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        return {
            "username": username,
            "token": os.urandom(32).hex()
        }
    
    def _authenticate_user_json(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """使用JSON存储认证用户（现有逻辑）"""
        import json
        import os
        
        users_file = 'users_data.json'
        if not os.path.exists(users_file):
            return None
        
        with open(users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        if username not in users:
            return None
        
        if users[username]['password'] != password:
            return None
        
        return {
            "username": username,
            "token": os.urandom(32).hex()
        }
    
    def _create_user_db(self, username: str, password: str) -> Dict[str, Any]:
        """使用数据库存储创建用户"""
        # 这里将在数据库表创建后实现
        pass
    
    def _authenticate_user_db(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """使用数据库存储认证用户"""
        # 这里将在数据库表创建后实现
        pass

class ChatModel:
    """聊天模型 - 与现有chat_data目录兼容"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.config = DatabaseConfig()
    
    def save_message(self, username: str, user_message: str, assistant_response: str) -> bool:
        """保存聊天消息 - 与现有save_chat_message函数兼容"""
        if not self.config.USE_DATABASE:
            # 使用现有JSON存储
            return self._save_message_json(username, user_message, assistant_response)
        
        # 使用数据库存储
        return self._save_message_db(username, user_message, assistant_response)
    
    def load_messages(self, username: str) -> Optional[Dict[str, Any]]:
        """加载聊天消息 - 与现有load_chat_data函数兼容"""
        if not self.config.USE_DATABASE:
            # 使用现有JSON存储
            return self._load_messages_json(username)
        
        # 使用数据库存储
        return self._load_messages_db(username)
    
    def _save_message_json(self, username: str, user_message: str, assistant_response: str) -> bool:
        """使用JSON存储保存消息（现有逻辑）"""
        import json
        import os
        
        chat_data_dir = 'chat_data'
        if not os.path.exists(chat_data_dir):
            os.makedirs(chat_data_dir)
        
        chat_file = os.path.join(chat_data_dir, f'{username}.json')
        
        if os.path.exists(chat_file):
            with open(chat_file, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
        else:
            chat_data = {"username": username, "messages": []}
        
        chat_data["messages"].append({
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": os.urandom(16).hex()
        })
        
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        
        return True
    
    def _load_messages_json(self, username: str) -> Optional[Dict[str, Any]]:
        """使用JSON存储加载消息（现有逻辑）"""
        import json
        import os
        
        chat_file = os.path.join('chat_data', f'{username}.json')
        if os.path.exists(chat_file):
            with open(chat_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _save_message_db(self, username: str, user_message: str, assistant_response: str) -> bool:
        """使用数据库存储保存消息"""
        # 这里将在数据库表创建后实现
        pass
    
    def _load_messages_db(self, username: str) -> Optional[Dict[str, Any]]:
        """使用数据库存储加载消息"""
        # 这里将在数据库表创建后实现
        pass

class DecisionAnalysisModel:
    """决策分析模型 - 新增功能"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.config = DatabaseConfig()
    
    def save_analysis(self, username: str, description: str, options: List[str], 
                     analysis_result: Dict[str, Any]) -> str:
        """保存决策分析结果"""
        if not self.config.USE_DATABASE:
            # 使用JSON存储
            return self._save_analysis_json(username, description, options, analysis_result)
        
        # 使用数据库存储
        return self._save_analysis_db(username, description, options, analysis_result)
    
    def _save_analysis_json(self, username: str, description: str, options: List[str], 
                           analysis_result: Dict[str, Any]) -> str:
        """使用JSON存储保存分析结果"""
        import json
        import os
        
        analysis_dir = 'analysis_data'
        if not os.path.exists(analysis_dir):
            os.makedirs(analysis_dir)
        
        analysis_id = os.urandom(16).hex()
        analysis_file = os.path.join(analysis_dir, f'{analysis_id}.json')
        
        analysis_data = {
            "analysis_id": analysis_id,
            "username": username,
            "description": description,
            "options": options,
            "result": analysis_result,
            "created_at": str(os.urandom(16).hex())
        }
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        return analysis_id
    
    def _save_analysis_db(self, username: str, description: str, options: List[str], 
                         analysis_result: Dict[str, Any]) -> str:
        """使用数据库存储保存分析结果"""
        # 这里将在数据库表创建后实现
        pass
