from flask import Flask, request, session, redirect, url_for, current_app, jsonify
from logging.handlers import RotatingFileHandler
import logging
import os


def init_logging(app):
    """初始化日志记录 (生产环境使用 stdout，本地开发使用文件日志)"""
    is_production = os.environ.get('FLASK_ENV') == 'production'

    if is_production:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
    elif not app.debug:
        # 本地非调试: 文件日志
        try:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=3)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
        except (OSError, PermissionError):
            # 无法创建日志目录时回退到 stdout
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            app.logger.addHandler(stream_handler)
            app.logger.setLevel(logging.INFO)

    app.logger.info('Application startup')


def create_app(config=None):
    """ 创建Flask应用实例 """
    app = Flask(__name__)

    # 加载配置
    if config is None:
        import config as project_config
        config = (
            project_config.DevelopmentConfig
            if os.environ.get('FLASK_ENV') == 'development'
            else project_config.ProductionConfig
        )
    app.config.from_object(config)

    # ---- 跨域 Session Cookie 配置 ----
    # 生产环境使用 HTTPS，需设置 Secure + SameSite=None
    is_production = os.environ.get('FLASK_ENV') == 'production'
    secure_cookie_env = os.environ.get('SESSION_COOKIE_SECURE')
    secure_cookie = (
        secure_cookie_env.strip().lower() in ('1', 'true', 'yes', 'on')
        if secure_cookie_env is not None
        else False
    )
    app.config.update(
        # Docker 快速开始默认通过 http://localhost:8080 访问；HTTPS 反代
        # 部署时用 SESSION_COOKIE_SECURE=true 显式开启 Secure Cookie。
        SESSION_COOKIE_SECURE=secure_cookie,
        SESSION_COOKIE_SAMESITE='None' if secure_cookie else 'Lax',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_NAME='codemind_session',
        PERMANENT_SESSION_LIFETIME=86400
    )

    # 设置日志
    init_logging(app)

    # 初始化扩展。Session Cookie 认证仍然需要 CSRF 防护；测试配置可显式关闭。
    csrf_enabled = app.config.get('WTF_CSRF_ENABLED', True)

    class NoOpCSRF:
        """空的 CSRF 实现，完全跳过检查"""
        def exempt(self, f):
            return f
        def protect(self):
            pass
    
    if csrf_enabled:
        from flask_wtf.csrf import CSRFProtect
        csrf = CSRFProtect(app)
    else:
        # 生产环境：使用空实现，完全跳过 CSRF 检查
        # 并且不导入 flask_wtf 模块
        csrf = NoOpCSRF()

    # CORS 支持（允许 Vue 前端跨域访问）
    from flask_cors import CORS
    cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173')
    origins = [o.strip() for o in cors_origins.split(',') if o.strip()]
    CORS(app, supports_credentials=True, origins=origins)

    # Swagger/OpenAPI 在线文档（文档要求访问 /apidocs/）。
    if os.environ.get('ENABLE_SWAGGER', 'true').strip().lower() in ('1', 'true', 'yes', 'on'):
        try:
            from flasgger import Swagger
            Swagger(
                app,
                config=getattr(config, 'swagger_config', None),
                template=getattr(config, 'SWAGGER_TEMPLATE', None),
            )
        except ImportError:
            app.logger.warning('flasgger 未安装，/apidocs/ 不可用')

    # 导入蓝图
    from app.api import (
        auth_bp,
        main_bp,
        answer_bp,
        code_review_bp,
        quizbank_bp,
        favorites_history_bp,
        user_api_bp,
        ai_question_bp,
        profile_bp,
        ability_matrix_bp,
        ollama_bp,
        admin_bp,
    )
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(answer_bp)
    app.register_blueprint(code_review_bp)
    app.register_blueprint(quizbank_bp)
    app.register_blueprint(favorites_history_bp)
    app.register_blueprint(user_api_bp)
    app.register_blueprint(ai_question_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(ability_matrix_bp)
    app.register_blueprint(ollama_bp)
    app.register_blueprint(admin_bp)

    # ---- 请求拦截器 ----
    @app.before_request
    def before_request():
        """
        公开 API 豁免认证检查
        """
        # 公开路由列表（不需要登录）
        public_routes = [
            '/',
            '/home',
            '/api/csrf-token',
            '/get_verification_code',
            '/get_forgot_password_code',
            '/register',
            '/login',
            '/health',
            '/auth/status',
            '/reset',
            '/reset_password',
        ]
        if request.path == '/api/questions' and request.method == 'GET':
            # 游客可以浏览题目列表，但题目详情和答题功能需要登录。
            return None
        if request.path in public_routes and request.method in ('POST', 'PUT', 'PATCH', 'DELETE', 'GET'):
            # 公开 API 直接放行
            return None

        # 已登录用户直接放行
        if 'user_id' in session:
            return
        if request.blueprint in current_app.config.get('WHITELIST_BLUEPRINTS', []) \
                or request.endpoint in current_app.config.get('WHITELIST_ROUTES', []):
            return
        app.logger.warning(f'未授权访问: {request.endpoint}')
        if request.path.startswith('/api/') or request.endpoint and '.api' in request.endpoint:
            return jsonify(status='error', message='未登录或登录已过期', code=401), 401
        return redirect(url_for('auth.login'))

    # CSRF 错误统一返回前端可读 JSON。
    if csrf_enabled:
        @app.errorhandler(400)
        @app.errorhandler(403)
        def handle_csrf_error(e):
            if e.description.startswith('The CSRF token'):
                current_app.logger.warning(f'CSRF验证失败: {request.path}')
                return jsonify(status='error', message='安全验证失败'), 403
            return e

    return app
