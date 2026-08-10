"""代码服务 - SQLite 版本"""

import json
import logging

from app.models.sqlite_db import get_db_connection

logging.basicConfig(level=logging.INFO)


def get_db_connection():
    """获取数据库连接"""
    return get_db_connection()


def get_test_cases(problem_id: int) -> list:
    """获取测试用例"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT input_data, expected_output
            FROM test_cases
            WHERE problem_id = ?
        """, (problem_id,))
        results = cursor.fetchall()

        test_cases = []
        for row in results:
            test_cases.append({
                "input": row["input_data"] if isinstance(row, dict) else row[0],
                "output": row["expected_output"] if isinstance(row, dict) else row[1]
            })

        logging.info(f"成功获取到题目 ID {problem_id} 的 {len(test_cases)} 个测试用例")
        connection.close()
        return test_cases
    except Exception as e:
        logging.error(f"获取测试用例失败: {e}")
        return []