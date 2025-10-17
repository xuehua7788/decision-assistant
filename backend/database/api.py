"""
数据库API接口 - 与现有项目完全兼容
严格审核：接口路径、参数名、响应格式
"""
from flask import Blueprint, jsonify, request
from .connection import test_database_connection
from .models import UserModel, ChatModel, DecisionAnalysisModel
from ..config.database import DatabaseConfig

# 创建数据库API蓝图
database_bp = Blueprint('database', __name__, url_prefix='/api/database')

@database_bp.route('/status', methods=['GET'])
def get_database_status():
    """获取数据库状态 - 新增接口，不冲突现有"""
    try:
        config = DatabaseConfig()
        
        # 基础配置信息
        status = {
            "database_configured": config.is_database_available(),
            "use_database": config.USE_DATABASE,
            "enable_analytics": config.ENABLE_ANALYTICS,
            "config_summary": config.get_config_summary()
        }
        
        # 如果数据库已配置，测试连接
        if config.is_database_available():
            connection_test = test_database_connection()
            status.update(connection_test)
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "database_configured": False,
            "use_database": False
        }), 500

@database_bp.route('/migrate', methods=['POST'])
def migrate_data():
    """数据迁移接口 - 新增接口，不冲突现有"""
    try:
        config = DatabaseConfig()
        
        if not config.is_database_available():
            return jsonify({
                "error": "数据库未配置",
                "migration_status": "failed"
            }), 400
        
        # 这里将实现数据迁移逻辑
        # 从JSON文件迁移到数据库
        
        return jsonify({
            "message": "数据迁移功能开发中",
            "migration_status": "pending",
            "current_storage": "JSON files",
            "target_storage": "PostgreSQL database"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "migration_status": "failed"
        }), 500

@database_bp.route('/test-connection', methods=['GET'])
def test_connection():
    """测试数据库连接 - 新增接口，不冲突现有"""
    try:
        result = test_database_connection()
        
        if result["status"] == "success":
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"连接测试失败: {str(e)}"
        }), 500

@database_bp.route('/config', methods=['GET'])
def get_config():
    """获取数据库配置信息 - 新增接口，不冲突现有"""
    try:
        config = DatabaseConfig()
        
        # 只返回非敏感信息
        safe_config = {
            "database_configured": config.is_database_available(),
            "use_database": config.USE_DATABASE,
            "enable_analytics": config.ENABLE_ANALYTICS,
            "db_name": config.DB_NAME,
            "db_host": config.DB_HOST if config.DB_HOST else "not_configured",
            "db_port": config.DB_PORT,
            "flask_env": config.FLASK_ENV,
            "port": config.PORT
        }
        
        return jsonify(safe_config), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "database_configured": False
        }), 500
