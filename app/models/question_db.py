"""题库管理 - SQLite 版本"""

import json
import logging

from app.models.sqlite_db import get_db_connection

logging.basicConfig(level=logging.INFO)


def create_mysql_connection():
    """兼容旧接口"""
    return get_db_connection()


def dict_to_markdown(content_dict):
    """将字典格式转换为 Markdown"""
    if isinstance(content_dict, str):
        return content_dict

    markdown_content = ""
    for section, text in content_dict.items():
        if isinstance(text, list):
            markdown_content += f"### {section}\n"
            for example in text:
                markdown_content += f"- {example}\n"
        else:
            markdown_content += f"### {section}\n{text}\n\n"
    return markdown_content.strip()


def get_all_questions():
    """获取所有题目列表"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
        SELECT id, title, difficulty, tags, created_at
        FROM problems
        ORDER BY created_at ASC
        """)
        results = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return {"questions": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def get_question_by_id(question_id):
    """根据 ID 获取题目详情"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
        SELECT id, title, content, difficulty, tags, created_at
        FROM problems
        WHERE id = ?
        """, (question_id,))
        result = cursor.fetchone()
        connection.close()
        if result:
            return {"question": dict(result)}, 200
        else:
            return {"error": "Question not found"}, 404
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def search_questions_by_title(title=None):
    """根据标题搜索题目"""
    if not title:
        return {"error": "'title' must be provided"}, 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
        SELECT id, title, content, difficulty, tags, created_at
        FROM problems
        WHERE title LIKE ?
        ORDER BY created_at ASC
        """, (f"%{title}%",))
        results = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return {"questions": results}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def update_question(question_id, title=None, difficulty=None, tags=None, content=None):
    """更新题目信息"""
    valid_difficulties = ["简单", "中等", "困难"]
    if difficulty and difficulty not in valid_difficulties:
        return {"error": f"Invalid difficulty. Valid values are: {valid_difficulties}"}, 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if difficulty is not None:
            updates.append("difficulty = ?")
            params.append(difficulty)
        if tags is not None:
            updates.append("tags = ?")
            params.append(tags)
        if content is not None:
            updates.append("content = ?")
            params.append(content)

        if not updates:
            connection.close()
            return {"message": "No changes needed"}, 200

        params.append(question_id)
        query = f"UPDATE problems SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        connection.commit()

        if cursor.rowcount == 0:
            connection.close()
            return {"error": "Question not found or no changes made"}, 404

        connection.close()
        return {"message": "Question updated successfully"}, 200
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500


def insert_question(title, content_dict, difficulty, tags):
    """插入新题目"""
    valid_difficulties = ["简单", "中等", "困难"]
    if difficulty not in valid_difficulties:
        return {"error": f"Invalid difficulty. Valid values are: {valid_difficulties}"}, 400

    content = dict_to_markdown(content_dict)

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO problems (title, content, difficulty, tags, created_at)
        VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
        """, (title, content, difficulty, tags))
        connection.commit()
        connection.close()
        return {"message": "Question inserted successfully"}, 201
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500