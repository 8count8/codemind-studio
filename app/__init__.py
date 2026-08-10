from flask import Flask, request, session, redirect, url_for, current_app, jsonify
from logging.handlers import RotatingFileHandler
import logging
import os


def init_logging(app):
    """ 初始化日志记录 """
    if not app.debug:
        # 如果应用不在调试模式下，则配置日志记录
        if not os.path.exists('logs'):
            # 如果日志目录不存在，则创建日志目录
            os.mkdir('logs')

        # 创建一个RotatingFileHandler，用于将日志写入文件，并设置文件大小和备份数量
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=3)

        # 设置日志格式，包括时间戳、日志级别、日志消息以及代码路径和行号
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

        # 设置日志处理器的日志级别为INFO
        file_handler.setLevel(logging.INFO)

        # 将日志处理器添加到应用的日志记录器中
        app.logger.addHandler(file_handler)

        # 设置应用日志记录器的日志级别为INFO
        app.logger.setLevel(logging.INFO)

        # 记录应用启动的日志信息
        app.logger.info('Application startup')


def create_app(config=None):
    """ 创建Flask应用实例 """
    app = Flask(__name__, template_folder="templates", static_folder='static')

    # 加载配置
    if config is not None:
        app.config.from_object(config)

    # 设置日志
    init_logging(app)

    # 初始化扩展
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect(app)

    # CORS 支持（允许 Vue 前端跨域访问）
    from flask_cors import CORS
    cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173')
    origins = [o.strip() for o in cors_origins.split(',') if o.strip()]
    CORS(app, supports_credentials=True, origins=origins)

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
        ability_matrix_bp
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
    # 请求拦截器
    @app.before_request
    def before_request():
        """
        请求拦截器，用于拦截未登录用户的请求
        :return: 如果请求不在白名单中且用户未登录，则重定向到登录页面
        """
        if 'user_id' in session:
            return
        elif request.blueprint in current_app.config.get('WHITELIST_BLUEPRINTS', []) \
                or request.endpoint in current_app.config.get('WHITELIST_ROUTES', []):
            return
        # 记录未授权访问的日志
        app.logger.warning(f'未授权访问: {request.endpoint}')
        return redirect(url_for('auth.login'))

    # 错误处理器（统一处理CSRF错误）
    @app.errorhandler(400)
    @app.errorhandler(403)
    def handle_csrf_error(e):
        if e.description.startswith('The CSRF token'):
            current_app.logger.warning(f'CSRF验证失败: {request.path}')
            return jsonify(status='error', message='安全验证失败'), 403
        return e

    return app
