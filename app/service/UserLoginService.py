from app.models.user_login import handle_register, handle_get_verification_code, handle_login, \
    handle_forgot_password_reset, handle_forgot_password_get_code

import re


def _valid_email(email):
    return isinstance(email, str) and len(email) <= 100 and re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email)


def _valid_password(password):
    return (
        isinstance(password, str)
        and 8 <= len(password) <= 128
        and re.search(r'[A-Za-z]', password)
        and re.search(r'\d', password)
    )


class UserLoginService:

    @staticmethod
    def login(username, password):
        """
        处理用户登录请求。
        :param username: 用户名
        :param password: 密码（明文）
        :return: JSON 格式的响应结果
        """
        if not isinstance(username, str) or not username.strip() or not isinstance(password, str):
            return {"status": "error", "message": "请输入账号和密码"}
        result = handle_login(username, password)
        return result

    @staticmethod
    def register(username, password, email, user_input_code):
        """
        处理用户注册请求。
        :param username: 用户名
        :param password: 密码（明文）
        :param email: 邮箱
        :param user_input_code: 用户输入的验证码
        :return: JSON 格式的响应结果
        """
        if not isinstance(username, str) or not re.fullmatch(r'[A-Za-z0-9_\u4e00-\u9fff]{2,50}', username):
            return {"status": "error", "message": "用户名需为 2-50 位中英文、数字或下划线"}
        if not _valid_email(email):
            return {"status": "error", "message": "邮箱格式不正确"}
        if not _valid_password(password):
            return {"status": "error", "message": "密码需为 8-128 位且同时包含字母和数字"}
        if not isinstance(user_input_code, str) or not re.fullmatch(r'\d{6}', user_input_code):
            return {"status": "error", "message": "验证码应为 6 位数字"}
        result = handle_register(username, password, email, user_input_code)
        return result

    @staticmethod
    def get_verification_code(email):
        """
        处理获取验证码请求。
        :param email: 邮箱地址
        :return: JSON 格式的响应结果
        """
        if not _valid_email(email):
            return {"status": "error", "message": "邮箱格式不正确"}
        result = handle_get_verification_code(email)
        return result

    @staticmethod
    def get_forgot_password_code(email):
        """
        处理忘记密码时获取验证码的请求。
        :param email: 邮箱地址
        :return: JSON 格式的响应结果
        """
        if not _valid_email(email):
            return {"status": "error", "message": "邮箱格式不正确"}
        result = handle_forgot_password_get_code(email)
        return result

    @staticmethod
    def reset_password(email, new_password, user_input_code):
        """
        处理忘记密码时重置密码的请求。
        :param email: 邮箱地址
        :param new_password: 新密码（明文）
        :param user_input_code: 用户输入的验证码
        :return: JSON 格式的响应结果
        """
        if not _valid_email(email):
            return {"status": "error", "message": "邮箱格式不正确"}
        if not _valid_password(new_password):
            return {"status": "error", "message": "密码需为 8-128 位且同时包含字母和数字"}
        if not isinstance(user_input_code, str) or not re.fullmatch(r'\d{6}', user_input_code):
            return {"status": "error", "message": "验证码应为 6 位数字"}
        result = handle_forgot_password_reset(email, new_password, user_input_code)
        return result
