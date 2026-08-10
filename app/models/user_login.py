"""用户的登录、注册信息、验证码存储到 SQLite 数据库"""
from datetime import datetime, timedelta
from flask import render_template_string
import random
import string
import smtplib
import os
from dotenv import load_dotenv
import bcrypt

from app.utils import EmailTool
from app.utils.DrunkEmailTool import ContentType
from app.models.sqlite_db import get_db_connection, get_current_timestamp

# 加载环境变量
load_dotenv()

# 邮件配置（从 .env 文件中加载）
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# 验证码模板
email_template = """<h1 style="color: #333; font-size: 24px;">欢迎注册</h1>
<p style="color: #666; font-size: 16px;">您的验证码是：</p>
<div class="verification-code" style="color: #007BFF; font-size: 20px; font-weight: bold;">{{ verification_code }}</div>
<p style="color: #666; font-size: 16px;">请在注册页面输入此验证码以完成注册。</p>
<p style="color: #666; font-size: 16px;">如果您没有请求此验证码，请忽略此邮件。</p>
<p style="color: #666; font-size: 16px;">此邮件由系统自动发送，请勿回复。</p>
"""


def create_database():
    """创建用户表和验证码表（已在初始化模块完成）"""
    pass


# 检查用户名或邮箱是否已存在
def check_user_exists(username=None, email=None):
    """检查用户名或邮箱是否已存在"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if username and email:
            cursor.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
        elif username:
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        elif email:
            cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        row = cursor.fetchone()
        return row is not None
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()


# 注册用户
def register_user(username, password, email):
    """向数据库中插入新用户"""
    hashed_password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())

    if check_user_exists(username=username, email=email):
        return {"status": "error", "message": "用户名或邮箱已被注册！"}

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                       (username, hashed_password.decode('UTF-8'), email))
        conn.commit()
        return {"status": "success", "message": "注册成功！"}
    except Exception as e:
        print(f"Error inserting user: {e}")
        return {"status": "error", "message": "注册失败！"}
    finally:
        conn.close()


# 发送验证码到邮箱
def send_verification_code(email, code):
    try:
        email_tool = EmailTool(storage_type="env")
        email_content = render_template_string(email_template, verification_code=code)
        email_tool.set_message(subject="验证码", content=email_content, content_type=ContentType.HTML)
        email_tool.send(email)
        print(f"验证码已发送至邮箱: {email}")
    except smtplib.SMTPRecipientsRefused:
        raise Exception("邮箱地址无效或被拒绝")
    except smtplib.SMTPAuthenticationError:
        raise Exception("SMTP认证失败，请检查邮箱账户和密码")
    except Exception as e:
        print(f"发送邮件失败: {e}")
        raise Exception("邮件发送失败")
    else:
        insert_verification_code(email, code)


# 生成随机验证码
def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


# 插入验证码到数据库
def insert_verification_code(email, code):
    """插入验证码，如已存在则更新"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        expires_at = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO verification_codes (email, code, expires_at)
            VALUES (?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET code=?, expires_at=?
        ''', (email, code, expires_at, code, expires_at))
        conn.commit()
    except Exception as e:
        print(f"Error inserting verification code: {e}")
    finally:
        conn.close()


# 验证验证码
def verify_verification_code(email, user_input_code):
    """验证用户输入的验证码"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT code, expires_at FROM verification_codes WHERE email=?
        ''', (email,))
        row = cursor.fetchone()

        if row:
            stored_code = row['code']
            expires_at = row['expires_at']
            if stored_code == user_input_code and datetime.now().strftime('%Y-%m-%d %H:%M:%S') < expires_at:
                return True
        return False
    except Exception as e:
        print(f"Error verifying verification code: {e}")
        return False
    finally:
        conn.close()


# 删除已使用的验证码
def delete_verification_code(email):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM verification_codes WHERE email=?', (email,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting verification code: {e}")
    finally:
        conn.close()


# 检查是否可以发送验证码
def can_send_verification_code(email):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT sent_time FROM verification_codes WHERE email=?', (email,))
        row = cursor.fetchone()

        if row:
            sent_time = row['sent_time']
            if sent_time:
                sent_datetime = datetime.strptime(sent_time, '%Y-%m-%d %H:%M:%S')
                if (datetime.now() - sent_datetime).total_seconds() < 20:
                    return False
        return True
    except Exception as e:
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
        return {"status": "success", "message": "验证码已发送，请查收邮箱！"}
    except Exception as e:
        print(f"验证码发送失败: {e}")
        return {"status": "error", "message": "验证码发送失败，请稍后再试！"}


# 用户注册
def handle_register(username, password, email, user_input_code):
    if not verify_verification_code(email, user_input_code):
        return {"status": "error", "message": "验证码错误！"}
    if check_user_exists(username=username, email=email):
        return {"status": "error", "message": "用户名或邮箱已被注册！"}
    result = register_user(username, password, email)
    if result["status"] == "success":
        delete_verification_code(email)
        return {"status": "success", "message": "注册成功！"}
    else:
        return {"status": "error", "message": "注册失败！"}


# 用户登录
def handle_login(username, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        row = cursor.fetchone()

        if row:
            stored_password = row['password']
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('UTF-8')
            if bcrypt.checkpw(password.encode('UTF-8'), stored_password):
                return {"status": "success", "message": "登录成功！"}
            else:
                return {"status": "error", "message": "用户名或密码错误！"}
        else:
            return {"status": "error", "message": "用户名或密码错误！"}
    except Exception as e:
        print(f"Database error: {e}")
        return {"status": "error", "message": "登录失败！"}
    finally:
        conn.close()


# 忘记密码 - 获取验证码
def handle_forgot_password_get_code(email):
    if not check_user_exists(email=email):
        return {"status": "error", "message": "该邮箱未注册！"}
    if not can_send_verification_code(email):
        return {"status": "error", "message": "验证码已发送，请稍后再试！"}
    code = generate_code()
    try:
        send_verification_code(email, code)
        return {"status": "success", "message": "验证码已发送，请查收邮箱！"}
    except Exception as e:
        return {"status": "error", "message": f"验证码发送失败: {str(e)}"}


# 忘记密码 - 重置密码
def handle_forgot_password_reset(email, new_password, user_input_code):
    if not verify_verification_code(email, user_input_code):
        return {"status": "error", "message": "验证码错误！"}
    hashed_password = bcrypt.hashpw(new_password.encode('UTF-8'), bcrypt.gensalt())

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password=? WHERE email=?", (hashed_password.decode('UTF-8'), email))
        conn.commit()
        if cursor.rowcount > 0:
            delete_verification_code(email)
            return {"status": "success", "message": "密码重置成功！"}
        else:
            return {"status": "error", "message": "邮箱未找到！"}
    except Exception as e:
        print(f"更新密码失败: {e}")
        return {"status": "error", "message": "密码重置失败！"}
    finally:
        conn.close()


# 通过用户名获取用户个人信息
def get_user_profile(username):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username, email FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        if row:
            return {"username": row['username'], "email": row['email']}
        else:
            return None
    except Exception as e:
        print(f"查询用户信息失败: {e}")
        return None
    finally:
        conn.close()