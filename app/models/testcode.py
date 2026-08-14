"""测试用例 - MySQL"""

from app.models.db import get_db_connection


def insert_test_case(connection, problem_id, input_data, expected_output):
    """插入测试用例"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
        INSERT INTO test_cases (problem_id, input_data, expected_output)
        VALUES (%s, %s, %s)
        """, (problem_id, input_data, expected_output))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error inserting test case: {e}")
        return False
