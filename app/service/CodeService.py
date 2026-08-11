"""代码服务 - Supabase PostgreSQL"""

import json
import logging

from app.models.db import get_db_connection, fetch_dict

logging.basicConfig(level=logging.INFO)


def get_test_cases(problem_id: int) -> list:
    """获取测试用例"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT input_data, expected_output
            FROM test_cases
            WHERE problem_id = %s
        """, (problem_id,))
        results = fetch_dict(cursor)

        test_cases = []
        for row in results:
            test_cases.append({
                "input": row.get("input_data"),
                "output": row.get("expected_output")
            })

        logging.info(f"成功获取到题目 ID {problem_id} 的 {len(test_cases)} 个测试用例")
        return test_cases
    except Exception as e:
        logging.error(f"获取测试用例失败: {e}")
        return []
    finally:
        if conn:
            conn.close()