"""收藏功能 - Supabase PostgreSQL"""

from app.models.db import get_db_connection, fetch_dict, fetch_one_dict, VALID_DIFFICULTIES


def add_favorite(user_id, title, question, difficulty, tags):
    """添加收藏到数据库"""
    if difficulty not in VALID_DIFFICULTIES:
        return {"error": f"Invalid difficulty. Valid values are: {VALID_DIFFICULTIES}"}, 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO favorites (user_id, question_id, question_title, question_content)
        VALUES (%s, %s, %s, %s)
        """, (user_id, title, title, question))
        conn.commit()
        return {"message": "Favorite added successfully"}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def get_favorites_with_question(user_id):
    """获取收藏列表（包含题目内容）"""
    conn = None
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
        return {"favorites": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def get_favorites_without_question(user_id):
    """获取收藏列表（不包含题目内容）"""
    conn = None
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
        return {"favorites": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def search_favorites_by_title(user_id, search_title):
    """根据标题搜索收藏"""
    conn = None
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
        return {"favorites": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def delete_favorite(favorite_id, user_id):
    """删除收藏"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM favorites
        WHERE id = %s AND user_id = %s
        """, (favorite_id, user_id))
        conn.commit()
        if cursor.rowcount == 0:
            return {"error": "Favorite not found"}, 404
        return {"message": "Favorite deleted successfully"}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()