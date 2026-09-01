"""用户登录/注册 - MySQL"""
from datetime import datetime, timedelta
from flask import render_template_string
import string
import smtplib
import os
import secrets
from dotenv import load_dotenv
import bcrypt

from app.utils import EmailTool
from app.utils.DrunkEmailTool import ContentType
from app.models.db import get_db_connection, get_current_timestamp, fetch_one_dict

load_dotenv()

email_template = """<h1 style="color: #333; font-size: 24px;">欢迎注册</h1>
<p style="color: #666; font-size: 16px;">您的验证码是：</p>
<div class="verification-code" style="color: #007BFF; font-size: 20px; font-weight: bold;">{{ verification_code }}</div>
<p style="color: #666; font-size: 16px;">请在注册页面输入此验证码以完成注册。</p>
<p style="color: #666; font-size: 16px;">如果您没有请求此验证码，请忽略此邮件。</p>
<p style="color: #666; font-size: 16px;">此邮件由系统自动发送，请勿回复。</p>
"""


def check_user_exists(username=None, email=None):
    """检查用户名或邮箱是否已存在"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if username and email:
            cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
        elif username:
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        elif email:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        row = cursor.fetchone()
        return row is not None
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def register_user(username, password, email):
    """注册新用户"""
    hashed_password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt(rounds=12))

    if check_user_exists(username=username, email=email):
        return {"status": "error", "message": "用户名或邮箱已被注册！"}

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                       (username, hashed_password.decode('UTF-8'), email))
        conn.commit()
        return {"status": "success", "message": "注册成功！"}
    except Exception as e:
        print(f"Error inserting user: {e}")
        return {"status": "error", "message": "注册失败！"}
    finally:
        if conn:
            conn.close()


def send_verification_code(email, code):
    try:
        print(f"[EMAIL] 准备发送验证码: email={email}, code={code}")
        email_tool = EmailTool(storage_type="env")
        print(f"[EMAIL] EmailTool 初始化成功: host={email_tool.email_server_host}, port={email_tool.email_server_port}")
        email_content = render_template_string(email_template, verification_code=code)
        email_tool.set_message(subject="验证码", content=email_content, content_type=ContentType.HTML)
        print(f"[EMAIL] 开始发送邮件...")
        email_tool.send(email)
        print(f"[EMAIL] 验证码已发送至邮箱: {email}")
    except smtplib.SMTPRecipientsRefused:
        raise Exception("邮箱地址无效或被拒绝")
    except smtplib.SMTPAuthenticationError:
        raise Exception("SMTP认证失败，请检查邮箱账户和密码")
    except Exception as e:
        print(f"[EMAIL] 发送邮件失败: {type(e).__name__}: {e}")
        raise Exception(f"邮件发送失败: {str(e)}")
    else:
        insert_verification_code(email, code)


def generate_code(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def insert_verification_code(email, code):
    """插入验证码"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        expires_at = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            INSERT INTO verification_codes (email, code, expires_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE code=%s, expires_at=%s
        ''', (email, code, expires_at, code, expires_at))
        conn.commit()
    except Exception as e:
        print(f"Error inserting verification code: {e}")
    finally:
        if conn:
            conn.close()


def verify_verification_code(email, user_input_code):
    """验证用户输入的验证码"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT code, expires_at FROM verification_codes WHERE email=%s', (email,))
        row = cursor.fetchone()

        if row:
            stored_code = str(row[0]) if row[0] else ''
            expires_at = row[1]

            # 恒定时间比较，防止时序攻击
            if not secrets.compare_digest(stored_code, user_input_code):
                return False

            # 用 datetime 对象比较过期时间，避免字符串比较的脆弱性
            if expires_at is None:
                return False
            if hasattr(expires_at, 'tzinfo'):
                # MySQL 返回的 datetime 对象，直接比较
                now = datetime.now(expires_at.tzinfo) if expires_at.tzinfo else datetime.now()
            else:
                now = datetime.now()
            if now < expires_at:
                return True
        return False
    except Exception as e:
        print(f"Error verifying verification code: {e}")
        return False
    finally:
        if conn:
            conn.close()


def delete_verification_code(email):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM verification_codes WHERE email=%s', (email,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting verification code: {e}")
    finally:
        if conn:
            conn.close()


def can_send_verification_code(email):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT sent_time FROM verification_codes WHERE email=%s', (email,))
        row = cursor.fetchone()

        if row:
            sent_time = row[0]
            if sent_time:
                if hasattr(sent_time, 'strftime'):
                    sent_str = sent_time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    sent_str = str(sent_time)
                sent_datetime = datetime.strptime(sent_str, '%Y-%m-%d %H:%M:%S')
                if (datetime.now() - sent_datetime).total_seconds() < 20:
                    return False
        return True
    except Exception as e:
        print(f"Error checking verification code send limit: {e}")
        return False
    finally:
        if conn:
            conn.close()


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
        print(f"[EMAIL] handle_get_verification_code 异常: {type(e).__name__}: {e}")
        return {"status": "error", "message": f"验证码发送失败: {str(e)}"}


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


def handle_login(username, password):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password FROM users WHERE username=%s OR email=%s LIMIT 1",
            (username, username),
        )
        row = cursor.fetchone()

        if row:
            user_id, canonical_username, stored_password = row
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('UTF-8')
            if bcrypt.checkpw(password.encode('UTF-8'), stored_password):
                # 更新最后登录时间
                cursor.execute("UPDATE users SET last_login = %s WHERE id = %s",
                               (datetime.now(), user_id))
                conn.commit()
                return {
                    "status": "success",
                    "message": "登录成功！",
                    "user_id": user_id,
                    "username": canonical_username,
                }
            else:
                return {"status": "error", "message": "用户名或密码错误！"}
        else:
            return {"status": "error", "message": "用户名或密码错误！"}
    except Exception as e:
        print(f"Database error: {e}")
        return {"status": "error", "message": "登录失败！"}
    finally:
        if conn:
            conn.close()


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


def handle_forgot_password_reset(email, new_password, user_input_code):
    if not verify_verification_code(email, user_input_code):
        return {"status": "error", "message": "验证码错误！"}
    hashed_password = bcrypt.hashpw(new_password.encode('UTF-8'), bcrypt.gensalt(rounds=12))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password=%s WHERE email=%s", 
                       (hashed_password.decode('UTF-8'), email))
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
        if conn:
            conn.close()


def get_user_profile(username):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, created_at, last_login FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
        if row:
            return {
                "username": row[0],
                "email": row[1],
                "created_at": str(row[2]) if row[2] else None,
                "last_login": str(row[3]) if row[3] else None
            }
        else:
            return None
    except Exception as e:
        print(f"查询用户信息失败: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_user_profile_by_id(user_id):
    """按数据库主键查询个人资料与学习概览。"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, created_at, last_login FROM users WHERE id=%s",
            (user_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        cursor.execute(
            """SELECT
                 (SELECT COUNT(*) FROM answer_records WHERE user_id=%s),
                 (SELECT COUNT(*) FROM user_uploads WHERE user_id=%s),
                 (SELECT COUNT(*) FROM favorites WHERE user_id=%s),
                 (SELECT COUNT(*) FROM ability_submissions WHERE user_id=%s)""",
            (user_id, user_id, user_id, user_id),
        )
        stats = cursor.fetchone() or (0, 0, 0, 0)
        return {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "created_at": str(row[3]) if row[3] else None,
            "last_login": str(row[4]) if row[4] else None,
            "stats": {
                "answers": int(stats[0] or 0),
                "submissions": int(stats[1] or 0),
                "favorites": int(stats[2] or 0),
                "evaluations": int(stats[3] or 0),
            },
        }
    except Exception as e:
        print(f"按 ID 查询用户信息失败: {e}")
        return None
    finally:
        if conn:
            conn.close()


def update_user_profile(user_id, username, email):
    """更新用户名与邮箱，唯一性由数据库约束保证。"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET username=%s, email=%s WHERE id=%s",
            (username, email, user_id),
        )
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        if conn:
            conn.rollback()
        message = "用户名或邮箱已被使用" if "Duplicate" in str(e) else f"更新失败: {e}"
        return {"status": "error", "message": message}
    finally:
        if conn:
            conn.close()
