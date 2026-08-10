import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
from dotenv import load_dotenv
# 加载环境变量
load_dotenv()
# MySQL 数据库配置
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# 数据库连接封装
def get_db_connection():
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
        logging.error(f"数据库连接失败: {e}")
        raise


# 获取当前时间戳
def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# 记录用户使用的功能名称到 functions_used 表
def log_function_usage(user_id, function_name):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        timestamp = get_current_timestamp()
        cursor.execute('INSERT INTO functions_used (user_id, function_name, timestamp) VALUES (%s, %s, %s)',
                       (user_id, function_name, timestamp))
        connection.commit()
        logging.info(f"功能 {function_name} 使用记录成功！")
    except Error as e:
        logging.error(f"记录功能使用失败: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# 处理上传文件并存储到 user_uploads 表
def upload_file_to_db(user_id, file_path, file_type):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        timestamp = get_current_timestamp()
        file_name = os.path.basename(file_path)

        # 如果是大文件，建议仅存储路径而非内容
        cursor.execute('''
        INSERT INTO user_uploads 
        (user_id, upload_time, file_name, file_type, file_path)
        VALUES (%s, %s, %s, %s, %s)
        ''', (user_id, timestamp, file_name, file_type, file_path))
        connection.commit()
        logging.info(f"文件 {file_name} 上传成功！")
    except Error as e:
        logging.error(f"文件上传失败: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# 记录后端 API 返回的代码文件到 api_responses 表
def log_api_response(upload_id, response_file_name, response_file_content):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        timestamp = get_current_timestamp()
        cursor.execute('''
        INSERT INTO api_responses 
        (user_upload_id, response_file_name, response_file_content, timestamp)
        VALUES (%s, %s, %s, %s)
        ''', (upload_id, response_file_name, response_file_content, timestamp))
        connection.commit()
        logging.info(f"API 响应文件 {response_file_name} 记录成功！")
    except Error as e:
        logging.error(f"记录 API 响应失败: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# 查询用户的历史记录
def get_user_history_combined(user_id):
    connection = None
    try:
        # 获取数据库连接
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 查询 functions_used 表：获取用户使用的功能记录
        cursor.execute('''
        SELECT 'function' AS record_type, function_name AS name, timestamp 
        FROM functions_used 
        WHERE user_id = %s
        ''', (user_id,))
        function_records = cursor.fetchall()

        # 查询 user_uploads 表：获取用户上传的文件记录
        cursor.execute('''
        SELECT 'upload' AS record_type, file_name AS name, upload_time AS timestamp, file_type, file_path 
        FROM user_uploads 
        WHERE user_id = %s
        ''', (user_id,))
        upload_records = cursor.fetchall()

        # 查询 api_responses 表：获取后端返回的代码文件记录
        cursor.execute('''
        SELECT 'api_response' AS record_type, response_file_name AS name, timestamp, response_file_content AS content 
        FROM api_responses 
        WHERE user_upload_id IN (
            SELECT id FROM user_uploads WHERE user_id = %s
        )
        ''', (user_id,))
        api_response_records = cursor.fetchall()

        # 合并所有记录
        all_records = []
        all_records.extend(function_records)
        all_records.extend(upload_records)
        all_records.extend(api_response_records)

        # 按时间排序（从最近到最早）
        all_records.sort(key=lambda x: x['timestamp'], reverse=True)

        logging.info(f"成功获取用户 {user_id} 的历史记录（整合版）！")
        return all_records

    except Error as e:
        logging.error(f"查询用户历史记录失败: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def delete_history_record(user_id, record_type, record_id):
    """
    删除某条历史记录。

    :param user_id: 用户 ID，用于确保用户只能删除自己的记录。
    :param record_type: 记录类型 ('function', 'upload', 'api_response')。
    :param record_id: 记录的唯一标识（对应表中的主键 ID）。
    :return: 是否删除成功 (True/False)。
    """
    connection = None
    try:
        # 获取数据库连接
        connection = get_db_connection()
        cursor = connection.cursor()

        # 根据记录类型执行不同的删除操作
        if record_type == "function":
            # 删除 functions_used 表中的记录
            cursor.execute('''
            DELETE FROM functions_used 
            WHERE id = %s AND user_id = %s
            ''', (record_id, user_id))

        elif record_type == "upload":
            # 删除 user_uploads 表中的记录
            cursor.execute('''
            DELETE FROM user_uploads 
            WHERE id = %s AND user_id = %s
            ''', (record_id, user_id))

        elif record_type == "api_response":
            # 删除 api_responses 表中的记录
            cursor.execute('''
            DELETE FROM api_responses 
            WHERE id = %s AND user_upload_id IN (
                SELECT id FROM user_uploads WHERE user_id = %s
            )
            ''', (record_id, user_id))

        else:
            logging.error(f"无效的记录类型: {record_type}")
            return False

        # 检查是否删除成功
        if cursor.rowcount == 0:
            logging.warning(f"未找到符合条件的记录 (user_id={user_id}, record_type={record_type}, record_id={record_id})")
            return False

        # 提交事务
        connection.commit()
        logging.info(f"成功删除记录 (user_id={user_id}, record_type={record_type}, record_id={record_id})")
        return True

    except Error as e:
        logging.error(f"删除历史记录失败: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()