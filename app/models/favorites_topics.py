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


def add_favorite(user_id, title, question, difficulty, tags):
    """
    添加收藏到数据库。
    :param user_id: 用户 ID
    :param title: 收藏标题
    :param question: 题目内容（Markdown 格式）
    :param difficulty: 难度等级
    :param tags: 标签列表（JSON 格式）
    :return: 操作结果（成功或错误信息）
    """
    # 合法的难度值
    valid_difficulties = ["简单", "中等", "困难"]

    # 验证 difficulty 是否合法
    if difficulty not in valid_difficulties:
        return {"error": f"Invalid difficulty. Valid values are: {valid_difficulties}"}, 400

    # 尝试创建数据库连接
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = connection.cursor()
        # 插入数据到 collections 表
        insert_query = """
        INSERT INTO collections (user_id, title, question, difficulty, tags, favorite)
        VALUES (%s, %s, %s, %s, %s, TRUE)
        """
        cursor.execute(insert_query, (user_id, title, question, difficulty, tags))
        connection.commit()  # 提交事务
        cursor.close()
        connection.close()
        return {"message": "Favorite added successfully"}, 200
    except Error as e:
        return {"error": f"Database error: {str(e)}"}, 500


def get_favorites_with_question(user_id):
    """
    获取按时间排序的收藏列表（包含题目具体内容）。
    :param user_id: 用户 ID
    :return: 收藏列表（成功或错误信息）
    """
    # 尝试创建数据库连接
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = connection.cursor(dictionary=True)  # 返回字典格式的结果
        # 查询用户的所有收藏（含题目内容）
        select_query = """
        SELECT title, question, difficulty, tags, created_at
        FROM collections
        WHERE user_id = %s AND favorite = TRUE
        ORDER BY created_at ASC
        """
        cursor.execute(select_query, (user_id,))
        results = cursor.fetchall()  # 获取所有结果
        cursor.close()
        connection.close()
        return {"favorites": results}, 200
    except Error as e:
        return {"error": f"Database error: {str(e)}"}, 500


def get_favorites_without_question(user_id):
    """
    获取按时间排序的收藏列表（不包含题目具体内容）。
    :param user_id: 用户 ID
    :return: 收藏列表（成功或错误信息）
    """
    # 尝试创建数据库连接
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = connection.cursor(dictionary=True)  # 返回字典格式的结果
        # 查询用户的所有收藏（不含题目内容）
        select_query = """
        SELECT title, difficulty, tags, created_at
        FROM collections
        WHERE user_id = %s AND favorite = TRUE
        ORDER BY created_at ASC
        """
        cursor.execute(select_query, (user_id,))
        results = cursor.fetchall()  # 获取所有结果
        cursor.close()
        connection.close()
        return {"favorites": results}, 200
    except Error as e:
        return {"error": f"Database error: {str(e)}"}, 500


def search_favorites_by_title(user_id, title=None):
    """
    根据标题进行高级搜索（支持模糊匹配）。
    :param user_id: 用户 ID
    :param title: 搜索标题（可选）
    :return: 搜索结果（成功或错误信息）
    """
    # 检查是否提供了搜索标题
    if not title:
        return {"error": "'title' must be provided"}, 400

    # 尝试创建数据库连接
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = connection.cursor(dictionary=True)  # 返回字典格式的结果

        # 构造动态 SQL 查询
        query = """
        SELECT title, question, difficulty, tags, created_at 
        FROM collections 
        WHERE user_id = %s AND favorite = TRUE
        """
        params = [user_id]

        if title:
            query += " AND title LIKE %s"
            params.append(f"%{title}%")  # 模糊匹配标题

        query += " ORDER BY created_at ASC"

        cursor.execute(query, params)
        results = cursor.fetchall()  # 获取所有结果
        cursor.close()
        connection.close()
        return {"favorites": results}, 200
    except Error as e:
        return {"error": f"Database error: {str(e)}"}, 500


def delete_favorite(user_id, title):
    """
    根据用户 ID 和标题删除收藏题目。
    :param user_id: 用户 ID
    :param title: 收藏标题
    :return: 操作结果（成功或错误信息）
    """
    # 尝试创建数据库连接
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = connection.cursor()
        # 删除指定用户的收藏题目
        delete_query = """
        DELETE FROM collections
        WHERE user_id = %s AND title = %s AND favorite = TRUE
        """
        cursor.execute(delete_query, (user_id, title))
        connection.commit()  # 提交事务

        # 检查是否删除成功
        if cursor.rowcount == 0:
            return {"error": "Favorite not found or already deleted"}, 404

        cursor.close()
        connection.close()
        return {"message": "Favorite deleted successfully"}, 200
    except Error as e:
        return {"error": f"Database error: {str(e)}"}, 500