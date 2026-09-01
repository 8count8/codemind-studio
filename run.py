"""
Flask 应用启动入口 - 供 gunicorn/Waitress / 桌面版 PyInstaller 使用
"""
import os
import sys
import logging

# ===== 桌面版（APP_DEPLOY_MODE=desktop）核心修正 =====
# PyInstaller --onefile 会把代码解压到 sys._MEIPASS；
# 同时我们要保证 DB / Ollama / 上传文件 写到安装目录（用户可访问），
# 而不是写进临时 _MEIPASS 目录。
# =======================================================
APP_DEPLOY_MODE = os.environ.get("APP_DEPLOY_MODE", "server").strip().lower()
_IS_DESKTOP = APP_DEPLOY_MODE == "desktop"

# 1) 解析"运行时持久化根目录"（桌面版必设）
def _resolve_runtime_root():
    if _IS_DESKTOP:
        # 优先使用启动器传入的环境变量；其次退回 exe 同级目录
        env_dir = (os.environ.get("APP_RUNTIME_ROOT") or "").strip()
        if env_dir:
            return env_dir
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        # 开发者机调试 desktop 模式：用项目根
        return os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.abspath(__file__))

RUNTIME_ROOT = _resolve_runtime_root()
os.environ["APP_RUNTIME_ROOT"] = RUNTIME_ROOT

# 2) 桌面版强制端口 & 路径（避免撞用户自己的 MySQL/Ollama/Flask）
if _IS_DESKTOP:
    os.environ.setdefault("DB_HOST", "127.0.0.1")
    os.environ.setdefault("DB_PORT", "13306")
    os.environ.setdefault("DB_USER", "codemind")
    # DB_PASSWORD / DB_NAME 由启动器写入 <RUNTIME_ROOT>/etc/.env，会在下面 load_dotenv 加载
    os.environ.setdefault("DB_NAME", "codemind")
    # Ollama 端口 + 模型仓库 都指向安装目录下的 ./runtime/ollama / ./models
    os.environ.setdefault("OLLAMA_HOST", "127.0.0.1")
    os.environ.setdefault("OLLAMA_MODELS", os.path.join(RUNTIME_ROOT, "models"))
    os.environ.setdefault("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
    # 上传/日志 持久化目录
    os.environ.setdefault("UPLOAD_FOLDER", os.path.join(RUNTIME_ROOT, "user_uploads"))
    os.environ.setdefault("LOG_DIR",  os.path.join(RUNTIME_ROOT, "logs"))
    # Flask 端口优先取环境变量（启动器传一个空闲的），否则 5000
    os.environ.setdefault("PORT", "5000")

# 3) 加载 <RUNTIME_ROOT>/etc/.env（桌面版专属：里面有随机生成的 MySQL 密码等）
#    开发机 server 模式下仍加载项目根的 .env
_ETC_ENV = os.path.join(RUNTIME_ROOT, "etc", ".env") if _IS_DESKTOP else None
try:
    from dotenv import load_dotenv
    if _ETC_ENV and os.path.isfile(_ETC_ENV):
        load_dotenv(_ETC_ENV, override=False)  # 不覆盖启动器传入的环境变量
    load_dotenv(override=False)
except Exception:
    pass  # python-dotenv 没装也不强求（桌面版打包进了 exe）

# 确保项目根目录在 Python 路径中
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.environ.setdefault('FLASK_ENV', 'production')

import config
from app import create_app

# 创建 Flask 应用实例
if _IS_DESKTOP:
    # 桌面版：DEBUG=False、关闭重定向警告、保证跨域允许 127.0.0.1
    app = create_app(config=config.ProductionConfig)
else:
    app = create_app(config=config.ProductionConfig)

# 初始化数据库（幂等操作）
try:
    from app.models.db import init_database
    init_database()
    print("[DB] 数据库初始化成功")
except Exception as e:
    print(f"[DB] 数据库初始化跳过: {e}")


# ============ 桌面版：挂载前端 dist 到根路径 / ==============
def _resolve_frontend_dir():
    """桌面版 / 开发者模式下，找到 Vue 构建输出目录"""
    candidates = []
    # 1) PyInstaller 打包时 --add-data 打进的目录（sys._MEIPASS/frontend-dist）
    if getattr(sys, "frozen", False):
        candidates.append(os.path.join(getattr(sys, "_MEIPASS", ""), "frontend-dist"))
    # 2) packaging/staging/frontend-dist（开发模式 build_setup.ps1 已经构建好）
    candidates.append(os.path.join(ROOT_DIR, "packaging", "staging", "frontend-dist"))
    # 3) 退回：用户自己把 dist 拷到项目根的 frontend/dist
    candidates.append(os.path.join(ROOT_DIR, "frontend", "dist"))
    for d in candidates:
        if d and os.path.isdir(d) and os.path.isfile(os.path.join(d, "index.html")):
            return d
    return None

FRONTEND_DIR = _resolve_frontend_dir()


@app.route('/health')
def health_check():
    """健康检查端点（桌面版启动器轮询用）"""
    import json
    result = {
        "status": "ok",
        "service": "cms-backend",
        "deploy_mode": APP_DEPLOY_MODE,
        "runtime_root": RUNTIME_ROOT,
        "frontend_dir": FRONTEND_DIR or "MISSING",
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

    # 数据库连接测试
    try:
        from app.models.db_connection import get_db_connection
        conn = get_db_connection()
        conn.close()
        result["database_status"] = "ok"
    except Exception as e:
        result["database_status"] = f"failed: {str(e)}"

    return app.response_class(
        response=json.dumps(result, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )


if FRONTEND_DIR:
    from flask import send_from_directory, safe_join

    @app.route('/')
    def root():
        """桌面版：根路径返回前端 SPA 首页"""
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route('/<path:filename>')
    def frontend_static(filename):
        """
        静态资源路由（Vue 的 assets/ 资源等）：
        - 如果前端 build 产物里有这个文件 → 直接返回
        - 否则（SPA deep-link，例如 /login、/dashboard）返回 index.html 交给 vue-router
        """
        full = safe_join(FRONTEND_DIR, filename)
        if os.path.isfile(full):
            return send_from_directory(FRONTEND_DIR, filename)
        return send_from_directory(FRONTEND_DIR, "index.html")
else:
    @app.route('/')
    def root():
        return 'CodeMind Studio Backend API is running! (Desktop frontend build not detected.)'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    if _IS_DESKTOP:
        # 桌面版：用 Waitress 替换 Flask dev server（稳定、无 warning、不需要 --no-reload）
        try:
            from waitress import serve
            print(f"[SERVER][desktop] Waitress 启动在 http://127.0.0.1:{port}")
            serve(app, host='127.0.0.1', port=port, threads=32,
                  _quiet=False, ident="CodeMindStudio")
        except ImportError:
            print(f"[SERVER][desktop] 退回 Flask dev server http://127.0.0.1:{port}")
            app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    else:
        print(f"[SERVER][server] Flask 启动在 0.0.0.0:{port}")
        app.run(host='0.0.0.0', port=port)
