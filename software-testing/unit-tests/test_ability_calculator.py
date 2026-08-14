"""
单元测试: ability_matrix_calculator 纯函数模块

覆盖:
- calculate_level 等级计算
- diagnose_weak_dimensions 薄弱维度诊断
- build_dimensions_dict 维度字典构建
- get_recommended_tasks 推荐任务
- get_dimension_suggestion 学习建议
"""
import unittest
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.utils.ability_matrix_calculator import (
    calculate_level,
    ABILITY_DIMENSIONS,
    DIMENSION_LABELS,
    diagnose_weak_dimensions,
    build_dimensions_dict,
    get_recommended_tasks,
    get_dimension_suggestion,
)


def make_scores(syntax=50, algorithm=50, project=50, debug=50, security=50):
    """辅助函数：构造各维度分数字典"""
    return {
        'syntax_score': syntax,
        'algorithm_score': algorithm,
        'project_score': project,
        'debug_score': debug,
        'security_score': security,
    }


class TestCalculateLevel(unittest.TestCase):
    """calculate_level 等级计算逻辑测试"""

    def test_empty_dict_returns_beginner(self):
        result = calculate_level({})
        self.assertEqual(result, '初学者')

    def test_none_input_returns_beginner(self):
        result = calculate_level(None)
        self.assertEqual(result, '初学者')

    def test_all_zeros_returns_beginner(self):
        scores = make_scores(0, 0, 0, 0, 0)
        result = calculate_level(scores)
        self.assertEqual(result, '初学者')

    def test_all_tens_returns_beginner(self):
        scores = make_scores(10, 10, 10, 10, 10)
        result = calculate_level(scores)
        self.assertEqual(result, '初学者')

    def test_avg_24_returns_beginner(self):
        scores = make_scores(24, 24, 24, 24, 24)
        result = calculate_level(scores)
        self.assertEqual(result, '初学者')

    def test_avg_25_returns_elementary(self):
        scores = make_scores(25, 25, 25, 25, 25)
        result = calculate_level(scores)
        self.assertEqual(result, '初级')

    def test_avg_49_returns_elementary(self):
        scores = make_scores(49, 49, 49, 49, 49)
        result = calculate_level(scores)
        self.assertEqual(result, '初级')

    def test_avg_50_returns_intermediate(self):
        scores = make_scores(50, 50, 50, 50, 50)
        result = calculate_level(scores)
        self.assertEqual(result, '中级')

    def test_avg_74_returns_intermediate(self):
        scores = make_scores(74, 74, 74, 74, 74)
        result = calculate_level(scores)
        self.assertEqual(result, '中级')

    def test_avg_75_returns_advanced(self):
        scores = make_scores(75, 75, 75, 75, 75)
        result = calculate_level(scores)
        self.assertEqual(result, '高级')

    def test_avg_89_returns_advanced(self):
        scores = make_scores(89, 89, 89, 89, 89)
        result = calculate_level(scores)
        self.assertEqual(result, '高级')

    def test_avg_90_returns_expert(self):
        scores = make_scores(90, 90, 90, 90, 90)
        result = calculate_level(scores)
        self.assertEqual(result, '专家')

    def test_perfect_score_returns_expert(self):
        scores = make_scores(100, 100, 100, 100, 100)
        result = calculate_level(scores)
        self.assertEqual(result, '专家')

    def test_mixed_scores_with_override(self):
        scores = make_scores(10, 95, 95, 95, 95)
        result = calculate_level(scores)
        self.assertEqual(result, '高级')

    def test_ability_dimensions_count(self):
        self.assertEqual(len(ABILITY_DIMENSIONS), 5)

    def test_partial_scores_dict(self):
        scores = {'syntax_score': 100}
        result = calculate_level(scores)
        self.assertEqual(result, '初学者')

    def test_partial_scores_above_threshold(self):
        scores = {'syntax_score': 100, 'algorithm_score': 100}
        result = calculate_level(scores)
        self.assertEqual(result, '初级')

    def test_partial_scores_with_four_dims(self):
        scores = make_scores(100, 100, 100, 100, 0)
        result = calculate_level(scores)
        self.assertEqual(result, '高级')

    def test_negative_scores_handled(self):
        scores = make_scores(-10, -5, 0, 5, 10)
        result = calculate_level(scores)
        self.assertEqual(result, '初学者')


class TestDiagnoseWeakDimensions(unittest.TestCase):
    """diagnose_weak_dimensions 薄弱维度诊断测试"""

    def test_empty_scores_returns_empty_list(self):
        result = diagnose_weak_dimensions({})
        self.assertEqual(result, [])

    def test_none_scores_returns_empty_list(self):
        result = diagnose_weak_dimensions(None)
        self.assertEqual(result, [])

    def test_all_equal_no_weak_dimensions(self):
        scores = make_scores(80, 80, 80, 80, 80)
        result = diagnose_weak_dimensions(scores)
        self.assertEqual(result, [])

    def test_one_weak_dimension_detected(self):
        scores = make_scores(90, 90, 30, 90, 90)
        result = diagnose_weak_dimensions(scores)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['dimension'], 'project_score')
        self.assertEqual(result[0]['score'], 30)

    def test_multiple_weak_dimensions(self):
        scores = make_scores(40, 30, 80, 35, 90)
        result = diagnose_weak_dimensions(scores)
        self.assertTrue(len(result) >= 2)

    def test_weak_sorted_by_score_ascending(self):
        scores = make_scores(50, 30, 80, 40, 90)
        result = diagnose_weak_dimensions(scores)
        if len(result) >= 2:
            self.assertLessEqual(result[0]['score'], result[1]['score'])

    def test_weak_dimension_has_suggestion(self):
        scores = make_scores(90, 90, 30, 90, 90)
        result = diagnose_weak_dimensions(scores)
        self.assertTrue(len(result) > 0)
        self.assertIn('suggestion', result[0])
        self.assertTrue(len(result[0]['suggestion']) > 0)

    def test_dimension_score_at_60_not_weak(self):
        """分数 >= 60 即使低于平均分也不算薄弱"""
        scores = make_scores(90, 90, 60, 90, 90)
        result = diagnose_weak_dimensions(scores)
        self.assertEqual(len(result), 0)

    def test_dimension_score_above_avg_not_weak(self):
        """分数高于平均分即使低于 60 也不算薄弱"""
        scores = make_scores(50, 50, 58, 50, 50)
        result = diagnose_weak_dimensions(scores)
        project = [d for d in result if d['dimension'] == 'project_score']
        self.assertEqual(len(project), 0, 'project_score=58 > avg=51.6, 不应被诊断为薄弱')


class TestBuildDimensionsDict(unittest.TestCase):
    """build_dimensions_dict 维度字典构建测试"""

    def test_all_dimensions_present(self):
        scores = make_scores(80, 70, 60, 50, 40)
        result = build_dimensions_dict(scores)
        for dim in ABILITY_DIMENSIONS:
            self.assertIn(dim, result)

    def test_each_dimension_has_label_and_score(self):
        scores = make_scores(80, 70, 60, 50, 40)
        result = build_dimensions_dict(scores)
        for dim in ABILITY_DIMENSIONS:
            self.assertIn('label', result[dim])
            self.assertIn('score', result[dim])

    def test_labels_match_expected(self):
        scores = make_scores(80, 70, 60, 50, 40)
        result = build_dimensions_dict(scores)
        self.assertEqual(result['syntax_score']['label'], '语法基础')
        self.assertEqual(result['algorithm_score']['label'], '算法思维')

    def test_scores_rounded_to_2_decimals(self):
        scores = make_scores(80.555, 70.123, 60.999, 50.001, 40.0)
        result = build_dimensions_dict(scores)
        for dim in ABILITY_DIMENSIONS:
            score = result[dim]['score']
            self.assertEqual(score, round(score, 2))

    def test_missing_dimensions_default_to_zero(self):
        scores = {'syntax_score': 100}
        result = build_dimensions_dict(scores)
        self.assertEqual(result['algorithm_score']['score'], 0)

    def test_empty_scores_all_zeros(self):
        result = build_dimensions_dict({})
        for dim in ABILITY_DIMENSIONS:
            self.assertEqual(result[dim]['score'], 0)


class TestGetRecommendedTasks(unittest.TestCase):
    """get_recommended_tasks 推荐任务测试"""

    def test_valid_dimension_returns_list(self):
        result = get_recommended_tasks('syntax_score')
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    def test_unknown_dimension_returns_empty_list(self):
        result = get_recommended_tasks('unknown_dim')
        self.assertEqual(result, [])

    def test_all_dimensions_have_recommendations(self):
        for dim in ABILITY_DIMENSIONS:
            result = get_recommended_tasks(dim)
            self.assertTrue(len(result) > 0, f"{dim} should have recommendations")

    def test_recommended_task_has_required_fields(self):
        result = get_recommended_tasks('syntax_score')
        for task in result:
            self.assertIn('title', task)
            self.assertIn('type', task)
            self.assertIn('difficulty', task)


class TestGetDimensionSuggestion(unittest.TestCase):
    """get_dimension_suggestion 学习建议测试"""

    def test_valid_dimension_returns_nonempty_string(self):
        for dim in ABILITY_DIMENSIONS:
            result = get_dimension_suggestion(dim)
            self.assertTrue(len(result) > 0, f"{dim} should have suggestion")

    def test_unknown_dimension_returns_default(self):
        result = get_dimension_suggestion('unknown')
        self.assertEqual(result, '继续努力！')

    def test_syntax_suggestion_contains_chinese(self):
        result = get_dimension_suggestion('syntax_score')
        self.assertIn('语法', result)


class TestDimensionLabels(unittest.TestCase):
    """DIMENSION_LABELS 常量测试"""

    def test_all_dimensions_have_labels(self):
        for dim in ABILITY_DIMENSIONS:
            self.assertIn(dim, DIMENSION_LABELS)

    def test_label_count_matches_dimensions(self):
        self.assertEqual(len(DIMENSION_LABELS), len(ABILITY_DIMENSIONS))


if __name__ == '__main__':
    unittest.main()
