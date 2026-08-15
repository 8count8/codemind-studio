"""
Flask 应用启动入口 - 供 gunicorn/Waitress 使用
"""
import os
import sys

# 确保项目根目录在 Python 路径中
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.environ.setdefault('FLASK_ENV', 'production')

import config
from app import create_app

# 创建 Flask 应用实例
app = create_app(config=config.ProductionConfig)

# 初始化数据库（幂等操作）
try:
    from app.models.db import init_database
    init_database()
    print("[DB] 数据库初始化成功")
except Exception as e:
    print(f"[DB] 数据库初始化跳过: {e}")


@app.route('/health')
def health_check():
    """健康检查端点"""
    import json
    result = {
        "status": "ok",
        "service": "cms-backend",
        "email_env": {
            "EMAIL_TYPE": "SET" if os.getenv("EMAIL_TYPE") else "MISSING",
            "EMAIL_ADDRESS": "SET" if os.getenv("EMAIL_ADDRESS") else "MISSING",
            "EMAIL_PASSWORD": "SET" if os.getenv("EMAIL_PASSWORD") else "MISSING",
        },
        "database": {
            "DB_HOST": os.getenv("DB_HOST", "localhost"),
            "DB_PORT": os.getenv("DB_PORT", "3306"),
            "DB_USER": os.getenv("DB_USER", "root"),
            "DB_NAME": os.getenv("DB_NAME", "codemind"),
        },
    }
    
    # SMTP 连接测试
    try:
        import socket
        socket.setdefaulttimeout(3)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("smtp.163.com", 465))
        s.close()
        result["smtp"] = "ok"
    except Exception as e:
        result["smtp"] = f"failed: {str(e)}"
    
    # 数据库连接测试
    try:
        from app.models.db_connection import get_db_connection
        conn = get_db_connection()
        conn.close()
        result["database_status"] = "ok"
    except Exception as e:
        result["database_status"] = f"failed: {str(e)}"
    
    return app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )


@app.route('/')
def root():
    """根路径"""
    return 'CodeMind Studio Backend API is running!'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[SERVER] Flask 启动在端口 {port}")
    app.run(host='0.0.0.0', port=port)
