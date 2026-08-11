"""
统一认证模块 — 集中管理 session 用户提取与鉴权

替代散落在各路由中的重复模式:
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": 401, "message": "请先登录"}), 401

提供三种使用方式:
1. get_current_user_id() — 直接获取 user_id，不做鉴权
2. require_auth() — 装饰器：未登录自动返回 401
3. get_authenticated_user_id() — 内联获取 user_id + 自动 401 响应
"""

from functools import wraps
from flask import session, jsonify, g

from app.utils.constants import HTTPStatus


def get_current_user_id():
    """从 session 获取当前用户 ID（不做鉴权，返回 None 表示未登录）"""
    return session.get('user_id')


def is_authenticated():
    """判断当前用户是否已登录"""
    return session.get('user_id') is not None


def get_authenticated_user_id():
    """
    获取已认证的用户 ID。
    如果未登录，返回 (None, error_response) 元组，调用方应检查 error_response 是否为 None。

    使用示例:
        user_id, err = get_authenticated_user_id()
        if err:
            return err
        # 继续使用 user_id
    """
    user_id = session.get('user_id')
    if not user_id:
        error_response = jsonify({
            "status": HTTPStatus.UNAUTHORIZED,
            "message": "请先登录"
        }), HTTPStatus.UNAUTHORIZED
        return None, error_response
    return user_id, None


def require_auth(f):
    """
    路由装饰器：要求用户已登录。
    未登录时自动返回 401 JSON 响应。

    使用示例:
        @ability_matrix_bp.route('/api/ability-matrix')
        @require_auth
        def get_ability_matrix():
            user_id = session.get('user_id')
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                "status": HTTPStatus.UNAUTHORIZED,
                "message": "请先登录"
            }), HTTPStatus.UNAUTHORIZED
        return f(*args, **kwargs)
    return decorated


def clear_session():
    """清除当前 session（退出登录时使用）"""
    session.pop('user_id', None)


def set_user_session(user_id):
    """设置用户 session（登录时使用）"""
    session['user_id'] = user_id