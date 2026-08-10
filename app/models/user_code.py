"""用户代码保存 - SQLite 版本"""

from app.models.sqlite_db import get_db_connection


def create_mysql_connection():
    """创建数据库连接（兼容旧接口）"""
    return get_db_connection()


def save_code_to_db(title, language, code_content):
    """保存用户代码到数据库"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO answer_records (question_id, question_title, user_answer, is_correct, created_at)
        VALUES (?, ?, ?, 0, datetime('now', 'localtime'))
        """, (title, title, code_content))
        connection.commit()
        connection.close()
        return {"message": "Code saved successfully"}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500