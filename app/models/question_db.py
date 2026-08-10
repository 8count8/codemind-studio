"""
该文件包含所有底层数据库操作函数。
这些函数负责直接与 MySQL 数据库交互，执行增删改查等操作。
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量中获取 MySQL 配置信息
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


def create_mysql_connection():
    """
    创建到 MySQL 数据库的连接。
    :return: 如果成功，返回数据库连接对象；如果失败，返回 None。
    """
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


def dict_to_markdown(content_dict):
    """
    将字典格式的内容转换为 Markdown 格式的字符串。
    :param content_dict: 题目内容（字典格式）
    :return: Markdown 格式的字符串
    """
    markdown_content = ""
    for section, text in content_dict.items():
        if isinstance(text, list):  # 处理示例部分
            markdown_content += f"### {section}\n"
            for example in text:
                markdown_content += f"- {example}\n"
        else:
            markdown_content += f"### {section}\n{text}\n\n"
    return markdown_content.strip()


def get_all_questions():
    """
    获取所有题目的列表。
    :return: 题目列表（成功或错误信息）
    """
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = connection.cursor(dictionary=True)
        select_query = """
        SELECT id, title, difficulty, tags, created_at
        FROM problems
        ORDER BY created_at ASC
        """
        cursor.execute(select_query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"questions": results}, 200
    except Error as e:
        return {"error": f"Database error: {str(e)}"}, 500



def get_question_by_id(question_id):
    """
    根据 ID 获取题目详情。
    :param question_id: 题目 ID
    :return: 题目详情（成功或错误信息）
    """
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = connection.cursor(dictionary=True)
        select_query = """
        SELECT id, title, content, difficulty, tags, created_at
        FROM problems
        WHERE id = %s
        """
        cursor.execute(select_query, (question_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        if result:
            return {"question": result}, 200
        else:
            return {"error": "Question not found"}, 404
    except Error as e:
        return {"error": f"Database error: {str(e)}"}, 500


def search_questions_by_title(title=None):
    """
    根据标题搜索题目（支持模糊匹配）。
    :param title: 搜索标题
    :return: 搜索结果（成功或错误信息）
    """
    if not title:
        return {"error": "'title' must be provided"}, 400

    connection = create_mysql_connection()
    if connection is None:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT id, title, content, difficulty, tags, created_at
        FROM problems
        WHERE title LIKE %s
        ORDER BY created_at ASC
        """
        cursor.execute(query, (f"%{title}%",))
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"questions": results}, 200
    except Error as e:
        return {"error": f"Database error: {str(e)}"}, 500


def update_question(question_id, title=None, difficulty=None, tags=None, content=None):
    """
    更新指定题目的信息。
    :param question_id: 题目 ID
    :param title: 新的标题（可选）
    :param difficulty: 新的难度（可选）
    :param tags: 新的标签列表（可选）
    :param content: 新的题目内容（Markdown 格式，可选）
    :return: 操作结果（成功或错误信息）
    """
    # 合法的难度值
    valid_difficulties = ["简单", "中等", "困难"]

    # 验证 difficulty 是否合法
    if difficulty and difficulty not in valid_difficulties:
        return {"error": f"Invalid difficulty. Valid values are: {valid_difficulties}"}, 400

    connection = create_mysql_connection()
    if connection is None:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = connection.cursor()
        update_query = """
        UPDATE problems
        SET
            title = COALESCE(%s, title),
            difficulty = COALESCE(%s, difficulty),
            tags = COALESCE(%s, tags),
            content = COALESCE(%s, content)
        WHERE id = %s
        """
        cursor.execute(update_query, (title, difficulty, tags, content, question_id))
        connection.commit()

        if cursor.rowcount == 0:
            return {"error": "Question not found or no changes made"}, 404

        cursor.close()
        connection.close()
        return {"message": "Question updated successfully"}, 200
    except Error as e:
        return {"error": f"Database error: {str(e)}"}, 500


def insert_question(title, content_dict, difficulty, tags):
    """
    插入新题目。
    :param title: 标题
    :param content_dict: 内容（字典格式）
    :param difficulty: 难度（中文）
    :param tags: 标签列表
    :return: 操作结果（成功或错误信息）
    """
    # 合法的难度值
    valid_difficulties = ["简单", "中等", "困难"]

    # 验证 difficulty 是否合法
    if difficulty not in valid_difficulties:
        return {"error": f"Invalid difficulty. Valid values are: {valid_difficulties}"}, 400

    # 将字典格式的内容转换为 Markdown 格式
    content = dict_to_markdown(content_dict)

    connection = create_mysql_connection()
    if connection is None:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO problems (title, content, difficulty, tags)
        VALUES (%s, %s, %s, %s)
        """
        data = (title, content, difficulty, tags)
        cursor.execute(insert_query, data)
        connection.commit()

        cursor.close()
        connection.close()
        return {"message": "Question inserted successfully"}, 201
    except Error as e:
        return {"error": f"Database error: {str(e)}"}, 500