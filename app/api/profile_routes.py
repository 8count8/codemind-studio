from . import profile_bp
from flask import render_template, session, url_for, redirect, current_app

from ..models.user_login import get_user_profile


@profile_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """
    个人资料页面
    """
    # 检查用户是否已登录
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    # 记录访问日志
    current_app.logger.info(f'用户访问个人资料页面: {user_id}')

    # 数据库查询获取用户信息
    user_info = get_user_profile(username=user_id)


    user = {
        'username': user_info['username'],
        'email': user_info['email'],
        "user_avatar": "/static/img/user_icon.png"
    }

    return render_template('profile.html', user=user)

