"""
Phase 6 测试: 全面集成测试

覆盖:
- 跨模块数据流验证 (Calculator → Model → Service)
- 路由注册完整性验证
- 错误处理一致性验证
- 数据转换管道验证
"""

import unittest
from unittest.mock import MagicMock, patch


class TestDataFlowIntegration(unittest.TestCase):
    """Calculator → Model → Service 数据流集成测试"""

    def test_calculator_to_model_level_flow(self):
        """验证 calculator 等级计算结果能正确通过 model 层传递"""
        from app.utils.ability_matrix_calculator import calculate_level
        from app.models.ability_matrix_model import calculate_level as model_calculate

        scores = {
            'syntax_score': 95, 'algorithm_score': 92,
            'project_score': 90, 'debug_score': 88, 'security_score': 95
        }

        calc_result = calculate_level(scores)
        model_result = model_calculate(scores)

        self.assertEqual(calc_result, model_result)
        self.assertEqual(calc_result, '专家')

    def test_calculator_to_model_dimensions_flow(self):
        """验证维度字典构建在 calculator 和 model 间一致"""
        from app.utils.ability_matrix_calculator import build_dimensions_dict
        from app.models.ability_matrix_model import build_dimensions_dict as model_build

        scores = {
            'syntax_score': 75, 'algorithm_score': 65,
            'project_score': 80, 'debug_score': 70, 'security_score': 85
        }

        calc_result = build_dimensions_dict(scores)
        model_result = model_build(scores)

        self.assertEqual(calc_result, model_result)
        self.assertIn('syntax_score', calc_result)
        self.assertIn('algorithm_score', calc_result)

    def test_calculator_to_model_weak_diagnose_flow(self):
        """验证薄弱维度诊断数据流"""
        from app.utils.ability_matrix_calculator import diagnose_weak_dimensions
        from app.models.ability_matrix_model import diagnose_weak_dimensions as model_diagnose

        scores = {
            'syntax_score': 85, 'algorithm_score': 40,
            'project_score': 90, 'debug_score': 45, 'security_score': 80
        }

        calc_result = diagnose_weak_dimensions(scores)
        model_result = model_diagnose(scores)

        self.assertEqual(calc_result, model_result)
        self.assertGreater(len(calc_result), 0)

    def test_level_labels_consistency_across_modules(self):
        """验证等级标签在所有模块中一致"""
        from app.utils.constants import LEVEL_LABELS
        from app.utils.ability_matrix_calculator import calculate_level

        test_cases = [
            ({
                'syntax_score': 0, 'algorithm_score': 0,
                'project_score': 0, 'debug_score': 0, 'security_score': 0
            }, '初学者'),
            ({
                'syntax_score': 25, 'algorithm_score': 25,
                'project_score': 25, 'debug_score': 25, 'security_score': 25
            }, '初级'),
            ({
                'syntax_score': 50, 'algorithm_score': 50,
                'project_score': 50, 'debug_score': 50, 'security_score': 50
            }, '中级'),
            ({
                'syntax_score': 75, 'algorithm_score': 75,
                'project_score': 75, 'debug_score': 75, 'security_score': 75
            }, '高级'),
            ({
                'syntax_score': 92, 'algorithm_score': 92,
                'project_score': 92, 'debug_score': 92, 'security_score': 92
            }, '专家'),
        ]

        for scores, expected_level in test_cases:
            level = calculate_level(scores)
            self.assertEqual(level, expected_level)
            self.assertIn(level, LEVEL_LABELS)

    def test_service_uses_calculator_constants(self):
        """验证 Service 层使用的常量与 Calculator 一致"""
        from app.service.ability_matrix_service import AbilityMatrixService
        from app.utils.ability_matrix_calculator import (
            ABILITY_DIMENSIONS,
            DIMENSION_LABELS,
        )

        self.assertEqual(AbilityMatrixService.DIMENSIONS, ABILITY_DIMENSIONS)
        self.assertEqual(AbilityMatrixService.DIMENSION_LABELS, DIMENSION_LABELS)

    def test_model_updates_uses_calculator_functions(self):
        """验证模型更新逻辑正确调用 calculator 函数"""
        from app.utils.ability_matrix_calculator import calculate_level

        scores = {
            'syntax_score': 60, 'algorithm_score': 70,
            'project_score': 80, 'debug_score': 65, 'security_score': 75
        }
        level = calculate_level(scores)
        self.assertEqual(level, '中级')

        scores2 = {
            'syntax_score': 80, 'algorithm_score': 85,
            'project_score': 90, 'debug_score': 75, 'security_score': 85
        }
        level2 = calculate_level(scores2)
        self.assertEqual(level2, '高级')


class TestRouteRegistration(unittest.TestCase):
    """路由注册完整性验证"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test_secret'
        self.app.config['TESTING'] = True

    def test_all_blueprints_registerable(self):
        """验证所有蓝图可正确注册"""
        from app.api import (
            ability_matrix_bp,
            auth_bp,
            user_api_bp,
            main_bp,
        )

        blueprints = [
            ability_matrix_bp,
            auth_bp,
            user_api_bp,
            main_bp,
        ]

        for bp in blueprints:
            self.app.register_blueprint(bp)

    def test_ability_matrix_routes_exist(self):
        """验证能力矩阵路由端点存在"""
        from app.api import ability_matrix_bp
        self.assertGreater(len(ability_matrix_bp.deferred_functions), 0)

    def test_auth_routes_exist(self):
        """验证认证路由端点存在"""
        from app.api import auth_bp
        self.assertGreater(len(auth_bp.deferred_functions), 0)

    def test_user_api_routes_exist(self):
        """验证用户 API 路由端点存在"""
        from app.api import user_api_bp
        self.assertGreater(len(user_api_bp.deferred_functions), 0)

    def test_main_routes_exist(self):
        """验证主路由端点存在"""
        from app.api import main_bp
        self.assertGreater(len(main_bp.deferred_functions), 0)


class TestErrorHandlingConsistency(unittest.TestCase):
    """错误处理一致性验证"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test_secret'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_all_protected_routes_return_401_unauthenticated(self):
        """验证所有受保护路由在未认证时返回 401"""
        from app.api import ability_matrix_bp, user_api_bp
        self.app.register_blueprint(ability_matrix_bp)
        self.app.register_blueprint(user_api_bp)

        protected_routes = [
            ('/api/ability-matrix', 'GET'),
            ('/api/ability-matrix/submit', 'POST'),
            ('/api/user/favorites', 'GET'),
        ]

        for url, method in protected_routes:
            if method == 'GET':
                resp = self.client.get(url)
            else:
                resp = self.client.post(
                    url,
                    data='{}',
                    content_type='application/json'
                )
            self.assertEqual(
                resp.status_code, 401,
                f"路由 {method} {url} 未认证时应返回 401, 实际返回 {resp.status_code}"
            )

    def test_401_response_format(self):
        """验证 401 响应格式一致"""
        from flask import Flask
        from app.utils.auth import require_auth

        self.app2 = Flask(__name__)
        self.app2.config['SECRET_KEY'] = 'test'
        self.app2.config['TESTING'] = True

        @self.app2.route('/test-protected')
        @require_auth
        def test_protected():
            return 'ok'

        client = self.app2.test_client()
        resp = client.get('/test-protected')
        self.assertEqual(resp.status_code, 401)

        data = resp.get_json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 401)
        self.assertIn('message', data)

    def test_missing_fields_handling(self):
        """验证缺失字段的错误处理"""
        from app.api import ability_matrix_bp
        self.app.register_blueprint(ability_matrix_bp)

        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'testuser'

            resp = client.post(
                '/api/ability-matrix/submit',
                data='{}',
                content_type='application/json'
            )
            self.assertEqual(resp.status_code, 400)


class TestAuthDataFlow(unittest.TestCase):
    """认证数据流集成测试"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_auth_session_lifecycle(self):
        """验证 session 生命周期"""
        from app.utils.auth import (
            set_user_session,
            get_current_user_id,
            is_authenticated,
            clear_session,
        )

        with self.app.test_request_context():
            self.assertIsNone(get_current_user_id())
            self.assertFalse(is_authenticated())

            set_user_session('user123')
            self.assertEqual(get_current_user_id(), 'user123')
            self.assertTrue(is_authenticated())

            clear_session()
            self.assertIsNone(get_current_user_id())
            self.assertFalse(is_authenticated())

    def test_require_auth_allows_authenticated_user(self):
        """验证认证用户可通过 require_auth"""
        from flask import jsonify
        from app.utils.auth import require_auth

        @self.app.route('/api/test-auth')
        @require_auth
        def test_auth():
            return jsonify({"status": "ok"})

        with self.client.session_transaction() as sess:
            sess['user_id'] = 'verified_user'

        resp = self.client.get('/api/test-auth')
        self.assertEqual(resp.status_code, 200)

    def test_require_auth_blocks_unauthenticated(self):
        """验证未认证用户被 require_auth 拦截"""
        from flask import jsonify
        from app.utils.auth import require_auth

        @self.app.route('/api/test-auth-2')
        @require_auth
        def test_auth_2():
            return jsonify({"status": "ok"})

        resp = self.client.get('/api/test-auth-2')
        self.assertEqual(resp.status_code, 401)

    def test_get_authenticated_user_id_integration(self):
        """验证 get_authenticated_user_id 完整流程"""
        from app.utils.auth import get_authenticated_user_id

        with self.app.test_request_context():
            user_id, err = get_authenticated_user_id()
            self.assertIsNone(user_id)
            self.assertIsNotNone(err)

    def test_get_authenticated_user_id_with_session(self):
        """验证带 session 的 get_authenticated_user_id"""
        from flask import session
        from app.utils.auth import get_authenticated_user_id

        with self.app.test_request_context():
            session['user_id'] = 'int_test_user'
            user_id, err = get_authenticated_user_id()
            self.assertEqual(user_id, 'int_test_user')
            self.assertIsNone(err)


class TestDataTransformationPipeline(unittest.TestCase):
    """数据转换管道集成测试"""

    def test_scores_to_level_to_dimensions_pipeline(self):
        """分数 → 等级 → 维度 完整管道"""
        from app.utils.ability_matrix_calculator import (
            calculate_level,
            build_dimensions_dict,
            ABILITY_DIMENSIONS,
        )

        scores = {
            'syntax_score': 80,
            'algorithm_score': 65,
            'project_score': 90,
            'debug_score': 55,
            'security_score': 75,
        }

        level = calculate_level(scores)
        dimensions = build_dimensions_dict(scores)

        self.assertEqual(level, '中级')
        self.assertEqual(len(dimensions), 5)

        for dim in ABILITY_DIMENSIONS:
            self.assertIn(dim, dimensions)
            self.assertIn('label', dimensions[dim])
            self.assertIn('score', dimensions[dim])

    def test_empty_scores_pipeline(self):
        """空分数管道处理"""
        from app.utils.ability_matrix_calculator import (
            calculate_level,
            build_dimensions_dict,
            diagnose_weak_dimensions,
        )

        scores = {}
        level = calculate_level(scores)
        dimensions = build_dimensions_dict(scores)
        weak = diagnose_weak_dimensions(scores)

        self.assertEqual(level, '初学者')
        for dim_data in dimensions.values():
            self.assertEqual(dim_data['score'], 0)
        self.assertEqual(weak, [])

    def test_high_scores_pipeline(self):
        """高分管道处理"""
        from app.utils.ability_matrix_calculator import (
            calculate_level,
            build_dimensions_dict,
            diagnose_weak_dimensions,
        )

        scores = {
            'syntax_score': 95,
            'algorithm_score': 92,
            'project_score': 88,
            'debug_score': 90,
            'security_score': 85,
        }

        level = calculate_level(scores)
        dimensions = build_dimensions_dict(scores)
        weak = diagnose_weak_dimensions(scores)

        self.assertEqual(level, '专家')
        self.assertEqual(len(weak), 0)

    def test_low_score_weak_detection_pipeline(self):
        """低分薄弱检测管道"""
        from app.utils.ability_matrix_calculator import (
            calculate_level,
            diagnose_weak_dimensions,
            get_dimension_suggestion,
        )

        scores = {
            'syntax_score': 50,
            'algorithm_score': 45,
            'project_score': 80,
            'debug_score': 55,
            'security_score': 85,
        }

        weak = diagnose_weak_dimensions(scores)
        level = calculate_level(scores)

        for dim in weak:
            self.assertIn('suggestion', dim)
            suggestion = get_dimension_suggestion(dim['dimension'])
            self.assertEqual(dim['suggestion'], suggestion)

        self.assertLessEqual(level, '中级')


if __name__ == '__main__':
    unittest.main()
