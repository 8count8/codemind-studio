"""
CodeMind Studio - 后端生产启动入口
支持 Render.com / Deta Space / 任意 Python 托管平台

启动方式:
  python run_backend.py
  waitress-serve --host=0.0.0.0 --port=$PORT run_backend:app
"""
import os
import sys

# 确保项目根目录在 sys.path 中
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.environ.setdefault('FLASK_ENV', 'production')

from app import create_app
from config import ProductionConfig

app = create_app(config=ProductionConfig)

# 初始化数据库
try:
    from app.models.db import init_database
    init_database()
except Exception as e:
    print(f"[WARN] 数据库初始化跳过: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')

    from waitress import serve
    print(f"[CodeMind Studio] 后端启动: http://{host}:{port}")
    serve(app, host=host, port=port, threads=8)
