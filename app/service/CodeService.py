import json
import os
import mysql.connector
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# MySQL 数据库配置
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))  # 确保端口是整数
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_db_connection():
    """
    创建并返回一个 MySQL 数据库连接。
    """
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset="utf8mb4"
        )
        if connection.is_connected():
            logging.info("数据库连接成功")
        return connection
    except mysql.connector.Error as e:
        logging.error(f"数据库连接失败: {e}")
        raise


def get_test_cases(problem_id: int) -> list:
    connection = None
    cursor = None
    test_cases = []

    # 获取数据库连接
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # 使用字典游标以便直接获取字段名和值

    # 查询测试用例
    query = """
        SELECT input_data, expected_output
        FROM test_cases
        WHERE problem_id = %s
        """
    cursor.execute(query, (problem_id,))
    results = cursor.fetchall()

    # 将结果转换为列表
    for row in results:
        test_cases.append({
            "input": row["input_data"],
            "output": row["expected_output"]
        })

    logging.info(f"成功获取到题目 ID {problem_id} 的 {len(test_cases)} 个测试用例")


    return test_cases