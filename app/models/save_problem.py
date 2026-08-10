import json
import os
import mysql.connector
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# MySQL 数据库配置
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


def dict_to_markdown(content_dict):
    """
    将字典格式的内容转换为 Markdown 格式的字符串。
    :param content_dict: 题目内容（字典格式）
    :return: Markdown 格式的字符串
    """
    # 如果content_dict已经是字符串，直接返回
    if isinstance(content_dict, str):
        return content_dict
        
    markdown_content = ""
    for section, text in content_dict.items():
        if isinstance(text, list):  # 处理示例部分
            markdown_content += f"### {section}\n"
            for example in text:
                markdown_content += f"- {example}\n"
        else:
            markdown_content += f"### {section}\n{text}\n\n"
    return markdown_content.strip()


def save_problem_to_database(title: str, content, difficulty: str, tags=None):
    """
    将生成的算法题目存储到数据库中
    
    参数:
        title (str): 题目标题
        content: 题目内容（字典格式或字符串）
        difficulty (str): 难度等级，可选值为 "简单", "中等", "困难"
        tags: 标签列表或字符串
        
    返回:
        bool: 存储成功返回 True，否则返回 False
    """
    try:
        # 连接到数据库
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cursor = connection.cursor()

        # 验证难度等级是否合法
        valid_difficulties = ["简单", "中等", "困难"]
        if difficulty not in valid_difficulties:
            raise ValueError(f"无效的难度等级。有效值为：{valid_difficulties}")

        # 处理标签
        if tags is None:
            tags = []
        elif isinstance(tags, str):
            tags = [tags]
        # 确保tags是列表类型
        elif not isinstance(tags, list):
            tags = [str(tags)]
            
        # 记录保存的tags内容，用于调试
        logging.info(f"保存题目标签: {tags}")
            
        # 将标签列表转换为 JSON 格式字符串
        tags_json = json.dumps(tags, ensure_ascii=False)

        # 处理内容格式
        if isinstance(content, dict):
            content_markdown = dict_to_markdown(content)
        else:
            content_markdown = content

        # 插入数据的 SQL 语句
        insert_query = """
        INSERT INTO problems (title, content, difficulty, tags)
        VALUES (%s, %s, %s, %s)
        """
        data = (title, content_markdown, difficulty, tags_json)
        
        # 执行插入操作
        cursor.execute(insert_query, data)
        problem_id = cursor.lastrowid  # 获取最后插入的 ID
        connection.commit()

        # 关闭连接
        cursor.close()
        connection.close()
        
        logging.info(f"成功保存题目 '{title}' 到数据库")
        return problem_id

    except Exception as e:
        logging.error(f"存储题目时发生错误：{str(e)}")
        return None

def save_test_cases_to_database(problem_id: int, test_cases: list):
    """
    将测试用例存储到数据库的 test_cases 表中

    参数:
        problem_id (int): 题目编号（外键）
        test_cases (list): 测试用例列表，格式为 [{"input": "输入数据", "output": "输出数据"}, ...]

    返回:
        bool: 存储是否成功
    """

    try:
        # 连接到数据库
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cursor = connection.cursor()

        # 插入测试用例
        insert_query = """
        INSERT INTO test_cases (problem_id, input_data, expected_output)
        VALUES (%s, %s, %s)
        """
        for test_case in test_cases:
            input_data = test_case.get("input", "")
            expected_output = test_case.get("output", "")
            cursor.execute(insert_query, (problem_id, input_data, expected_output))

        # 提交事务
        connection.commit()
        logging.info(f"成功存储 {len(test_cases)} 条测试用例到数据库")
        return True

    except Exception as e:
        logging.error(f"存储测试用例时发生错误: {str(e)}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()