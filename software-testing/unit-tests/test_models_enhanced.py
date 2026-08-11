"""
Phase 2 测试: 数据模型与服务层增强测试

覆盖:
- ability_matrix_model 向后兼容重导出验证
- ability_matrix_model 数据转换逻辑测试
- 模型层常量一致性验证
- 循环依赖约束验证
- Service 层纯逻辑测试
"""

import unittest
from unittest.mock import MagicMock, patch


class TestModelBackwardCompatibility(unittest.TestCase):
    """验证模型层的向后兼容重导出"""

    def test_ability_dimensions_reexported(self):
        from app.models.ability_matrix_model import ABILITY_DIMENSIONS
        from app.utils.ability_matrix_calculator import ABILITY_DIMENSIONS as CALC_DIMS
        self.assertEqual(ABILITY_DIMENSIONS, CALC_DIMS)

    def test_dimension_labels_reexported(self):
        from app.models.ability_matrix_model import DIMENSION_LABELS
        from app.utils.ability_matrix_calculator import DIMENSION_LABELS as CALC_LABELS
        self.assertEqual(DIMENSION_LABELS, CALC_LABELS)

    def test_calculate_level_reexported(self):
        from app.models.ability_matrix_model import calculate_level
        result = calculate_level({
            'syntax_score': 100, 'algorithm_score': 100,
            'project_score': 100, 'debug_score': 100, 'security_score': 100
        })
        self.assertEqual(result, '专家')

    def test_build_dimensions_dict_reexported(self):
        from app.models.ability_matrix_model import build_dimensions_dict
        result = build_dimensions_dict({
            'syntax_score': 80,
            'algorithm_score': 60,
        })
        self.assertIn('syntax_score', result)
        self.assertIn('algorithm_score', result)

    def test_diagnose_weak_dimensions_reexported(self):
        from app.models.ability_matrix_model import diagnose_weak_dimensions
        result = diagnose_weak_dimensions({
            'syntax_score': 80, 'algorithm_score': 45,
            'project_score': 70, 'debug_score': 50, 'security_score': 90
        })
        self.assertIsInstance(result, list)

    def test_get_dimension_suggestion_reexported(self):
        from app.models.ability_matrix_model import get_dimension_suggestion
        result = get_dimension_suggestion('syntax_score')
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


class TestModelDataConversion(unittest.TestCase):
    """验证模型层中的数据转换逻辑"""

    def test_build_dimensions_dict_all_dimensions_included(self):
        from app.utils.ability_matrix_calculator import build_dimensions_dict, ABILITY_DIMENSIONS
        result = build_dimensions_dict({})
        for dim in ABILITY_DIMENSIONS:
            self.assertIn(dim, result)

    def test_build_dimensions_dict_default_zero(self):
        from app.utils.ability_matrix_calculator import build_dimensions_dict
        result = build_dimensions_dict({})
        for dim_data in result.values():
            self.assertEqual(dim_data['score'], 0)

    def test_build_dimensions_dict_uses_labels(self):
        from app.utils.ability_matrix_calculator import build_dimensions_dict, DIMENSION_LABELS
        result = build_dimensions_dict({
            'syntax_score': 85,
        })
        self.assertEqual(
            result['syntax_score']['label'],
            DIMENSION_LABELS['syntax_score']
        )

    def test_build_dimensions_dict_rounds_scores(self):
        from app.utils.ability_matrix_calculator import build_dimensions_dict
        result = build_dimensions_dict({
            'syntax_score': 85.678,
        })
        self.assertEqual(result['syntax_score']['score'], 85.68)

    def test_diagnose_weak_dimensions_empty_input(self):
        from app.utils.ability_matrix_calculator import diagnose_weak_dimensions
        result = diagnose_weak_dimensions({})
        self.assertEqual(result, [])

    def test_diagnose_weak_dimensions_identical_scores(self):
        from app.utils.ability_matrix_calculator import diagnose_weak_dimensions
        result = diagnose_weak_dimensions({
            'syntax_score': 70, 'algorithm_score': 70,
            'project_score': 70, 'debug_score': 70, 'security_score': 70
        })
        self.assertEqual(result, [])

    def test_diagnose_weak_dimensions_all_below_60(self):
        from app.utils.ability_matrix_calculator import diagnose_weak_dimensions
        result = diagnose_weak_dimensions({
            'syntax_score': 50, 'algorithm_score': 55,
            'project_score': 45, 'debug_score': 58, 'security_score': 52
        })
        self.assertGreater(len(result), 0)
        for dim in result:
            self.assertLess(dim['score'], 60)

    def test_diagnose_weak_dimensions_sorted_by_score(self):
        from app.utils.ability_matrix_calculator import diagnose_weak_dimensions
        result = diagnose_weak_dimensions({
            'syntax_score': 55, 'algorithm_score': 45,
            'project_score': 50, 'debug_score': 40, 'security_score': 60
        })
        scores = [d['score'] for d in result]
        self.assertEqual(scores, sorted(scores))

    def test_diagnose_weak_dimensions_have_suggestions(self):
        from app.utils.ability_matrix_calculator import diagnose_weak_dimensions
        result = diagnose_weak_dimensions({
            'syntax_score': 80, 'algorithm_score': 40,
            'project_score': 90, 'debug_score': 45, 'security_score': 85
        })
        for dim in result:
            self.assertIn('suggestion', dim)
            self.assertTrue(len(dim['suggestion']) > 0)


class TestModelConstants(unittest.TestCase):
    """验证模型层常量的完整性和一致性"""

    def test_ability_dimensions_count(self):
        from app.utils.ability_matrix_calculator import ABILITY_DIMENSIONS
        self.assertEqual(len(ABILITY_DIMENSIONS), 5)

    def test_ability_dimensions_five_expected(self):
        from app.utils.ability_matrix_calculator import ABILITY_DIMENSIONS
        expected = {
            'syntax_score', 'algorithm_score', 'project_score',
            'debug_score', 'security_score'
        }
        self.assertEqual(set(ABILITY_DIMENSIONS), expected)

    def test_dimension_labels_count(self):
        from app.utils.ability_matrix_calculator import DIMENSION_LABELS
        self.assertEqual(len(DIMENSION_LABELS), 5)

    def test_dimension_labels_match_dimensions(self):
        from app.utils.ability_matrix_calculator import ABILITY_DIMENSIONS, DIMENSION_LABELS
        self.assertEqual(set(DIMENSION_LABELS.keys()), set(ABILITY_DIMENSIONS))

    def test_dimension_labels_are_chinese(self):
        from app.utils.ability_matrix_calculator import DIMENSION_LABELS
        for label in DIMENSION_LABELS.values():
            self.assertTrue(any('\u4e00' <= c <= '\u9fff' for c in label),
                            f"Label '{label}' 不含中文字符")

    def test_level_thresholds_count(self):
        from app.utils.ability_matrix_calculator import LEVEL_THRESHOLDS
        self.assertEqual(len(LEVEL_THRESHOLDS), 4)

    def test_level_thresholds_keys(self):
        from app.utils.ability_matrix_calculator import LEVEL_THRESHOLDS
        self.assertIn('专家', LEVEL_THRESHOLDS)
        self.assertIn('高级', LEVEL_THRESHOLDS)
        self.assertIn('中级', LEVEL_THRESHOLDS)
        self.assertIn('初级', LEVEL_THRESHOLDS)

    def test_learn_recommendations_have_all_dimensions(self):
        from app.utils.ability_matrix_calculator import ABILITY_DIMENSIONS, get_recommended_tasks
        for dim in ABILITY_DIMENSIONS:
            tasks = get_recommended_tasks(dim)
            self.assertIsInstance(tasks, list)
            self.assertGreater(len(tasks), 0)

    def test_learn_recommendations_structure(self):
        from app.utils.ability_matrix_calculator import get_recommended_tasks
        tasks = get_recommended_tasks('syntax_score')
        for task in tasks:
            self.assertIn('title', task)
            self.assertIn('type', task)
            self.assertIn('difficulty', task)


class TestModelCircularDependency(unittest.TestCase):
    """验证循环依赖约束"""

    def _get_code_only(self, source):
        """去除注释行，只保留实际代码"""
        lines = source.split('\n')
        code_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            if stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            code_lines.append(line)
        return '\n'.join(code_lines)

    def test_ability_matrix_model_no_service_import(self):
        """ability_matrix_model 不应导入任何 service 模块"""
        import inspect
        from app.models import ability_matrix_model

        source = inspect.getsource(ability_matrix_model)
        code_only = self._get_code_only(source)
        forbidden = [
            'from app.service',
            'import app.service',
        ]
        for pattern in forbidden:
            self.assertNotIn(pattern, code_only,
                             f"ability_matrix_model 包含禁止的导入: {pattern}")

    def test_db_model_no_service_import(self):
        """db.py 不应导入任何 service 模块"""
        import inspect
        from app.models import db

        source = inspect.getsource(db)
        code_only = self._get_code_only(source)
        forbidden = [
            'from app.service',
            'import app.service',
        ]
        for pattern in forbidden:
            self.assertNotIn(pattern, code_only,
                             f"db.py 包含禁止的导入: {pattern}")

    def test_calculator_no_model_import(self):
        """ability_matrix_calculator 不应导入任何 model 模块"""
        import inspect
        from app.utils import ability_matrix_calculator

        source = inspect.getsource(ability_matrix_calculator)
        code_only = self._get_code_only(source)
        forbidden = [
            'from app.models',
            'import app.models',
            'from app.service',
            'import app.service',
        ]
        for pattern in forbidden:
            self.assertNotIn(pattern, code_only,
                             f"ability_matrix_calculator 包含禁止的导入: {pattern}")

    def test_constants_no_model_or_service_import(self):
        """constants.py 不应导入 model 或 service"""
        import inspect
        from app.utils import constants

        source = inspect.getsource(constants)
        code_only = self._get_code_only(source)
        forbidden = [
            'from app.models',
            'import app.models',
            'from app.service',
            'import app.service',
        ]
        for pattern in forbidden:
            self.assertNotIn(pattern, code_only,
                             f"constants.py 包含禁止的导入: {pattern}")


class TestServicePureLogic(unittest.TestCase):
    """验证 Service 层中的纯逻辑"""

    def test_ability_matrix_service_dimensions_match(self):
        from app.service.ability_matrix_service import AbilityMatrixService
        from app.utils.ability_matrix_calculator import ABILITY_DIMENSIONS

        self.assertEqual(AbilityMatrixService.DIMENSIONS, ABILITY_DIMENSIONS)

    def test_ability_matrix_service_labels_match(self):
        from app.service.ability_matrix_service import AbilityMatrixService
        from app.utils.ability_matrix_calculator import DIMENSION_LABELS

        self.assertEqual(AbilityMatrixService.DIMENSION_LABELS, DIMENSION_LABELS)

    def test_ability_matrix_service_has_expected_static_methods(self):
        from app.service.ability_matrix_service import AbilityMatrixService

        expected_methods = [
            'get_user_matrix',
            'init_user_matrix',
            'submit_code_evaluation',
            'evaluate_code_with_ai',
        ]
        for method in expected_methods:
            self.assertTrue(
                hasattr(AbilityMatrixService, method),
                f"AbilityMatrixService 缺少方法: {method}"
            )

    def test_question_model_has_expected_methods(self):
        from app.models.question_model import QuestionModel

        expected_methods = [
            'get_all_questions',
            'get_question_by_id',
            'search_questions_by_title',
            'update_question',
        ]
        for method in expected_methods:
            self.assertTrue(
                hasattr(QuestionModel, method),
                f"QuestionModel 缺少方法: {method}"
            )


class TestDBConverters(unittest.TestCase):
    """验证 db_converters 模块"""

    def test_dict_to_markdown_plain_dict(self):
        from app.models.db_converters import dict_to_markdown
        result = dict_to_markdown({"标题": "内容"})
        self.assertIn("### 标题", result)
        self.assertIn("内容", result)

    def test_dict_to_markdown_list_values(self):
        from app.models.db_converters import dict_to_markdown
        result = dict_to_markdown({"章节": ["A", "B"]})
        self.assertIn("- A", result)
        self.assertIn("- B", result)

    def test_dict_to_markdown_empty(self):
        from app.models.db_converters import dict_to_markdown
        result = dict_to_markdown({})
        self.assertEqual(result, "")

    def test_dict_to_markdown_non_dict_passthrough(self):
        from app.models.db_converters import dict_to_markdown
        result = dict_to_markdown("plain text")
        self.assertEqual(result, "plain text")

    def test_db_utils_fetch_dict(self):
        from app.models.db_utils import fetch_dict
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]

        result = fetch_dict(mock_cursor)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"id": 1, "name": "Alice"})

    def test_db_utils_fetch_one_dict(self):
        from app.models.db_utils import fetch_one_dict
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchone.return_value = (1, "Alice")

        result = fetch_one_dict(mock_cursor)
        self.assertEqual(result, {"id": 1, "name": "Alice"})

    def test_db_utils_fetch_one_dict_empty(self):
        from app.models.db_utils import fetch_one_dict
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",)]
        mock_cursor.fetchone.return_value = None

        result = fetch_one_dict(mock_cursor)
        self.assertIsNone(result)


class TestQuestionModel(unittest.TestCase):
    """题库模型测试"""

    def test_question_model_class_exists(self):
        from app.models.question_model import QuestionModel
        self.assertIsNotNone(QuestionModel)

    def test_question_model_has_expected_methods(self):
        from app.models.question_model import QuestionModel

        expected_methods = [
            'get_all_questions',
            'get_question_by_id',
            'search_questions_by_title',
            'update_question',
        ]
        for method in expected_methods:
            self.assertTrue(
                hasattr(QuestionModel, method),
                f"QuestionModel 缺少方法: {method}"
            )

    @patch('app.models.question_db.get_db_connection')
    def test_get_all_questions_returns_list(self, mock_conn):
        mock_cursor = MagicMock()
        mock_cursor.description = [
            ("id",), ("title",), ("difficulty",), ("content",)
        ]
        mock_cursor.fetchall.return_value = [
            (1, "两数之和", "简单", "经典题目"),
            (2, "反转链表", "中等", "链表操作"),
        ]
        mock_conn.return_value.cursor.return_value = mock_cursor

        from app.models.question_model import QuestionModel
        result = QuestionModel.get_all_questions()
        self.assertIn("questions", result)

    @patch('app.models.question_db.get_db_connection')
    def test_get_question_by_id_found(self, mock_conn):
        mock_cursor = MagicMock()
        mock_cursor.description = [
            ("id",), ("title",), ("difficulty",), ("content",)
        ]
        mock_cursor.fetchone.return_value = (1, "两数之和", "简单", "经典题目")
        mock_conn.return_value.cursor.return_value = mock_cursor

        from app.models.question_model import QuestionModel
        result = QuestionModel.get_question_by_id("1")
        self.assertIsInstance(result, dict)
        self.assertIn("question", result)

    @patch('app.models.question_db.get_db_connection')
    def test_get_question_by_id_not_found(self, mock_conn):
        mock_cursor = MagicMock()
        mock_cursor.description = [
            ("id",), ("title",), ("difficulty",), ("content",)
        ]
        mock_cursor.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = mock_cursor

        from app.models.question_model import QuestionModel
        result = QuestionModel.get_question_by_id("99999")
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    @patch('app.models.question_db.get_db_connection')
    def test_search_questions_by_title(self, mock_conn):
        mock_cursor = MagicMock()
        mock_cursor.description = [
            ("id",), ("title",), ("difficulty",), ("content",)
        ]
        mock_cursor.fetchall.return_value = [
            (1, "两数之和", "简单", "经典题目"),
        ]
        mock_conn.return_value.cursor.return_value = mock_cursor

        from app.models.question_model import QuestionModel
        result = QuestionModel.search_questions_by_title("两数")
        self.assertIsInstance(result, dict)
        self.assertIn("questions", result)


class TestUserModel(unittest.TestCase):
    """用户模型测试"""

    def test_auth_utils_importable(self):
        from app.utils.auth import (
            get_current_user_id,
            is_authenticated,
            get_authenticated_user_id,
            require_auth,
            set_user_session,
            clear_session,
        )
        self.assertTrue(callable(get_current_user_id))
        self.assertTrue(callable(is_authenticated))
        self.assertTrue(callable(get_authenticated_user_id))
        self.assertTrue(callable(require_auth))
        self.assertTrue(callable(set_user_session))
        self.assertTrue(callable(clear_session))


class TestDBConnection(unittest.TestCase):
    """数据库连接模块测试"""

    def test_db_connection_module_exists(self):
        from app.models import db_connection
        self.assertIsNotNone(db_connection)

    def test_get_db_connection_exists(self):
        from app.models.db_connection import get_db_connection
        self.assertTrue(callable(get_db_connection))

    def test_init_database_exists(self):
        from app.models.db_connection import init_database
        self.assertTrue(callable(init_database))

    def test_get_create_statements_exists(self):
        from app.models.db_connection import get_create_statements
        self.assertTrue(callable(get_create_statements))

    def test_get_create_statements_returns_list(self):
        from app.models.db_connection import get_create_statements
        stmts = get_create_statements()
        self.assertIsInstance(stmts, list)
        self.assertGreater(len(stmts), 0)

    def test_create_statements_are_sql_strings(self):
        from app.models.db_connection import get_create_statements
        stmts = get_create_statements()
        for stmt in stmts:
            self.assertIsInstance(stmt, str)
            upper = stmt.upper()
            self.assertTrue(
                upper.startswith('CREATE') or upper.startswith('ALTER'),
                f"Statement 不以 CREATE/ALTER 开头: {stmt[:50]}"
            )

    def test_expected_tables_in_statements(self):
        from app.models.db_connection import get_create_statements
        stmts = get_create_statements()
        all_sql = ' '.join(stmts).upper()
        expected_tables = [
            'USERS', 'ABILITY_MATRIX', 'FAVORITES',
            'PROBLEMS', 'TEST_CASES', 'USER_UPLOADS',
        ]
        for table in expected_tables:
            self.assertIn(table, all_sql,
                          f"建表语句中缺少表: {table}")


if __name__ == '__main__':
    unittest.main()