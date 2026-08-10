"""
统一数据库路由模块
- 本地开发：使用 SQLite（零配置）
- 生产部署：使用 Supabase PostgreSQL（免费，持久化）

通过环境变量 DATABASE_URL 自动切换：
- 本地无 DATABASE_URL → 使用 SQLite
- 部署有 DATABASE_URL → 使用 PostgreSQL
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 判断使用哪种数据库
USE_POSTGRESQL = bool(os.environ.get('DATABASE_URL'))


def get_db_connection():
    """获取数据库连接（自动选择 SQLite 或 PostgreSQL）"""
    if USE_POSTGRESQL:
        try:
            import psycopg2
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            conn.autocommit = True
            return conn
        except Exception as e:
            logger.error(f"PostgreSQL 连接失败: {e}")
            raise
    else:
        # SQLite 模式
        import sqlite3
        db_path = os.environ.get('DATABASE_PATH', 'codemind.db')
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"SQLite 连接失败: {e}")
            raise


def init_database():
    """初始化数据库（自动选择 SQLite 或 PostgreSQL）"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if USE_POSTGRESQL:
            # PostgreSQL 建表语句
            statements = get_postgresql_create_statements()
        else:
            # SQLite 建表语句
            statements = get_sqlite_create_statements()

        for stmt in statements:
            cursor.execute(stmt)

        conn.commit()
        db_type = "PostgreSQL" if USE_POSTGRESQL else "SQLite"
        logger.info(f"{db_type} 数据库初始化成功")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_sqlite_create_statements():
    """SQLite 建表语句"""
    return [
        '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )''',
        '''CREATE TABLE IF NOT EXISTS verification_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            code TEXT NOT NULL,
            sent_time TEXT DEFAULT (datetime('now', 'localtime')),
            expires_at TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS functions_used (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            function_name TEXT NOT NULL,
            timestamp TEXT DEFAULT (datetime('now', 'localtime'))
        )''',
        '''CREATE TABLE IF NOT EXISTS user_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            upload_time TEXT DEFAULT (datetime('now', 'localtime')),
            file_name TEXT NOT NULL,
            file_type TEXT,
            file_path TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS api_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_upload_id INTEGER NOT NULL,
            response_file_name TEXT,
            response_file_content TEXT,
            timestamp TEXT DEFAULT (datetime('now', 'localtime'))
        )''',
        '''CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            question_title TEXT,
            question_content TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )''',
        '''CREATE TABLE IF NOT EXISTS answer_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            user_answer TEXT,
            is_correct INTEGER DEFAULT 0,
            time_spent INTEGER,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )''',
        '''CREATE TABLE IF NOT EXISTS ability_matrix (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            syntax_score REAL DEFAULT 0,
            algorithm_score REAL DEFAULT 0,
            project_score REAL DEFAULT 0,
            debug_score REAL DEFAULT 0,
            security_score REAL DEFAULT 0,
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        )''',
        '''CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            difficulty TEXT,
            tags TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )''',
        '''CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER NOT NULL,
            input_data TEXT,
            expected_output TEXT
        )'''
    ]


def get_postgresql_create_statements():
    """PostgreSQL 建表语句"""
    return [
        '''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        )''',
        '''CREATE TABLE IF NOT EXISTS verification_codes (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            code VARCHAR(10) NOT NULL,
            sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS functions_used (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            function_name VARCHAR(100) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS user_uploads (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_name VARCHAR(255) NOT NULL,
            file_type VARCHAR(50),
            file_path TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS api_responses (
            id SERIAL PRIMARY KEY,
            user_upload_id INTEGER NOT NULL,
            response_file_name VARCHAR(255),
            response_file_content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS favorites (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            question_id VARCHAR(50) NOT NULL,
            question_title VARCHAR(255),
            question_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS answer_records (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            question_id VARCHAR(50) NOT NULL,
            user_answer TEXT,
            is_correct INTEGER DEFAULT 0,
            time_spent INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS ability_matrix (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL UNIQUE,
            syntax_score REAL DEFAULT 0,
            algorithm_score REAL DEFAULT 0,
            project_score REAL DEFAULT 0,
            debug_score REAL DEFAULT 0,
            security_score REAL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS problems (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT,
            difficulty VARCHAR(20),
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS test_cases (
            id SERIAL PRIMARY KEY,
            problem_id INTEGER NOT NULL,
            input_data TEXT,
            expected_output TEXT
        )'''
    ]


def get_current_timestamp():
    """获取当前时间戳字符串"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def fetch_dict(cursor):
    """将查询结果转换为字典列表（兼容 SQLite 和 PostgreSQL）"""
    if USE_POSTGRESQL:
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        return [dict(row) for row in cursor.fetchall()]


def fetch_one_dict(cursor):
    """获取单条查询结果为字典"""
    if USE_POSTGRESQL:
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    else:
        row = cursor.fetchone()
        return dict(row) if row else None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    init_database()