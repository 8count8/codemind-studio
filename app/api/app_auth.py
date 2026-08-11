"""
    用户认证
"""
from app.api.flasgger_compat import swag_from

from . import auth_bp
from flask import redirect, url_for, request, current_app, jsonify

from app.service import UserLoginService
from app.utils.auth import set_user_session, clear_session, get_current_user_id


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录
    """
    try:
        if request.method == 'POST':
            # 获取表单中的用户名和密码
            username = request.form.get('username')
            password = request.form.get('password')

            # 调用 UserLoginService 进行登录验证
            result = UserLoginService.login(username, password)

            # 根据登录结果进行处理
            if result["status"] == "success":
                set_user_session(username)
                current_app.logger.info(f'用户登录成功: {username}')
                return {"status": 200, "message": "用户登录成功", "redirect": url_for('main.dashboard')}
            else:
                current_app.logger.warning(f'用户登录失败: {username}, 原因: {result["message"]}')
                return {"status": 400, "message": result["message"]}

        # GET 请求（页面由 Vue Router 渲染）
        return jsonify({"status": 200, "message": "请使用 Vue 前端访问"})
    except Exception as e:
        current_app.logger.error(f"登录错误: {str(e)}")
        return f"服务器错误: {str(e)}", 500


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    退出登录
    """
    user_id = get_current_user_id()
    if user_id:
        clear_session()
        current_app.logger.info(f'用户退出: {user_id}')
    return jsonify({"status": 200, "message": "退出成功"})


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    注册新用户
    """
    try:
        if request.method == 'POST':
            # 获取表单中的用户名、密码、邮箱和验证码
            username = request.form.get('new-username')
            password = request.form.get('new-password')
            email = request.form.get('new-email')
            user_input_code = request.form.get('verification-code')

            # 调用 UserLoginService 进行注册
            result = UserLoginService.register(username, password, email, user_input_code)

            # 根据注册结果进行处理
            if result["status"] == "success":
                current_app.logger.info(f'用户注册成功: {username}')
                return {"status": 200, "message": "注册成功", "redirect": url_for('auth.login')}
            else:
                current_app.logger.warning(f'用户注册失败: {username}, 原因: {result["message"]}')
                return {"status": 400, "message": result["message"]}

        # GET 请求（页面由 Vue Router 渲染）
        return jsonify({"status": 200, "message": "请使用 Vue 前端访问"})
    except Exception as e:
        current_app.logger.error(f"注册错误: {str(e)}")
        return f"服务器错误: {str(e)}", 500


@auth_bp.route('/get_verification_code', methods=['POST'])
@swag_from({
    'tags': ['用户认证'],
    'description': '发送验证码到指定邮箱',
    'parameters': [
        {
            'name': 'email',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': '接收验证码的邮箱地址'
        }
    ],
    'responses': {
        200: {
            'description': '验证码发送结果',
            'examples': {
                'success': {'status': 'success', 'message': '验证码已发送'},
                'error': {'status': 'error', 'message': '邮箱格式不正确'}
            }
        },
        500: {
            'description': '服务器内部错误',
            'examples': {'error': {'status': 'error', 'message': '服务器错误'}}
        }
    }
})
def get_verification_code():
    """
    获取验证码
    """
    try:
        # 获取表单中的邮箱
        email = request.form.get('email')

        print(email)
        # 调用 UserLoginService 获取验证码
        result = UserLoginService.get_verification_code(email)
        print(result)
        # 返回 JSON 格式的响应结果
        return result
    except Exception as e:
        current_app.logger.error(f"获取验证码错误: {str(e)}")
        return {"status": "error", "message": "服务器错误"}, 500


@auth_bp.route('/reset', methods=['GET', 'POST'])
def reset():
    """
    重置密码
    """
    try:
        if request.method == 'POST':
            # 获取表单中的邮箱、新密码和验证码
            email = request.form.get('email')
            new_password = request.form.get('new_password')
            user_input_code = request.form.get('verification_code')

            # 调用 UserLoginService 进行密码重置
            result = UserLoginService.reset_password(email, new_password, user_input_code)

            # 根据重置结果进行处理
            if result["status"] == "success":
                current_app.logger.info(f'密码重置成功: {email}')
                return redirect(url_for('auth.login'))  # 重置成功，跳转到登录页
            else:
                current_app.logger.warning(f'密码重置失败: {email}, 原因: {result["message"]}')
                return {"status": 400, "message": result["message"]}

        # GET 请求（页面由 Vue Router 渲染）
        return jsonify({"status": 200, "message": "请使用 Vue 前端访问"})
    except Exception as e:
        current_app.logger.error(f"重置密码错误: {str(e)}")
        return f"服务器错误: {str(e)}", 500


@auth_bp.route('/get_forgot_password_code', methods=['POST'])
def get_forgot_password_code():
    """
    获取忘记密码的验证码
    """
    try:
        # 获取表单中的邮箱
        email = request.form.get('email')

        # 调用 UserLoginService 获取验证码
        result = UserLoginService.get_forgot_password_code(email)

        # 返回 JSON 格式的响应结果
        return result
    except Exception as e:
        current_app.logger.error(f"获取验证码错误: {str(e)}")
        return {"status": "error", "message": "服务器错误"}, 500


@auth_bp.route('/status', methods=['GET'])
def check_login_status():
    user_id = get_current_user_id()
    if user_id:
        return {"isAuthenticated": True, "user": {"username": user_id, "avatar": "default-avatar.png"}}
    else:
        return {"isAuthenticated": False}


@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    """
    处理重置密码的请求。
    """
    try:
        # 获取表单中的邮箱、新密码和验证码
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        verification_code = request.form.get('verification_code')

        # 调用 UserLoginService 进行密码重置
        result = UserLoginService.reset_password(email, new_password, verification_code)

        # 根据重置结果进行处理
        if result["status"] == "success":
            current_app.logger.info(f'密码重置成功: {email}')
            return {"status": 200, "message": "密码重置成功，请使用新密码登录"}
        else:
            current_app.logger.warning(f'密码重置失败: {email}, 原因: {result["message"]}')
            return {"status": 400, "message": result["message"]}
    except Exception as e:
        current_app.logger.error(f"重置密码错误: {str(e)}")
        return {"status": 500, "message": "服务器错误"}, 500

# /auth/status
@auth_bp.route('/auth/status', methods=['GET'])
def auth_status():
    """
    检查用户认证状态。
    """
    try:
        user_id = get_current_user_id()
        if user_id:
            return jsonify({"isAuthenticated": True, "user": {"username": user_id, "avatar": "/static/img/user_icon.png"}}), 200
        else:
            return jsonify({"isAuthenticated": False}), 200
    except Exception as e:
        current_app.logger.error(f"检查登录状态错误: {str(e)}")
        return jsonify({"isAuthenticated": False}), 500


