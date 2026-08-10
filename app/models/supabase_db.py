"""Supabase PostgreSQL 数据库管理模块（免费版，无需银行卡）"""

import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# 数据库连接配置（从环境变量读取）
DB_URL = os.environ.get('DATABASE_URL', '')


def get_db_connection():
    """创建 PostgreSQL 数据库连接"""
    try:
        if not DB_URL:
            raise ValueError("DATABASE_URL 未设置，请在 Supabase 获取连接字符串")
        
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
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
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL
            )
        ''')

        # 验证码表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_codes (
                id SERIAL PRIMARY KEY,
                email VARCHAR(100) UNIQUE NOT NULL,
                code VARCHAR(10) NOT NULL,
                sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')

        # 功能使用记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS functions_used (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                function_name VARCHAR(100) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 用户上传文件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_uploads (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_name VARCHAR(255) NOT NULL,
                file_type VARCHAR(50),
                file_path TEXT
            )
        ''')

        # API 响应表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_responses (
                id SERIAL PRIMARY KEY,
                user_upload_id INTEGER NOT NULL,
                response_file_name VARCHAR(255),
                response_file_content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 收藏表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                question_id VARCHAR(50) NOT NULL,
                question_title VARCHAR(255),
                question_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 答题记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answer_records (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                question_id VARCHAR(50) NOT NULL,
                user_answer TEXT,
                is_correct INTEGER DEFAULT 0,
                time_spent INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 能力矩阵表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ability_matrix (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                syntax_score REAL DEFAULT 0,
                algorithm_score REAL DEFAULT 0,
                project_score REAL DEFAULT 0,
                debug_score REAL DEFAULT 0,
                security_score REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 题目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT,
                difficulty VARCHAR(20),
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 测试用例表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                id SERIAL PRIMARY KEY,
                problem_id INTEGER NOT NULL,
                input_data TEXT,
                expected_output TEXT
            )
        ''')

        conn.commit()
        logger.info("Supabase 数据库初始化成功")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_current_timestamp():
    """获取当前时间戳字符串"""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    init_database()