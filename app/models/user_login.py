"""用户的登录、注册信息、验证码存储到数据库"""
from datetime import datetime, timedelta
import mysql.connector
from flask import render_template_string
from mysql.connector import Error
import random
import string
import smtplib
import os
from dotenv import load_dotenv
import bcrypt

from app.utils import EmailTool
from app.utils.DrunkEmailTool import ContentType

# 加载环境变量
load_dotenv()

# 邮件配置（从 .env 文件中加载）
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# MySQL 数据库配置
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# 验证码模板
email_template = """<h1 style="color: #333; font-size: 24px;">欢迎注册</h1>
<p style="color: #666; font-size: 16px;">您的验证码是：</p>
<div class="verification-code" style="color: #007BFF; font-size: 20px; font-weight: bold;">{{ verification_code }}</div>
<p style="color: #666; font-size: 16px;">请在注册页面输入此验证码以完成注册。</p>
<p style="color: #666; font-size: 16px;">如果您没有请求此验证码，请忽略此邮件。</p>
<p style="color: #666; font-size: 16px;">此邮件由系统自动发送，请勿回复。</p>
"""

# 创建 MySQL 数据库连接
def create_mysql_connection():
    """
    创建到 MySQL 数据库的连接。
    :return: 数据库连接对象
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


# 创建用户表和验证码表
def create_database():
    """
    创建用户表和验证码表。
    """
    conn = create_mysql_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_codes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                code VARCHAR(6) NOT NULL,
                sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        conn.commit()
    except Error as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()


# 检查用户名或邮箱是否已存在
def check_user_exists(username=None, email=None):
    """
    检查用户名或邮箱是否已存在。
    :param username: 用户名（可选）
    :param email: 邮箱（可选）
    :return: 如果存在返回 True，否则返回 False
    """
    conn = create_mysql_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    try:
        if username and email:
            cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
        elif username:
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        elif email:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        exists = cursor.fetchone() is not None
        return exists
    except Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()


## 注册用户
def register_user(username, password, email):
    """
    向数据库中插入新用户。
    :param username: 用户名
    :param password: 密码（明文）
    :param email: 邮箱
    :return: 如果注册成功返回 True，否则返回 False
    """
    # 加密密码
    hashed_password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())
    # 检查用户名或邮箱是否已存在
    if check_user_exists(username=username, email=email):
        return {"status": "error", "message": "用户名或邮箱已被注册！"}

    conn = create_mysql_connection()
    if conn is None:
        return {"status": "error", "message": "数据库连接失败！"}

    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                       (username, hashed_password, email))
        conn.commit()
        return {"status": "success", "message": "注册成功！"}
    except Error as e:
        print(f"Error inserting user: {e}")
        return {"status": "error", "message": "注册失败！"}
    finally:
        conn.close()


# 发送验证码到邮箱
def send_verification_code(email, code):
    try:
        # 使用EmailTool
        email_tool = EmailTool(storage_type="env")
        # 替换占位符
        email_content = render_template_string(email_template, verification_code=code)
        # 设置邮件内容
        email_tool.set_message(subject="验证码", content=email_content, content_type=ContentType.HTML)
        # 发送邮件
        email_tool.send(email)

        print(f"验证码已发送至邮箱: {email}")
    except smtplib.SMTPRecipientsRefused:
        print(f"邮箱地址被拒绝: {email}")
        raise Exception("邮箱地址无效或被拒绝")
    except smtplib.SMTPAuthenticationError:
        print("SMTP认证失败，请检查邮箱账户和密码")
        raise Exception("SMTP认证失败")
    except Exception as e:
        print(f"发送邮件失败: {e}")
        raise Exception("邮件发送失败")
    else:
        insert_verification_code(email, code)  # 确保邮件发送成功后才插入数据库


# 生成随机验证码
def generate_code(length=6):
    """
    生成随机验证码。
    :param length: 验证码长度
    :return: 随机验证码字符串
    """
    return ''.join(random.choices(string.digits, k=length))


# 插入验证码到数据库
def insert_verification_code(email, code):
    """
    插入验证码到数据库。
    :param email: 邮箱地址
    :param code: 验证码
    """
    conn = create_mysql_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    try:
        # 设置验证码的过期时间为当前时间 + 10 分钟
        expires_at = datetime.now() + timedelta(minutes=10)
        cursor.execute('''
            INSERT INTO verification_codes (email, code, expires_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE code=%s, expires_at=%s
        ''', (email, code, expires_at, code, expires_at))
        conn.commit()
    except Error as e:
        print(f"Error inserting verification code: {e}")
    finally:
        conn.close()


# 验证验证码
def verify_verification_code(email, user_input_code):
    """
    验证用户输入的验证码。
    :param email: 邮箱地址
    :param user_input_code: 用户输入的验证码
    :return: 如果验证码有效返回 True，否则返回 False
    """
    conn = create_mysql_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT code, expires_at FROM verification_codes WHERE email=%s
        ''', (email,))
        row = cursor.fetchone()

        if row:
            stored_code, expires_at = row
            # 检查验证码是否匹配且未过期
            if stored_code == user_input_code and datetime.now() < expires_at:
                return True
        return False
    except Error as e:
        print(f"Error verifying verification code: {e}")
        return False
    finally:
        conn.close()


# 删除已使用的验证码
def delete_verification_code(email):
    """
    删除已使用的验证码。
    :param email: 邮箱地址
    """
    conn = create_mysql_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    try:
        cursor.execute('''
            DELETE FROM verification_codes WHERE email=%s
        ''', (email,))
        conn.commit()
    except Error as e:
        print(f"Error deleting verification code: {e}")
    finally:
        conn.close()


# 检查是否可以发送验证码
def can_send_verification_code(email):
    """
    检查是否可以发送验证码。
    :param email: 邮箱地址
    :return: 如果可以发送返回 True，否则返回 False
    """
    conn = create_mysql_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT sent_time FROM verification_codes WHERE email=%s
        ''', (email,))
        row = cursor.fetchone()

        if row:
            sent_time = row[0]
            # 如果距离上次发送时间不足 20 秒，则不允许发送
            if (datetime.now() - sent_time).total_seconds() < 20:
                return False
        return True
    except Error as e:
        print(f"Error checking verification code send limit: {e}")
        return False
    finally:
        conn.close()


# 获取验证码
def handle_get_verification_code(email):
    if check_user_exists(email=email):
        return {"status": "error", "message": "该邮箱已被注册！"}
    if not can_send_verification_code(email):
        return {"status": "error", "message": "验证码已发送，请稍后再试！"}
    code = generate_code()
    try:
        send_verification_code(email, code)
        insert_verification_code(email, code)  # 只有发送成功后才插入数据库
        return {"status": "success", "message": "验证码已发送，请查收邮箱！"}
    except Exception as e:
        print(f"验证码发送失败: {e}")
        return {"status": "error", "message": "验证码发送失败，请稍后再试！"}


# 用户注册
def handle_register(username, password, email, user_input_code):
    """
    处理用户注册请求。
    :param username: 用户名
    :param password: 密码（明文）
    :param email: 邮箱
    :param user_input_code: 用户输入的验证码
    :return: JSON 格式的响应结果
    """
    # 验证验证码
    if not verify_verification_code(email, user_input_code):
        return {"status": "error", "message": "验证码错误！"}

    # 检查用户名或邮箱是否已存在
    if check_user_exists(username=username, email=email):
        return {"status": "error", "message": "用户名或邮箱已被注册！"}

    # 注册用户
    result = register_user(username, password, email)
    if result["status"] == "success":
        # 删除已使用的验证码
        delete_verification_code(email)
        return {"status": "success", "message": "注册成功！"}
    else:
        return {"status": "error", "message": "注册失败！"}


# 用户登录
def handle_login(username, password):
    """
    处理用户登录请求。
    :param username: 用户名
    :param password: 密码（明文）
    :return: JSON 格式的响应结果
    """
    conn = create_mysql_connection()
    if conn is None:
        return {"status": "error", "message": "数据库连接失败！"}

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()

        if row:
            stored_password = row[0]
            # 验证密码
            if bcrypt.checkpw(password.encode('UTF-8'), stored_password.encode('UTF-8')):
                return {"status": "success", "message": "登录成功！"}
            else:
                return {"status": "error", "message": "用户名或密码错误！"}
        else:
            return {"status": "error", "message": "用户名或密码错误！"}
    except Error as e:
        print(f"Database error: {e}")
        return {"status": "error", "message": "登录失败！"}
    finally:
        conn.close()


# 忘记密码 - 获取验证码
def handle_forgot_password_get_code(email):
    """
    处理忘记密码时获取验证码的请求。
    :param email: 邮箱地址
    :return: JSON 格式的响应结果
    """
    # 检查邮箱是否已注册
    if not check_user_exists(email=email):
        return {"status": "error", "message": "该邮箱未注册！"}

    # 检查验证码发送频率限制
    if not can_send_verification_code(email):
        return {"status": "error", "message": "验证码已发送，请稍后再试！"}

    # 生成并发送验证码
    code = generate_code()
    try:
        send_verification_code(email, code)
        insert_verification_code(email, code)
        return {"status": "success", "message": "验证码已发送，请查收邮箱！"}
    except Exception as e:
        return {"status": "error", "message": f"验证码发送失败: {str(e)}"}


# 忘记密码 - 重置密码
def handle_forgot_password_reset(email, new_password, user_input_code):
    """
    处理忘记密码时重置密码的请求。
    :param email: 邮箱地址
    :param new_password: 新密码（明文）
    :param user_input_code: 用户输入的验证码
    :return: JSON 格式的响应结果
    """
    # 验证验证码
    if not verify_verification_code(email, user_input_code):
        return {"status": "error", "message": "验证码错误！"}

    # 加密新密码
    hashed_password = bcrypt.hashpw(new_password.encode('UTF-8'), bcrypt.gensalt())

    # 更新密码
    conn = create_mysql_connection()
    if conn is None:
        return {"status": "error", "message": "数据库连接失败！"}

    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_password, email))
        conn.commit()
        if cursor.rowcount > 0:
            delete_verification_code(email)  # 删除已使用的验证码
            return {"status": "success", "message": "密码重置成功！"}
        else:
            return {"status": "error", "message": "邮箱未找到！"}
    except Error as e:
        print(f"更新密码失败: {e}")
        return {"status": "error", "message": "密码重置失败！"}
    finally:
        conn.close()


# 通过用户名获取用户个人信息函数
def get_user_profile(username):
    """
    根据用户名获取用户的个人信息。
    :param username: 用户名
    :return: 如果用户存在，返回包含用户信息的字典；否则返回 None
    """
    conn = create_mysql_connection()
    if conn is None:
        return None

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, email FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()

        if row:
            # 构造返回的用户信息字典
            user_info = {
                "username": row[0],
                "email": row[1]
            }
            return user_info
        else:
            return None  # 用户不存在
    except Error as e:
        print(f"查询用户信息失败: {e}")
        return None
    finally:
        conn.close()
