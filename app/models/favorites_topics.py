"""收藏功能 - MySQL"""

from app.models.db import get_db_connection, fetch_dict, fetch_one_dict, VALID_DIFFICULTIES
from app.models.learning_model import _ensure_extended_schema


def add_favorite(user_id, title, question, difficulty, tags):
    """添加收藏到数据库"""
    if difficulty not in VALID_DIFFICULTIES:
        return {"error": f"Invalid difficulty. Valid values are: {VALID_DIFFICULTIES}"}, 400

    conn = None
    try:
        conn = get_db_connection()
        _ensure_extended_schema(conn)
        cursor = conn.cursor()
        # 新前端传入 question_id；旧调用仍可传题目标题并携带内容。
        cursor.execute(
            "SELECT id, title, content FROM problems WHERE id = %s LIMIT 1",
            (title,),
        )
        problem = cursor.fetchone()
        question_id = problem[0] if problem else title
        question_title = problem[1] if problem else str(title)
        question_content = problem[2] if problem else question
        cursor.execute(
            "SELECT id FROM favorites WHERE user_id = %s AND question_id = %s LIMIT 1",
            (user_id, str(question_id)),
        )
        if cursor.fetchone():
            return {"message": "Favorite already exists"}, 200
        cursor.execute("""
        INSERT INTO favorites (user_id, question_id, question_title, question_content)
        VALUES (%s, %s, %s, %s)
        """, (user_id, str(question_id), question_title, question_content))
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
        _ensure_extended_schema(conn)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT CAST(f.question_id AS UNSIGNED) AS id, f.id AS favorite_id,
               COALESCE(p.title, f.question_title) AS title,
               COALESCE(p.content, f.question_content) AS question,
               p.difficulty, p.tags, f.created_at, f.topic_id, t.name AS topic_name
        FROM favorites f
        LEFT JOIN problems p ON p.id = CAST(f.question_id AS UNSIGNED)
        LEFT JOIN favorite_topics t ON t.id = f.topic_id
        WHERE f.user_id = %s
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
        _ensure_extended_schema(conn)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT CAST(f.question_id AS UNSIGNED) AS id, f.id AS favorite_id,
               COALESCE(p.title, f.question_title) AS title,
               p.difficulty, p.tags, f.created_at, f.topic_id, t.name AS topic_name
        FROM favorites f
        LEFT JOIN problems p ON p.id = CAST(f.question_id AS UNSIGNED)
        LEFT JOIN favorite_topics t ON t.id = f.topic_id
        WHERE f.user_id = %s
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


def delete_favorite(question_or_favorite_id, user_id):
    """删除收藏"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM favorites
        WHERE user_id = %s AND (question_id = %s OR id = %s)
        """, (user_id, str(question_or_favorite_id), question_or_favorite_id))
        conn.commit()
        if cursor.rowcount == 0:
            return {"error": "Favorite not found"}, 404
        return {"message": "Favorite deleted successfully"}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()
