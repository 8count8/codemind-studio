"""保存题目 - SQLite 版本"""

import json
import logging

from app.models.sqlite_db import get_db_connection

logging.basicConfig(level=logging.INFO)


def dict_to_markdown(content_dict):
    """将字典格式的内容转换为 Markdown 格式的字符串"""
    if isinstance(content_dict, str):
        return content_dict

    markdown_content = ""
    for section, text in content_dict.items():
        if isinstance(text, list):
            markdown_content += f"### {section}\n"
            for example in text:
                markdown_content += f"- {example}\n"
        else:
            markdown_content += f"### {section}\n{text}\n\n"
    return markdown_content.strip()


def save_problem_to_database(title: str, content, difficulty: str, tags=None):
    """将算法题目存储到数据库"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        valid_difficulties = ["简单", "中等", "困难"]
        if difficulty not in valid_difficulties:
            raise ValueError(f"无效的难度等级。有效值为：{valid_difficulties}")

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
        INSERT INTO answer_records (question_id, question_title, user_answer, is_correct, created_at)
        VALUES (?, ?, ?, 0, datetime('now', 'localtime'))
        """, (title, title, content_markdown))
        
        problem_id = cursor.lastrowid
        connection.commit()
        connection.close()

        logging.info(f"成功保存题目 '{title}' 到数据库")
        return problem_id

    except Exception as e:
        logging.error(f"存储题目时发生错误：{str(e)}")
        return None


def save_test_cases_to_database(problem_id: int, test_cases: list):
    """将测试用例存储到数据库"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        for test_case in test_cases:
            input_data = test_case.get("input", "")
            expected_output = test_case.get("output", "")
            cursor.execute("""
            INSERT INTO answer_records (question_id, user_answer, is_correct, created_at)
            VALUES (?, ?, 0, datetime('now', 'localtime'))
            """, (problem_id, input_data))

        connection.commit()
        connection.close()
        logging.info(f"成功存储 {len(test_cases)} 条测试用例到数据库")
        return True

    except Exception as e:
        logging.error(f"存储测试用例时发生错误: {str(e)}")
        return False


# 兼容旧接口
create_mysql_connection = get_db_connection