"""保存题目 - Supabase PostgreSQL"""

import json
import logging

from app.models.db import get_db_connection, dict_to_markdown, VALID_DIFFICULTIES

logging.basicConfig(level=logging.INFO)


def save_problem_to_database(title: str, content, difficulty: str, tags=None):
    """将算法题目存储到数据库"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if difficulty not in VALID_DIFFICULTIES:
            raise ValueError(f"无效的难度等级。有效值为：{VALID_DIFFICULTIES}")

        if tags is None:
            tags = []
        elif isinstance(tags, str):
            tags = [tags]
        elif not isinstance(tags, list):
            tags = [str(tags)]

        logging.info(f"保存题目标签: {tags}")
        tags_json = json.dumps(tags, ensure_ascii=False)

        if isinstance(content, dict):
            content_markdown = dict_to_markdown(content)
        else:
            content_markdown = content

        cursor.execute("""
        INSERT INTO problems (title, content, difficulty, tags)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """, (title, content_markdown, difficulty, tags_json))
        problem_id = cursor.fetchone()[0]
        connection.commit()

        logging.info(f"成功保存题目 '{title}' 到数据库, id={problem_id}")
        return problem_id

    except Exception as e:
        logging.error(f"存储题目时发生错误：{str(e)}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def save_test_cases_to_database(problem_id: int, test_cases: list):
    """将测试用例存储到数据库"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        for test_case in test_cases:
            input_data = test_case.get("input", "")
            expected_output = test_case.get("output", "")
            cursor.execute("""
            INSERT INTO test_cases (problem_id, input_data, expected_output)
            VALUES (%s, %s, %s)
            """, (problem_id, input_data, expected_output))

        connection.commit()
        logging.info(f"成功存储 {len(test_cases)} 条测试用例到数据库")
        return True

    except Exception as e:
        logging.error(f"存储测试用例时发生错误: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()