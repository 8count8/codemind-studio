import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量中获取 MySQL 配置信息
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))  # 确保端口是整数
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

def insert_test_case(connection, problem_id, input_data, expected_output):
    """
    插入一条测试用例数据到 test_cases 表中。
    """
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO test_cases (problem_id, input_data, expected_output)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (problem_id, input_data, expected_output))
        connection.commit()
        print(f"Inserted test case with auto-generated ID: problem_id={problem_id}, input_data={input_data}, expected_output={expected_output}")
    except Error as e:
        print(f"Error while inserting test case: {e}")
    finally:
        cursor.close()

def parse_markdown_file(file_path):
    """
    解析单个 Markdown 文件的内容。
    :param file_path: Markdown 文件路径
    :return: 测试用例的列表
    """
    with open(file_path, "r", encoding="utf-8") as file:
        markdown_text = file.read()

    lines = markdown_text.strip().split("\n")
    data_lines = []

    # 找到数据行的起始位置
    for i, line in enumerate(lines):
        if line.startswith("|") and "---" in lines[i + 1]:  # 找到分隔线
            data_lines = lines[i + 2:]  # 跳过分隔线和表头
            break

    test_cases = []
    for line in data_lines:
        values = [v.strip() for v in line.split("|")[1:-1]]  # 去掉首尾的空列
        if len(values) == 3:  # 确保有 3 列数据
            try:
                test_case = {
                    "problem_id": int(values[0]),  # 将第一列转换为整数
                    "input_data": values[1],
                    "expected_output": values[2]
                }
                test_cases.append(test_case)
            except ValueError as e:
                print(f"Error parsing line: {line}. Details: {e}")
    return test_cases

def process_markdown_folder(folder_path):
    """
    处理文件夹中的所有 Markdown 文件。
    :param folder_path: 包含 Markdown 文件的文件夹路径
    :return: 所有测试用例的列表
    """
    all_test_cases = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".md"):  # 只处理 .md 文件
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing file: {file_path}")
            test_cases = parse_markdown_file(file_path)
            all_test_cases.extend(test_cases)
    return all_test_cases

def main():
    # Markdown 文件夹路径
    markdown_folder = r"D:\PycharmProject\CMS\testmd"  # 替换为你的文件夹路径

    # 解析文件夹中的所有 Markdown 文件
    test_cases = process_markdown_folder(markdown_folder)

    # 创建数据库连接
    connection = create_mysql_connection()
    if connection is None:
        print("无法连接到数据库，程序退出。")
        return

    try:
        # 将解析后的测试用例插入到数据库中
        for test_case in test_cases:
            insert_test_case(
                connection,
                test_case["problem_id"],
                test_case["input_data"],
                test_case["expected_output"]
            )
    finally:
        # 关闭数据库连接
        if connection.is_connected():
            connection.close()
            print("数据库连接已关闭。")

if __name__ == "__main__":
    main()