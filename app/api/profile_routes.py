from . import profile_bp
from flask import session, url_for, redirect, current_app, jsonify
from app.utils.auth import require_auth

from ..models.user_login import get_user_profile


@profile_bp.route('/profile', methods=['GET', 'POST'])
@require_auth
def profile():
    """
    个人资料页面（页面由 Vue Router 渲染）
    """
    user_id = session.get('user_id')
    current_app.logger.info(f'用户访问个人资料页面: {user_id}')
    user_info = get_user_profile(username=user_id)

    return jsonify({
        "status": 200,
        "user": {
            "username": user_info['username'],
            "email": user_info['email'],
            "user_avatar": "/static/img/user_icon.png"
        }
    })