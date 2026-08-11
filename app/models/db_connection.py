"""
数据库连接模块 — PostgreSQL 连接管理与建表

负责:
- get_db_connection(): 获取 psycopg2 连接
- init_database(): 初始化所有表
- get_create_statements(): 建表 SQL 语句
"""

import os
import logging

import psycopg2

logger = logging.getLogger(__name__)


def get_db_connection():
    """获取 PostgreSQL 数据库连接"""
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"PostgreSQL 连接失败: {e}")
        raise


def get_create_statements():
    """PostgreSQL 建表语句"""
    return [
        '''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
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
        )''',
        '''CREATE TABLE IF NOT EXISTS ability_submissions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            source_type VARCHAR(50) NOT NULL,
            source_id VARCHAR(100),
            scores_json TEXT,
            detail_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''
    ]


def init_database():
    """初始化数据库，创建所有必要的表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for stmt in get_create_statements():
            cursor.execute(stmt)

        conn.commit()
        logger.info("PostgreSQL 数据库初始化成功")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()