import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
# 加载环境变量
load_dotenv()
# MySQL 数据库配置
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


# 创建 MySQL 数据库连接
def create_mysql_connection():
    """
    创建到 MySQL 数据库的连接。
    :return: 数据库连接对象
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

# 插入用户代码到数据库
def save_code_to_db(title, language, code_content):
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "Database connection failed"}, 500

    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO user_code (title, language, code_content)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (title, language, code_content))
        connection.commit()
        cursor.close()
        connection.close()
        return {"message": "Code saved successfully"}, 200
    except Error as e:
        return {"error": f"Database error: {str(e)}"}, 500
