"""收藏功能 - SQLite 版本"""

from app.models.sqlite_db import get_db_connection


def add_favorite(user_id, title, question, difficulty, tags):
    """添加收藏到数据库"""
    valid_difficulties = ["简单", "中等", "困难"]

    if difficulty not in valid_difficulties:
        return {"error": f"Invalid difficulty. Valid values are: {valid_difficulties}"}, 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO favorites (user_id, question_id, question_title, question_content, created_at)
        VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
        """, (user_id, title, title, question))
        connection.commit()
        connection.close()
        return {"message": "Favorite added successfully"}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def get_favorites_with_question(user_id):
    """获取收藏列表（包含题目内容）"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
        SELECT id, question_title as title, question_content as question, created_at
        FROM favorites
        WHERE user_id = ?
        ORDER BY created_at ASC
        """, (user_id,))
        results = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return {"favorites": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def get_favorites_without_question(user_id):
    """获取收藏列表（不包含题目内容）"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
        SELECT id, question_title as title, created_at
        FROM favorites
        WHERE user_id = ?
        ORDER BY created_at ASC
        """, (user_id,))
        results = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return {"favorites": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def search_favorites_by_title(user_id, title=None):
    """根据标题搜索收藏"""
    if not title:
        return {"error": "'title' must be provided"}, 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT id, question_title as title, question_content as question, created_at 
        FROM favorites 
        WHERE user_id = ?
        """
        params = [user_id]

        if title:
            query += " AND question_title LIKE ?"
            params.append(f"%{title}%")

        query += " ORDER BY created_at ASC"

        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return {"favorites": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def delete_favorite(user_id, title):
    """删除收藏"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
        DELETE FROM favorites
        WHERE user_id = ? AND question_title = ?
        """, (user_id, title))
        connection.commit()

        if cursor.rowcount == 0:
            connection.close()
            return {"error": "Favorite not found or already deleted"}, 404

        connection.close()
        return {"message": "Favorite deleted successfully"}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


# 兼容旧接口
create_mysql_connection = get_db_connection