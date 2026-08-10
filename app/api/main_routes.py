""" 主页路由 """
from . import main_bp
from flask import session, current_app, jsonify
from flask_wtf.csrf import generate_csrf


@main_bp.route('/')
@main_bp.route('/home', methods=['GET'])
def home():
    """
    首页（页面由 Vue Router 渲染）
    """
    return jsonify({"status": 200})


@main_bp.route('/dashboard')
def dashboard():
    """
    仪表盘路由（页面由 Vue Router 渲染）
    """
    current_app.logger.info(f'用户 {session.get("user_id")} 访问仪表盘')
    return jsonify({"status": 200})


@main_bp.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    """
    获取 CSRF token（供 Vue 前端调用）
    """
    return jsonify({'csrf_token': generate_csrf()})
