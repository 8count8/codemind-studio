"""测试用例 - SQLite 版本"""

from app.models.sqlite_db import get_db_connection


def create_mysql_connection():
    """兼容旧接口"""
    return get_db_connection()


def insert_test_case(connection, problem_id, input_data, expected_output):
    """插入测试用例"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO test_cases (problem_id, input_data, expected_output)
        VALUES (?, ?, ?)
        """, (problem_id, input_data, expected_output))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error inserting test case: {e}")
        return False