"""用户代码保存 - MySQL"""

from app.models.db import get_db_connection


def save_code_to_db(title, language, code_content, user_id=None):
    """保存用户代码到数据库

    answer_records.user_id 为 NOT NULL，必须在调用前显式传入已登录用户的 user_id，
    否则直接返回 400 错误，避免触发数据库 NOT NULL 约束异常。
    """
    if user_id is None:
        return {"error": "Missing required parameter: user_id"}, 400

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO answer_records (user_id, question_id, user_answer, is_correct, created_at)
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (user_id, title, code_content, 0))
        connection.commit()
        return {"message": "Code saved successfully"}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
