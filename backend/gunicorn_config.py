"""
Gunicorn 配置文件
用于生产环境部署
"""
import os

# 服务器配置
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# 日志配置
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 进程配置
preload_app = True
max_requests = 1000
max_requests_jitter = 100

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
