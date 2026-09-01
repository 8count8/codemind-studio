"""题库管理 - MySQL"""

import json
import logging
import threading
import time

from app.models.db import get_db_connection, fetch_dict, fetch_one_dict, dict_to_markdown, VALID_DIFFICULTIES

logging.basicConfig(level=logging.INFO)

_question_cache_lock = threading.Lock()
_question_cache = None
_question_cache_expires_at = 0.0
_QUESTION_CACHE_TTL_SECONDS = 30


def clear_question_cache():
    """Invalidate the short-lived list cache after a question mutation."""
    global _question_cache, _question_cache_expires_at
    with _question_cache_lock:
        _question_cache = None
        _question_cache_expires_at = 0.0


def get_all_questions():
    """获取所有题目列表"""
    global _question_cache, _question_cache_expires_at
    now = time.monotonic()
    if _question_cache is not None and now < _question_cache_expires_at:
        return {"questions": list(_question_cache)}, 200
    conn = None
    with _question_cache_lock:
        now = time.monotonic()
        if _question_cache is not None and now < _question_cache_expires_at:
            return {"questions": list(_question_cache)}, 200
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, title, difficulty, tags, created_at
            FROM problems
            ORDER BY created_at ASC
            """)
            results = fetch_dict(cursor)
            _question_cache = tuple(results)
            _question_cache_expires_at = time.monotonic() + _QUESTION_CACHE_TTL_SECONDS
            return {"questions": list(_question_cache)}, 200
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}, 500
        finally:
            if conn:
                conn.close()


def get_question_by_id(question_id):
    """根据 ID 获取题目详情"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, title, content, difficulty, tags, created_at
        FROM problems
        WHERE id = %s
        """, (question_id,))
        result = fetch_one_dict(cursor)
        if result:
            return {"question": result}, 200
        else:
            return {"error": "Question not found"}, 404
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def search_questions_by_title(title=None):
    """根据标题搜索题目"""
    if not title:
        return {"error": "'title' must be provided"}, 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, title, content, difficulty, tags, created_at
        FROM problems
        WHERE title LIKE %s
        ORDER BY created_at ASC
        """, (f"%{title}%",))
        results = fetch_dict(cursor)
        return {"questions": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def update_question(question_id, title=None, difficulty=None, tags=None, content=None):
    """更新题目信息"""
    if difficulty and difficulty not in VALID_DIFFICULTIES:
        return {"error": f"Invalid difficulty. Valid values are: {VALID_DIFFICULTIES}"}, 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        updates = []
        params = []
        if title is not None:
            updates.append("title = %s")
            params.append(title)
        if difficulty is not None:
            updates.append("difficulty = %s")
            params.append(difficulty)
        if tags is not None:
            updates.append("tags = %s")
            params.append(tags)
        if content is not None:
            updates.append("content = %s")
            params.append(content)

        if not updates:
            return {"message": "No changes needed"}, 200

        params.append(question_id)
        query = f"UPDATE problems SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, params)
        conn.commit()
        clear_question_cache()

        if cursor.rowcount == 0:
            return {"error": "Question not found or no changes made"}, 404

        return {"message": "Question updated successfully"}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def insert_question(title, content_dict, difficulty, tags):
    """插入新题目"""
    if difficulty not in VALID_DIFFICULTIES:
        return {"error": f"Invalid difficulty. Valid values are: {VALID_DIFFICULTIES}"}, 400

    content = dict_to_markdown(content_dict)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO problems (title, content, difficulty, tags)
        VALUES (%s, %s, %s, %s)
        """, (title, content, difficulty, tags))
        conn.commit()
        clear_question_cache()
        return {"message": "Question inserted successfully"}, 201
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()
