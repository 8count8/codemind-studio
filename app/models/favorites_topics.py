"""收藏功能 - 支持 SQLite 和 PostgreSQL"""

from app.models.db import get_db_connection, fetch_dict, fetch_one_dict


def create_mysql_connection():
    """兼容旧接口"""
    return get_db_connection()


def add_favorite(user_id, title, question, difficulty, tags):
    """添加收藏到数据库"""
    valid_difficulties = ["简单", "中等", "困难"]

    if difficulty not in valid_difficulties:
        return {"error": f"Invalid difficulty. Valid values are: {valid_difficulties}"}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO favorites (user_id, question_id, question_title, question_content)
        VALUES (%s, %s, %s, %s)
        """, (user_id, title, title, question))
        conn.commit()
        conn.close()
        return {"message": "Favorite added successfully"}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def get_favorites_with_question(user_id):
    """获取收藏列表（包含题目内容）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, question_title AS title, question_content AS question, created_at
        FROM favorites
        WHERE user_id = %s
        ORDER BY created_at ASC
        """, (user_id,))
        results = fetch_dict(cursor)
        conn.close()
        return {"favorites": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def get_favorites_without_question(user_id):
    """获取收藏列表（不包含题目内容）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, question_title AS title, created_at
        FROM favorites
        WHERE user_id = %s
        ORDER BY created_at ASC
        """, (user_id,))
        results = fetch_dict(cursor)
        conn.close()
        return {"favorites": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def search_favorites_by_title(user_id, search_title):
    """根据标题搜索收藏"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, question_title AS title, question_content AS question, created_at
        FROM favorites
        WHERE user_id = %s AND question_title LIKE %s
        ORDER BY created_at ASC
        """, (user_id, f"%{search_title}%"))
        results = fetch_dict(cursor)
        conn.close()
        return {"favorites": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def delete_favorite(favorite_id, user_id):
    """删除收藏"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM favorites
        WHERE id = %s AND user_id = %s
        """, (favorite_id, user_id))
        conn.commit()
        if cursor.rowcount == 0:
            conn.close()
            return {"error": "Favorite not found"}, 404
        conn.close()
        return {"message": "Favorite deleted successfully"}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500