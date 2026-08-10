"""
后端插入题目到数据库的程序
将题目以 word 格式放在电脑的‘D:\PycharmProject\CMS\markdown’路径下（可更换）
需要以‘题目标题_题目标签_题目难度’格式放入
具体格式同word一致
"""
import os
import mysql.connector
from mysql.connector import Error
import json
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
            database=MYSQL_DATABASE,
            charset="utf8mb4",  # 确保使用 utf8mb4 字符集
            use_unicode=True    # 确保支持 Unicode 字符
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


# 解析 Markdown 文件内容
def parse_markdown_file(file_path):
    """
    解析 Markdown 文件内容并返回 Markdown 格式的字符串。
    :param file_path: Markdown 文件路径
    :return: Markdown 格式的题目内容
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # 将 Markdown 内容直接返回
    return content.strip()


# 单次插入题目数据
def seed_problems_from_files(folder_path):
    """
    从指定文件夹中读取 Markdown 文件并插入到数据库。
    :param folder_path: 存放 Markdown 文件的文件夹路径
    """
    # 获取所有 Markdown 文件
    markdown_files = [f for f in os.listdir(folder_path) if f.endswith(".md")]
    if not markdown_files:
        print("No Markdown files found in the folder.")
        return

    connection = create_mysql_connection()
    if connection is None:
        print("Database connection failed")
        return

    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO problems (title, content, difficulty, tags)
        VALUES (%s, %s, %s, %s)
        """

        # 遍历每个文件
        for file_name in markdown_files:
            # 解析文件名
            name_parts = file_name.split(".")[0].split("_")  # 去掉扩展名并按 "_" 分割
            if len(name_parts) < 3 or not name_parts[-1]:  # 确保有难度部分且不为空
                print(f"Invalid file name format: {file_name}")
                continue

            title = "_".join(name_parts[:-2])  # 标题是前部分
            tags_raw = name_parts[-2]  # 标签原始值
            difficulty = name_parts[-1].strip()  # 最后一部分是难度，去除多余空格和换行符
            difficulty = difficulty.replace("\n", "").replace("\r", "")  # 去除不可见字符

            # 清理 tags 并转换为 JSON 格式
            tags = [tag.strip() for tag in tags_raw.replace("，", ",").split(",")]  # 替换中文逗号并分割
            tags_json = json.dumps(tags, ensure_ascii=False)  # 转换为 JSON 格式

            # 检查难度是否有效
            valid_difficulties = ["简单", "中等", "困难"]
            if difficulty not in valid_difficulties:
                print(f"Invalid difficulty level: {difficulty} in file {file_name}")
                continue

            # 调试输出
            print(f"Parsed title: '{title}'")
            print(f"Parsed tags: {tags_json}")
            print(f"Parsed difficulty: '{difficulty}'")

            # 解析 Markdown 文件内容
            file_path = os.path.join(folder_path, file_name)
            try:
                content = parse_markdown_file(file_path)
            except Exception as e:
                print(f"Error parsing file {file_name}: {e}")
                continue

            # 插入数据到数据库（单次插入）
            try:
                cursor.execute(insert_query, (title, content, difficulty, tags_json))
                connection.commit()  # 每次插入后立即提交
                print(f"Successfully inserted problem '{title}' into the database.")
            except Error as e:
                print(f"Error inserting data for file {file_name}: {str(e)}")
                connection.rollback()  # 出错时回滚事务

    except Error as e:
        print(f"Database error: {str(e)}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# 运行脚本
if __name__ == "__main__":
    folder_path = r"D:\PycharmProject\CMS\word"  # 存放 Markdown 文件的文件夹路径
    seed_problems_from_files(folder_path)