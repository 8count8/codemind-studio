"""
Phase 1 测试: 验证常量定义的正确性和一致性

覆盖模块:
- app.utils.constants (HTTPStatus, LevelThresholds, LEVEL_LABELS)
- app.models.db_constants (VALID_DIFFICULTIES, USE_POSTGRESQL)
"""

import unittest


class TestHTTPStatus(unittest.TestCase):
    """验证 HTTP 状态码常量"""

    def setUp(self):
        from app.utils.constants import HTTPStatus
        self.HTTPStatus = HTTPStatus

    def test_ok_is_200(self):
        self.assertEqual(self.HTTPStatus.OK, 200)

    def test_bad_request_is_400(self):
        self.assertEqual(self.HTTPStatus.BAD_REQUEST, 400)

    def test_unauthorized_is_401(self):
        self.assertEqual(self.HTTPStatus.UNAUTHORIZED, 401)

    def test_not_found_is_404(self):
        self.assertEqual(self.HTTPStatus.NOT_FOUND, 404)

    def test_internal_error_is_500(self):
        self.assertEqual(self.HTTPStatus.INTERNAL_ERROR, 500)

    def test_all_status_codes_are_int(self):
        for attr in ['OK', 'BAD_REQUEST', 'UNAUTHORIZED', 'NOT_FOUND', 'INTERNAL_ERROR']:
            self.assertIsInstance(getattr(self.HTTPStatus, attr), int)

    def test_status_codes_in_valid_range(self):
        self.assertTrue(200 <= self.HTTPStatus.OK < 600)
        self.assertTrue(400 <= self.HTTPStatus.BAD_REQUEST < 500)
        self.assertTrue(400 <= self.HTTPStatus.UNAUTHORIZED < 500)
        self.assertTrue(400 <= self.HTTPStatus.NOT_FOUND < 500)
        self.assertTrue(500 <= self.HTTPStatus.INTERNAL_ERROR < 600)

    def test_no_duplicate_status_codes(self):
        codes = [
            self.HTTPStatus.OK,
            self.HTTPStatus.BAD_REQUEST,
            self.HTTPStatus.UNAUTHORIZED,
            self.HTTPStatus.NOT_FOUND,
            self.HTTPStatus.INTERNAL_ERROR,
        ]
        self.assertEqual(len(codes), len(set(codes)))


class TestLevelThresholds(unittest.TestCase):
    """验证等级阈值常量"""

    def setUp(self):
        from app.utils.constants import LevelThresholds
        self.thresholds = LevelThresholds

    def test_expert_threshold_is_90(self):
        self.assertEqual(self.thresholds.EXPERT, 90)

    def test_advanced_threshold_is_75(self):
        self.assertEqual(self.thresholds.ADVANCED, 75)

    def test_intermediate_threshold_is_50(self):
        self.assertEqual(self.thresholds.INTERMEDIATE, 50)

    def test_beginner_threshold_is_25(self):
        self.assertEqual(self.thresholds.BEGINNER, 25)

    def test_thresholds_are_ascending(self):
        self.assertLess(
            self.thresholds.BEGINNER,
            self.thresholds.INTERMEDIATE
        )
        self.assertLess(
            self.thresholds.INTERMEDIATE,
            self.thresholds.ADVANCED
        )
        self.assertLess(
            self.thresholds.ADVANCED,
            self.thresholds.EXPERT
        )

    def test_thresholds_are_int(self):
        for attr in ['EXPERT', 'ADVANCED', 'INTERMEDIATE', 'BEGINNER']:
            self.assertIsInstance(getattr(self.thresholds, attr), int)

    def test_thresholds_positive(self):
        for attr in ['EXPERT', 'ADVANCED', 'INTERMEDIATE', 'BEGINNER']:
            self.assertGreater(getattr(self.thresholds, attr), 0)

    def test_expert_is_highest(self):
        self.assertEqual(self.thresholds.EXPERT, 90)

    def test_no_gaps_in_levels(self):
        """相邻等级之间不应有过大跳跃"""
        self.assertLessEqual(
            self.thresholds.EXPERT - self.thresholds.ADVANCED, 20
        )
        self.assertLessEqual(
            self.thresholds.ADVANCED - self.thresholds.INTERMEDIATE, 30
        )


class TestLevelLabels(unittest.TestCase):
    """验证等级标签映射"""

    def setUp(self):
        from app.utils.constants import LEVEL_LABELS
        self.labels = LEVEL_LABELS

    def test_has_five_levels(self):
        self.assertEqual(len(self.labels), 5)

    def test_expert_label_exists(self):
        self.assertIn('专家', self.labels)

    def test_advanced_label_exists(self):
        self.assertIn('高级', self.labels)

    def test_intermediate_label_exists(self):
        self.assertIn('中级', self.labels)

    def test_beginner_label_exists(self):
        self.assertIn('初级', self.labels)

    def test_novice_label_exists(self):
        self.assertIn('初学者', self.labels)

    def test_all_labels_are_strings(self):
        for key, value in self.labels.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, str)

    def test_keys_match_values(self):
        """标签的 key 和 value 应该一致"""
        for key, value in self.labels.items():
            self.assertEqual(key, value)

    def test_label_values_are_chinese(self):
        expected = {'专家', '高级', '中级', '初级', '初学者'}
        self.assertEqual(set(self.labels.keys()), expected)


class TestDBConstants(unittest.TestCase):
    """验证数据库常量"""

    def setUp(self):
        from app.models.db_constants import USE_POSTGRESQL, VALID_DIFFICULTIES
        self.use_postgresql = USE_POSTGRESQL
        self.valid_difficulties = VALID_DIFFICULTIES

    def test_use_postgresql_is_bool(self):
        self.assertIsInstance(self.use_postgresql, bool)

    def test_valid_difficulties_is_list(self):
        self.assertIsInstance(self.valid_difficulties, list)

    def test_valid_difficulties_count(self):
        self.assertEqual(len(self.valid_difficulties), 3)

    def test_valid_difficulties_values(self):
        self.assertIn('简单', self.valid_difficulties)
        self.assertIn('中等', self.valid_difficulties)
        self.assertIn('困难', self.valid_difficulties)

    def test_valid_difficulties_no_duplicates(self):
        self.assertEqual(
            len(self.valid_difficulties),
            len(set(self.valid_difficulties))
        )

    def test_valid_difficulties_sorted(self):
        """难度等级应从低到高排列"""
        difficulty_order = {'简单': 0, '中等': 1, '困难': 2}
        sorted_values = sorted(
            self.valid_difficulties,
            key=lambda x: difficulty_order.get(x, 99)
        )
        self.assertEqual(self.valid_difficulties, sorted_values)

    def test_all_difficulties_are_strings(self):
        for d in self.valid_difficulties:
            self.assertIsInstance(d, str)

    def test_custom_difficulty_not_valid(self):
        self.assertNotIn('地狱', self.valid_difficulties)


class TestConstantsConsistency(unittest.TestCase):
    """跨模块常量一致性验证"""

    def test_http_status_used_in_auth(self):
        """验证 auth 模块使用的状态码与常量一致"""
        from app.utils.constants import HTTPStatus
        from app.utils.auth import require_auth

        self.assertEqual(HTTPStatus.UNAUTHORIZED, 401)
        self.assertEqual(HTTPStatus.OK, 200)

    def test_level_thresholds_match_calculator(self):
        """验证等级阈值在 constants 和 calculator 中一致"""
        from app.utils.constants import LevelThresholds
        from app.utils.ability_matrix_calculator import LEVEL_THRESHOLDS

        self.assertEqual(
            LevelThresholds.EXPERT,
            LEVEL_THRESHOLDS['专家']
        )
        self.assertEqual(
            LevelThresholds.ADVANCED,
            LEVEL_THRESHOLDS['高级']
        )
        self.assertEqual(
            LevelThresholds.INTERMEDIATE,
            LEVEL_THRESHOLDS['中级']
        )
        self.assertEqual(
            LevelThresholds.BEGINNER,
            LEVEL_THRESHOLDS['初级']
        )

    def test_difficulty_constants_match_db(self):
        """验证难度常量在 db_constants 和 db.py 重导出中一致"""
        from app.models.db_constants import VALID_DIFFICULTIES
        from app.models.db import VALID_DIFFICULTIES as DB_DIFFICULTIES

        self.assertEqual(VALID_DIFFICULTIES, DB_DIFFICULTIES)

    def test_level_labels_match_calculator_levels(self):
        """验证 LEVEL_LABELS 的 key 与 calculator 的等级输出一致"""
        from app.utils.constants import LEVEL_LABELS
        from app.utils.ability_matrix_calculator import calculate_level

        all_labels = set(LEVEL_LABELS.keys())
        test_scores = {
            'all_zeros': {
                'syntax_score': 0, 'algorithm_score': 0,
                'project_score': 0, 'debug_score': 0, 'security_score': 0
            },
            'all_25': {
                'syntax_score': 25, 'algorithm_score': 25,
                'project_score': 25, 'debug_score': 25, 'security_score': 25
            },
            'all_50': {
                'syntax_score': 50, 'algorithm_score': 50,
                'project_score': 50, 'debug_score': 50, 'security_score': 50
            },
            'all_75': {
                'syntax_score': 75, 'algorithm_score': 75,
                'project_score': 75, 'debug_score': 75, 'security_score': 75
            },
            'all_90': {
                'syntax_score': 90, 'algorithm_score': 90,
                'project_score': 90, 'debug_score': 90, 'security_score': 90
            },
        }

        for name, scores in test_scores.items():
            level = calculate_level(scores)
            self.assertIn(level, all_labels,
                          f"{name} 产生的等级 '{level}' 不在 LEVEL_LABELS 中")


if __name__ == '__main__':
    unittest.main()