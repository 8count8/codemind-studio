"""
单元测试: app/models/db.py 纯函数

覆盖:
- dict_to_markdown: 字典转 Markdown
- fetch_dict: 游标结果转字典列表
- fetch_one_dict: 游标单行转字典
- get_current_timestamp: 时间戳生成
"""
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.models.db import (
    dict_to_markdown,
    fetch_dict,
    fetch_one_dict,
    get_current_timestamp,
    VALID_DIFFICULTIES,
)


class TestDictToMarkdown(unittest.TestCase):
    """dict_to_markdown 转换逻辑测试"""

    def test_string_input_returns_unchanged(self):
        result = dict_to_markdown("plain text")
        self.assertEqual(result, "plain text")

    def test_empty_string(self):
        result = dict_to_markdown("")
        self.assertEqual(result, "")

    def test_dict_with_list_values(self):
        content = {
            "Python 基础": ["变量", "函数", "类"],
            "Java 进阶": ["多态", "泛型"],
        }
        result = dict_to_markdown(content)
        self.assertIn("### Python 基础", result)
        self.assertIn("- 变量", result)
        self.assertIn("- 函数", result)
        self.assertIn("- 类", result)
        self.assertIn("### Java 进阶", result)
        self.assertIn("- 多态", result)
        self.assertIn("- 泛型", result)

    def test_dict_with_string_values(self):
        content = {
            "概述": "这是一段描述文字",
            "用法": "调用方式说明",
        }
        result = dict_to_markdown(content)
        self.assertIn("### 概述", result)
        self.assertIn("这是一段描述文字", result)
        self.assertIn("### 用法", result)
        self.assertIn("调用方式说明", result)

    def test_mixed_dict(self):
        content = {
            "章节一": "纯文本内容",
            "章节二": ["列表项 A", "列表项 B"],
        }
        result = dict_to_markdown(content)
        self.assertIn("### 章节一", result)
        self.assertIn("纯文本内容", result)
        self.assertIn("### 章节二", result)
        self.assertIn("- 列表项 A", result)
        self.assertIn("- 列表项 B", result)

    def test_empty_dict_returns_empty_string(self):
        result = dict_to_markdown({})
        self.assertEqual(result, "")


class TestFetchDict(unittest.TestCase):
    """fetch_dict 游标转字典列表测试"""

    def test_empty_cursor(self):
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = []

        result = fetch_dict(mock_cursor)
        self.assertEqual(result, [])

    def test_single_row(self):
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "Alice")]

        result = fetch_dict(mock_cursor)
        self.assertEqual(result, [{"id": 1, "name": "Alice"}])

    def test_multiple_rows(self):
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",), ("score",)]
        mock_cursor.fetchall.return_value = [
            (1, "Alice", 95),
            (2, "Bob", 87),
            (3, "Carol", 92),
        ]

        result = fetch_dict(mock_cursor)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], {"id": 1, "name": "Alice", "score": 95})
        self.assertEqual(result[1], {"id": 2, "name": "Bob", "score": 87})
        self.assertEqual(result[2], {"id": 3, "name": "Carol", "score": 92})

    def test_single_column(self):
        mock_cursor = MagicMock()
        mock_cursor.description = [("count",)]
        mock_cursor.fetchall.return_value = [(42,)]

        result = fetch_dict(mock_cursor)
        self.assertEqual(result, [{"count": 42}])


class TestFetchOneDict(unittest.TestCase):
    """fetch_one_dict 游标单行转字典测试"""

    def test_empty_result_returns_none(self):
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchone.return_value = None

        result = fetch_one_dict(mock_cursor)
        self.assertIsNone(result)

    def test_single_row(self):
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",), ("email",)]
        mock_cursor.fetchone.return_value = (1, "Alice", "alice@example.com")

        result = fetch_one_dict(mock_cursor)
        self.assertEqual(result, {"id": 1, "name": "Alice", "email": "alice@example.com"})

    def test_single_value_row(self):
        mock_cursor = MagicMock()
        mock_cursor.description = [("cnt",)]
        mock_cursor.fetchone.return_value = [(100,)]

        result = fetch_one_dict(mock_cursor)
        self.assertEqual(result, {"cnt": (100,)})


class TestGetCurrentTimestamp(unittest.TestCase):
    """get_current_timestamp 时间戳格式测试"""

    def test_format_matches_expected_pattern(self):
        with patch('app.models.db_utils.datetime') as mock_dt:
            mock_now = datetime(2025, 1, 9, 14, 30, 45)
            mock_dt.now.return_value = mock_now
            result = get_current_timestamp()
            self.assertEqual(result, "2025-01-09 14:30:45")

    def test_returns_string(self):
        result = get_current_timestamp()
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 19)


class TestValidDifficulties(unittest.TestCase):
    """VALID_DIFFICULTIES 常量测试"""

    def test_contains_expected_values(self):
        self.assertIn("简单", VALID_DIFFICULTIES)
        self.assertIn("中等", VALID_DIFFICULTIES)
        self.assertIn("困难", VALID_DIFFICULTIES)

    def test_count_is_three(self):
        self.assertEqual(len(VALID_DIFFICULTIES), 3)


if __name__ == '__main__':
    unittest.main()
