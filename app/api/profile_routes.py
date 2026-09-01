from . import profile_bp
import re

from flask import session, current_app, jsonify, request
from app.utils.auth import require_auth

from ..models.user_login import get_user_profile, get_user_profile_by_id, update_user_profile


def _profile_payload(user_info):
    return {
        "status": 200,
        "data": {
            **user_info,
            "user_avatar": "/img/user_icon.png",
        },
    }


@profile_bp.route('/profile', methods=['GET', 'POST'])
@require_auth
def profile():
    """
    个人资料页面（页面由 Vue Router 渲染）
    """
    user_id = session.get('user_id')
    current_app.logger.info(f'用户访问个人资料页面: {user_id}')
    user_info = get_user_profile_by_id(user_id)
    if user_info is None:
        # 兼容旧会话（历史版本将 username 放在 user_id 中）。
        user_info = get_user_profile(username=session.get('username') or user_id)
    if not user_info:
        return jsonify({"status": 404, "message": "用户不存在"}), 404
    payload = _profile_payload(user_info)
    payload["user"] = payload["data"]
    return jsonify(payload)


@profile_bp.route('/api/profile', methods=['GET', 'PUT'])
@profile_bp.route('/api/profile/me', methods=['GET'])
@profile_bp.route('/api/profile/update', methods=['PUT'])
@require_auth
def profile_api():
    user_id = session.get('user_id')
    if request.method == 'PUT':
        body = request.get_json(silent=True) or {}
        username = str(body.get('username') or '').strip()
        email = str(body.get('email') or '').strip().lower()
        if not re.fullmatch(r'[A-Za-z0-9_\u4e00-\u9fff]{2,50}', username):
            return jsonify({"status": 400, "message": "用户名需为 2-50 位中英文、数字或下划线"}), 400
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) or len(email) > 100:
            return jsonify({"status": 400, "message": "邮箱格式不正确"}), 400
        result = update_user_profile(user_id, username, email)
        if result.get('status') != 'success':
            return jsonify({"status": 409, "message": result.get('message', '更新失败')}), 409
        session['username'] = username

    user_info = get_user_profile_by_id(user_id)
    if not user_info:
        return jsonify({"status": 404, "message": "用户不存在"}), 404
    return jsonify(_profile_payload(user_info))
