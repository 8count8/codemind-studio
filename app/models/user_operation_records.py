"""用户操作记录 - 支持 SQLite 和 PostgreSQL"""
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

from app.models.db import get_db_connection, get_current_timestamp, fetch_dict, USE_POSTGRESQL


def log_function_usage(user_id, function_name):
    """记录用户功能使用日志"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        timestamp = get_current_timestamp()
        cursor.execute('INSERT INTO functions_used (user_id, function_name, timestamp) VALUES (%s, %s, %s)',
                       (user_id, function_name, timestamp))
        connection.commit()
        logging.info(f"功能 {function_name} 使用记录成功！")
    except Exception as e:
        logging.error(f"记录功能使用失败: {e}")
    finally:
        connection.close()


def upload_file_to_db(user_id, file_path, file_type):
    """处理上传文件并存储到数据库"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        timestamp = get_current_timestamp()
        file_name = os.path.basename(file_path)

        cursor.execute('''
        INSERT INTO user_uploads 
        (user_id, upload_time, file_name, file_type, file_path)
        VALUES (%s, %s, %s, %s, %s)
        ''', (user_id, timestamp, file_name, file_type, file_path))
        connection.commit()
        logging.info(f"文件 {file_name} 上传成功！")
    except Exception as e:
        logging.error(f"文件上传失败: {e}")
    finally:
        connection.close()


def log_api_response(upload_id, response_file_name, response_file_content):
    """记录后端 API 返回的代码文件"""
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
    except Exception as e:
        logging.error(f"记录 API 响应失败: {e}")
    finally:
        connection.close()


def get_user_history_combined(user_id):
    """查询用户的历史记录（整合版）"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 查询 functions_used 表
        cursor.execute('''
        SELECT 'function' AS record_type, function_name AS name, timestamp 
        FROM functions_used 
        WHERE user_id = %s
        ''', (user_id,))
        function_records = fetch_dict(cursor)

        # 查询 user_uploads 表
        cursor.execute('''
        SELECT 'upload' AS record_type, file_name AS name, upload_time AS timestamp, file_type, file_path 
        FROM user_uploads 
        WHERE user_id = %s
        ''', (user_id,))
        upload_records = fetch_dict(cursor)

        # 查询 api_responses 表
        cursor.execute('''
        SELECT 'api_response' AS record_type, response_file_name AS name, timestamp, response_file_content AS content 
        FROM api_responses 
        WHERE user_upload_id IN (
            SELECT id FROM user_uploads WHERE user_id = %s
        )
        ''', (user_id,))
        api_response_records = fetch_dict(cursor)

        # 合并所有记录
        all_records = function_records + upload_records + api_response_records

        # 按时间排序
        all_records.sort(key=lambda x: str(x.get('timestamp', '')), reverse=True)

        logging.info(f"成功获取用户 {user_id} 的历史记录！")
        return all_records

    except Exception as e:
        logging.error(f"查询用户历史记录失败: {e}")
        return None
    finally:
        connection.close()


def delete_history_record(user_id, record_type, record_id):
    """删除某条历史记录"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if record_type == "function":
            cursor.execute('''
            DELETE FROM functions_used 
            WHERE id = %s AND user_id = %s
            ''', (record_id, user_id))

        elif record_type == "upload":
            cursor.execute('''
            DELETE FROM user_uploads 
            WHERE id = %s AND user_id = %s
            ''', (record_id, user_id))

        elif record_type == "api_response":
            cursor.execute('''
            DELETE FROM api_responses 
            WHERE id = %s AND user_upload_id IN (
                SELECT id FROM user_uploads WHERE user_id = %s
            )
            ''', (record_id, user_id))

        else:
            logging.error(f"无效的记录类型: {record_type}")
            return False

        if cursor.rowcount == 0:
            logging.warning(f"未找到符合条件的记录")
            return False

        connection.commit()
        logging.info(f"成功删除记录")
        return True

    except Exception as e:
        logging.error(f"删除历史记录失败: {e}")
        return False
    finally:
        connection.close()