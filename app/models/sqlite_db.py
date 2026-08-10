"""SQLite 数据库统一管理模块"""
import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 数据库文件路径（支持环境变量配置）
DB_PATH = os.environ.get('DATABASE_PATH', 'codemind.db')


def get_db_connection():
    """创建 SQLite 数据库连接"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise


def init_database():
    """初始化数据库，创建所有必要的表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')

        # 验证码表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                code TEXT NOT NULL,
                sent_time TEXT DEFAULT (datetime('now', 'localtime')),
                expires_at TEXT
            )
        ''')

        # 功能使用记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS functions_used (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                function_name TEXT NOT NULL,
                timestamp TEXT DEFAULT (datetime('now', 'localtime'))
            )
        ''')

        # 用户上传文件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                upload_time TEXT DEFAULT (datetime('now', 'localtime')),
                file_name TEXT NOT NULL,
                file_type TEXT,
                file_path TEXT
            )
        ''')

        # API 响应表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_upload_id INTEGER NOT NULL,
                response_file_name TEXT,
                response_file_content TEXT,
                timestamp TEXT DEFAULT (datetime('now', 'localtime'))
            )
        ''')

        # 收藏表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id TEXT NOT NULL,
                question_title TEXT,
                question_content TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        ''')

        # 答题记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answer_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id TEXT NOT NULL,
                user_answer TEXT,
                is_correct INTEGER DEFAULT 0,
                time_spent INTEGER,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        ''')

        # 能力矩阵表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ability_matrix (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                syntax_score REAL DEFAULT 0,
                algorithm_score REAL DEFAULT 0,
                project_score REAL DEFAULT 0,
                debug_score REAL DEFAULT 0,
                security_score REAL DEFAULT 0,
                updated_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        ''')

        # 题目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                difficulty TEXT,
                tags TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        ''')

        # 测试用例表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER NOT NULL,
                input_data TEXT,
                expected_output TEXT
            )
        ''')

        conn.commit()
        logger.info("数据库初始化成功")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_current_timestamp():
    """获取当前时间戳字符串"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    init_database()