"""题目导入 - SQLite 版本"""

from app.models.sqlite_db import get_db_connection


def create_mysql_connection():
    """兼容旧接口"""
    return get_db_connection()