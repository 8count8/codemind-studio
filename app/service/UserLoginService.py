from app.models.user_login import handle_register, handle_get_verification_code, handle_login, \
    handle_forgot_password_reset, handle_forgot_password_get_code


class UserLoginService:

    @staticmethod
    def login(username, password):
        """
        处理用户登录请求。
        :param username: 用户名
        :param password: 密码（明文）
        :return: JSON 格式的响应结果
        """
        # 调用模型层的 handle_login 函数进行登录验证
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
        # 调用模型层的 handle_register 函数进行注册
        result = handle_register(username, password, email, user_input_code)
        return result

    @staticmethod
    def get_verification_code(email):
        """
        处理获取验证码请求。
        :param email: 邮箱地址
        :return: JSON 格式的响应结果
        """
        # 调用模型层的 handle_get_verification_code 函数获取验证码
        result = handle_get_verification_code(email)
        return result

    @staticmethod
    def get_forgot_password_code(email):
        """
        处理忘记密码时获取验证码的请求。
        :param email: 邮箱地址
        :return: JSON 格式的响应结果
        """
        # 调用模型层的 handle_forgot_password_get_code 函数
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
        # 调用模型层的 handle_forgot_password_reset 函数
        result = handle_forgot_password_reset(email, new_password, user_input_code)
        return result
