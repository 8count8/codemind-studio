"""
Phase 6 测试: 端到端流程测试

覆盖:
- 用户认证端到端流程
- 能力矩阵评估端到端流程
- 代码提交 → 评分 → 历史流程
- 收藏添加/删除流程
- 完整用户旅程
"""

import unittest
import json
from unittest.mock import patch, MagicMock


class TestUserAuthE2E(unittest.TestCase):
    """用户认证端到端流程"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'e2e_test_secret'
        self.app.config['TESTING'] = True

        from app.api import auth_bp
        self.app.register_blueprint(auth_bp)
        self.client = self.app.test_client()

    def test_login_page_loads(self):
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)

    def test_register_page_loads(self):
        resp = self.client.get('/register')
        self.assertEqual(resp.status_code, 200)

    def test_auth_status_unauthenticated(self):
        resp = self.client.get('/auth/status')
        data = resp.get_json()
        self.assertFalse(data.get('isAuthenticated', True))

    def test_logout_when_not_logged_in(self):
        resp = self.client.get('/logout')
        self.assertIn(resp.status_code, (200, 302))


class TestAbilityMatrixE2E(unittest.TestCase):
    """能力矩阵端到端流程"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'e2e_test_secret'
        self.app.config['TESTING'] = True

        from app.api import ability_matrix_bp
        self.app.register_blueprint(ability_matrix_bp)
        self.client = self.app.test_client()

    @patch('app.api.ability_matrix_routes.AbilityMatrixService')
    def test_full_matrix_workflow(self, mock_svc):
        """完整能力矩阵工作流: 获取 → 提交 → 获取"""
        mock_svc.init_user_matrix.return_value = None
        mock_svc.get_user_matrix.return_value = (
            {
                'syntax_score': 80,
                'algorithm_score': 70,
                'level': '中级',
                'dimensions': {},
                'weak_dimensions': [],
                'average_score': 75,
                'total_submissions': 0,
            },
            200
        )
        mock_svc.submit_code_evaluation.return_value = (
            {
                'scores': {'syntax_score': 85},
                'detail': {'feedback': 'Good'},
            },
            200
        )

        with self.client.session_transaction() as sess:
            sess['user_id'] = 'e2e_test_user'

        # 获取初始矩阵
        resp = self.client.get('/api/ability-matrix')
        self.assertEqual(resp.status_code, 200)

        # 提交代码评估
        resp = self.client.post(
            '/api/ability-matrix/submit',
            data=json.dumps({
                'code': 'def hello(): return 1',
                'question_id': 'q1'
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

        # 再次获取矩阵
        resp = self.client.get('/api/ability-matrix')
        self.assertEqual(resp.status_code, 200)

        # 清除 session 后返回 401
        with self.client.session_transaction() as sess:
            sess.clear()
        resp = self.client.get('/api/ability-matrix')
        self.assertEqual(resp.status_code, 401)

    @patch('app.api.ability_matrix_routes.AbilityMatrixService')
    def test_submit_empty_code_validation(self, mock_svc):
        """提交空代码验证"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'e2e_test_user'

        resp = self.client.post(
            '/api/ability-matrix/submit',
            data=json.dumps({'code': ''}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

    def test_submit_without_auth(self):
        """未认证提交代码返回 401"""
        resp = self.client.post(
            '/api/ability-matrix/submit',
            data=json.dumps({'code': 'x=1'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 401)

    @patch('app.api.ability_matrix_routes.AbilityMatrixService')
    def test_matrix_page_with_auth(self, mock_svc):
        """认证用户访问矩阵页面"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'e2e_test_user'

        resp = self.client.get('/ability-matrix')
        self.assertEqual(resp.status_code, 200)

    def test_matrix_page_without_auth(self):
        """未认证用户访问矩阵页面"""
        resp = self.client.get('/ability-matrix')
        self.assertEqual(resp.status_code, 401)


class TestCodeSubmissionE2E(unittest.TestCase):
    """代码提交端到端流程"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'e2e_test_secret'
        self.app.config['TESTING'] = True

        from app.api import user_api_bp
        self.app.register_blueprint(user_api_bp)
        self.client = self.app.test_client()

    @patch('app.api.user_api.FavoriteService')
    def test_add_favorite_workflow(self, mock_fs):
        """添加收藏完整工作流"""
        mock_fs.add_favorite.return_value = {"status": 200}

        with self.client.session_transaction() as sess:
            sess['user_id'] = 'e2e_fav_user'

        resp = self.client.post(
            '/api/user/favorites',
            data=json.dumps({
                "questionId": "q100",
                "action": "add",
                "title": "测试题目",
                "content": "题目内容",
                "difficulty": "中等",
                "tags": ["数组", "字符串"]
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

    @patch('app.api.user_api.FavoriteService')
    def test_remove_favorite_workflow(self, mock_fs):
        """删除收藏完整工作流"""
        mock_fs.delete_favorite.return_value = {"status": 200}

        with self.client.session_transaction() as sess:
            sess['user_id'] = 'e2e_fav_user'

        resp = self.client.post(
            '/api/user/favorites',
            data=json.dumps({
                "questionId": "q100",
                "action": "remove",
                "title": "测试题目"
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

    def test_favorite_operations_require_auth(self):
        """收藏操作需要认证"""
        resp = self.client.get('/api/user/favorites')
        self.assertEqual(resp.status_code, 401)

        resp = self.client.post(
            '/api/user/favorites',
            data=json.dumps({
                "questionId": "q1",
                "action": "add",
                "title": "test"
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 401)

    def test_invalid_favorite_action(self):
        """无效收藏操作返回 400"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'e2e_fav_user'

        resp = self.client.post(
            '/api/user/favorites',
            data=json.dumps({
                "questionId": "q1",
                "action": "invalid_action",
                "title": "test"
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

    @patch('app.api.user_api.FavoriteService')
    def test_get_favorites_list(self, mock_fs):
        """获取收藏列表"""
        mock_fs.get_favorites_without_question.return_value = {
            "favorites": [
                {"id": 1, "question_id": "q1", "title": "题目1"},
                {"id": 2, "question_id": "q2", "title": "题目2"},
            ]
        }

        with self.client.session_transaction() as sess:
            sess['user_id'] = 'e2e_fav_user'

        resp = self.client.get('/api/user/favorites')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('data', data)

    @patch('app.api.user_api.QuestionService')
    def test_get_questions_list(self, mock_qs):
        """获取题库列表"""
        mock_qs.get_all_questions.return_value = {
            "questions": [
                {"id": 1, "title": "题目1", "difficulty": "简单"},
                {"id": 2, "title": "题目2", "difficulty": "中等"},
            ]
        }

        resp = self.client.get('/api/questions')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('data', data)


class TestPageNavigationE2E(unittest.TestCase):
    """页面导航端到端测试"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'e2e_test_secret'
        self.app.config['TESTING'] = True

        from app.api import main_bp
        self.app.register_blueprint(main_bp)
        self.client = self.app.test_client()

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_dashboard_page(self):
        resp = self.client.get('/dashboard')
        self.assertEqual(resp.status_code, 200)

    def test_csrf_token_page(self):
        resp = self.client.get('/api/csrf-token')
        self.assertEqual(resp.status_code, 200)

    @patch('app.api.profile_routes.get_user_profile')
    def test_profile_page_with_auth(self, mock_profile):
        """认证用户访问 profile"""
        mock_profile.return_value = {
            'username': 'testuser',
            'email': 'test@example.com'
        }

        from app.api import profile_bp
        self.app.register_blueprint(profile_bp)

        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'

        resp = self.client.get('/profile')
        self.assertEqual(resp.status_code, 200)

    def test_profile_page_without_auth(self):
        """未认证用户访问 profile"""
        from app.api import profile_bp
        self.app.register_blueprint(profile_bp)

        resp = self.client.get('/profile')
        self.assertEqual(resp.status_code, 401)


class TestCompleteUserJourney(unittest.TestCase):
    """完整用户旅程端到端测试"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'e2e_test_secret'
        self.app.config['TESTING'] = True

        from app.api import (
            ability_matrix_bp,
            auth_bp,
            user_api_bp,
            main_bp,
            profile_bp,
        )

        self.app.register_blueprint(ability_matrix_bp)
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(user_api_bp)
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(profile_bp)

        self.client = self.app.test_client()

    @patch('app.api.ability_matrix_routes.AbilityMatrixService')
    @patch('app.api.user_api.FavoriteService')
    @patch('app.api.profile_routes.get_user_profile')
    def test_complete_learning_journey(self, mock_profile, mock_fs, mock_am):
        """完整学习旅程: 登录 → 获取矩阵 → 提交代码 → 收藏 → 登出"""
        mock_am.init_user_matrix.return_value = None
        mock_am.get_user_matrix.return_value = (
            {
                'syntax_score': 75, 'algorithm_score': 60,
                'level': '中级',
                'dimensions': {},
                'weak_dimensions': [],
                'average_score': 67.5,
                'total_submissions': 3,
            },
            200
        )
        mock_am.submit_code_evaluation.return_value = (
            {'scores': {'syntax_score': 80, 'algorithm_score': 65}},
            200
        )
        mock_fs.get_favorites_without_question.return_value = {
            "favorites": [{"id": 1}]
        }
        mock_fs.add_favorite.return_value = {"status": 200}
        mock_fs.delete_favorite.return_value = {"status": 200}
        mock_profile.return_value = {
            'username': 'journey_user',
            'email': 'journey@example.com'
        }

        # 检查初始状态（未登录）
        resp = self.client.get('/auth/status')
        data = resp.get_json()
        self.assertFalse(data.get('isAuthenticated', True))

        # 模拟登录
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'journey_user'

        # 验证已登录
        resp = self.client.get('/auth/status')
        data = resp.get_json()
        self.assertTrue(data.get('isAuthenticated'))

        # 访问能力矩阵
        resp = self.client.get('/api/ability-matrix')
        self.assertEqual(resp.status_code, 200)

        # 提交代码评估
        resp = self.client.post(
            '/api/ability-matrix/submit',
            data=json.dumps({'code': 'x = 1 + 1'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

        # 查看收藏
        resp = self.client.get('/api/user/favorites')
        self.assertEqual(resp.status_code, 200)

        # 添加收藏
        resp = self.client.post(
            '/api/user/favorites',
            data=json.dumps({
                "questionId": "q_journey",
                "action": "add",
                "title": "旅程题目"
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

        # 查看个人资料
        resp = self.client.get('/profile')
        self.assertEqual(resp.status_code, 200)

        # 登出
        resp = self.client.get('/logout')
        self.assertIn(resp.status_code, (200, 302))

        # 验证已登出
        resp = self.client.get('/auth/status')
        data = resp.get_json()
        self.assertFalse(data.get('isAuthenticated', True))

        # 受保护 API 返回 401
        resp = self.client.get('/api/ability-matrix')
        self.assertEqual(resp.status_code, 401)

        resp = self.client.get('/api/user/favorites')
        self.assertEqual(resp.status_code, 401)

    @patch('app.api.ability_matrix_routes.AbilityMatrixService')
    def test_error_recovery_flow(self, mock_am):
        """错误恢复流程: 错误提交 → 正确提交"""
        mock_am.init_user_matrix.return_value = None
        mock_am.get_user_matrix.return_value = (
            {'syntax_score': 50, 'level': '初级', 'dimensions': {}}, 200
        )
        mock_am.submit_code_evaluation.return_value = (
            {'scores': {'syntax_score': 90}}, 200
        )

        with self.client.session_transaction() as sess:
            sess['user_id'] = 'recovery_user'

        # 错误提交 (空代码)
        resp = self.client.post(
            '/api/ability-matrix/submit',
            data=json.dumps({'code': ''}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

        # 正确提交
        resp = self.client.post(
            '/api/ability-matrix/submit',
            data=json.dumps({'code': 'print("hello")'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main()
