"""
Data Models for Decision Assistant
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatSession(Base):
    """聊天会话模型"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联的消息
    messages = relationship("ChatMessage", back_populates="session")
    
    # 提取的决策参数
    extracted_params = Column(JSON, default={})
    decision_context = Column(Text)

class ChatMessage(Base):
    """聊天消息模型"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String(50))  # user or assistant
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # 提取的关键信息
    extracted_entities = Column(JSON, default={})
    
    session = relationship("ChatSession", back_populates="messages")

class DecisionAnalysis(Base):
    """决策分析结果模型"""
    __tablename__ = "decision_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    description = Column(Text)
    options = Column(JSON)
    
    # 算法结果
    algorithm_results = Column(JSON)
    final_recommendation = Column(String(500))
    confidence_score = Column(String(50))
    
    # AI分析结果
    ai_analysis = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ExtractedParameters(Base):
    """从对话中提取的参数"""
    __tablename__ = "extracted_parameters"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    
    # 决策相关参数
    decision_type = Column(String(100))
    budget = Column(String(100))
    timeline = Column(String(100))
    priorities = Column(JSON)
    constraints = Column(JSON)
    
    # 提取的选项
    identified_options = Column(JSON)
    
    extracted_at = Column(DateTime, default=datetime.utcnow)
