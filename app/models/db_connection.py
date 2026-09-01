"""
数据库连接模块 — MySQL 连接管理与建表

负责:
- get_db_connection(): 获取 mysql-connector-python 连接
- init_database(): 初始化所有表
- get_create_statements(): 建表 SQL 语句
"""

import os
import logging

import mysql.connector
from mysql.connector import errorcode

logger = logging.getLogger(__name__)


def get_db_connection():
    """获取 MySQL 数据库连接（使用 Oracle 官方 mysql-connector-python）"""
    try:
        host = os.environ.get('DB_HOST', 'localhost')
        port = int(os.environ.get('DB_PORT', 3306))
        user = os.environ.get('DB_USER', 'root')
        password = os.environ.get('DB_PASSWORD', '')
        database = os.environ.get('DB_NAME', 'codemind')

        options = dict(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            autocommit=True,
            connection_timeout=10,
        )
        try:
            # 有 C 扩展时优先使用；纯 Python/精简镜像中自动回退。
            conn = mysql.connector.connect(use_pure=False, **options)
        except ImportError:
            conn = mysql.connector.connect(use_pure=True, **options)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logger.error("MySQL 连接失败：用户名或密码错误")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logger.error(f"MySQL 连接失败：数据库 '{database}' 不存在，请先 CREATE DATABASE {database}")
        elif err.errno == errorcode.CR_CONN_HOST_ERROR:
            logger.error(f"MySQL 连接失败：无法连接到 {host}:{port}")
        else:
            logger.error(f"MySQL 连接失败（{err.errno}）: {err}")
        raise
    except Exception as e:
        logger.error(f"MySQL 连接失败: {e}")
        raise


def get_create_statements():
    """MySQL 建表语句"""
    return [
        '''CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',
        
        '''CREATE TABLE IF NOT EXISTS verification_codes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            code VARCHAR(10) NOT NULL,
            sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',
        
        '''CREATE TABLE IF NOT EXISTS functions_used (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            function_name VARCHAR(100) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',
        
        '''CREATE TABLE IF NOT EXISTS user_uploads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_name VARCHAR(255) NOT NULL,
            file_type VARCHAR(50),
            file_path TEXT,
            file_content LONGTEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',
        
        '''CREATE TABLE IF NOT EXISTS api_responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_upload_id INT NOT NULL,
            response_file_name VARCHAR(255),
            response_file_content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',
        
        '''CREATE TABLE IF NOT EXISTS favorites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            question_id VARCHAR(50) NOT NULL,
            question_title VARCHAR(255),
            question_content TEXT,
            topic_id INT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY idx_favorites_user_question (user_id, question_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',
        
        '''CREATE TABLE IF NOT EXISTS favorite_topics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(80) NOT NULL,
            description VARCHAR(255) DEFAULT '',
            tags VARCHAR(255) DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY idx_favorite_topics_user_name (user_id, name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',

        '''CREATE TABLE IF NOT EXISTS answer_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            question_id VARCHAR(50) NOT NULL,
            user_answer TEXT,
            is_correct INT DEFAULT 0,
            time_spent INT,
            language VARCHAR(30) DEFAULT 'python',
            execution_result LONGTEXT,
            score FLOAT DEFAULT 0,
            run_time_ms INT DEFAULT 0,
            task_id VARCHAR(64),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',
        
        '''CREATE TABLE IF NOT EXISTS ability_matrix (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            syntax_score FLOAT DEFAULT 0,
            algorithm_score FLOAT DEFAULT 0,
            project_score FLOAT DEFAULT 0,
            debug_score FLOAT DEFAULT 0,
            security_score FLOAT DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',
        
        '''CREATE TABLE IF NOT EXISTS problems (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT,
            difficulty VARCHAR(20),
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',
        
        '''CREATE TABLE IF NOT EXISTS test_cases (
            id INT AUTO_INCREMENT PRIMARY KEY,
            problem_id INT NOT NULL,
            input_data TEXT,
            expected_output TEXT,
            description VARCHAR(255) DEFAULT ''
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',

        '''CREATE TABLE IF NOT EXISTS user_drafts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            question_id VARCHAR(50) NOT NULL,
            language VARCHAR(30) DEFAULT 'python',
            code LONGTEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY idx_user_drafts_user_question (user_id, question_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''',
        
        '''CREATE TABLE IF NOT EXISTS ability_submissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            source_type VARCHAR(50) NOT NULL,
            source_id VARCHAR(100),
            scores_json TEXT,
            detail_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''
    ]


def init_database():
    """初始化数据库，创建所有必要的表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for stmt in get_create_statements():
            cursor.execute(stmt)

        conn.commit()
        logger.info("MySQL 数据库初始化成功")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
