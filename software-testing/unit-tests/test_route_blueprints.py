"""
路由集成测试: 验证统一认证改造后的所有路由行为

覆盖:
- app_auth.py: 登录/登出/状态检查
- ability_matrix_routes.py: 能力矩阵路由
- profile_routes.py: 个人资料路由
- user_api.py: 用户 API 路由
- main_routes.py: 主页路由
- @require_auth 装饰器在所有路由上的行为
"""
import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


class TestAppAuthRoutes(unittest.TestCase):
    """app_auth.py 路由测试"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import auth_bp
        self.app.register_blueprint(auth_bp)
        self.client = self.app.test_client()

    def test_get_login_page(self):
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)

    def test_get_register_page(self):
        resp = self.client.get('/register')
        self.assertEqual(resp.status_code, 200)

    def test_check_auth_status_not_logged_in(self):
        resp = self.client.get('/auth/status')
        data = resp.get_json()
        self.assertFalse(data.get('isAuthenticated', True))

    def test_check_auth_status_when_logged_in(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        resp = self.client.get('/auth/status')
        data = resp.get_json()
        self.assertTrue(data.get('isAuthenticated'))

    def test_logout_when_not_logged_in(self):
        resp = self.client.get('/logout')
        self.assertIn(resp.status_code, (200, 302))

    def test_reset_password_page(self):
        resp = self.client.get('/reset')
        self.assertEqual(resp.status_code, 200)


class TestMainRoutes(unittest.TestCase):
    """main_routes.py 路由测试"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import main_bp
        self.app.register_blueprint(main_bp)
        self.client = self.app.test_client()

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 200)

    def test_home_alias(self):
        resp = self.client.get('/home')
        self.assertEqual(resp.status_code, 200)

    def test_dashboard_page(self):
        resp = self.client.get('/dashboard')
        self.assertEqual(resp.status_code, 200)

    def test_csrf_token(self):
        resp = self.client.get('/api/csrf-token')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('csrf_token', data)


class TestAbilityMatrixRoutes(unittest.TestCase):
    """ability_matrix_routes.py 路由测试"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import ability_matrix_bp
        self.app.register_blueprint(ability_matrix_bp)
        self.client = self.app.test_client()

    def test_page_requires_auth(self):
        """能力矩阵页面现在也需要认证"""
        resp = self.client.get('/ability-matrix')
        self.assertEqual(resp.status_code, 401)

    def test_page_authenticated(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        resp = self.client.get('/ability-matrix')
        self.assertEqual(resp.status_code, 200)

    def test_get_matrix_unauthenticated_returns_401(self):
        resp = self.client.get('/api/ability-matrix')
        self.assertEqual(resp.status_code, 401)

    @patch('app.api.ability_matrix_routes.AbilityMatrixService')
    def test_get_matrix_authenticated(self, mock_svc):
        mock_svc.init_user_matrix.return_value = None
        mock_svc.get_user_matrix.return_value = ({"scores": {}}, 200)
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        resp = self.client.get('/api/ability-matrix')
        self.assertEqual(resp.status_code, 200)

    def test_submit_unauthenticated_returns_401(self):
        resp = self.client.post(
            '/api/ability-matrix/submit',
            data=json.dumps({'code': 'x=1'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 401)

    @patch('app.api.ability_matrix_routes.AbilityMatrixService')
    def test_submit_authenticated(self, mock_svc):
        mock_svc.submit_code_evaluation.return_value = ({"scores": {}}, 200)
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        resp = self.client.post(
            '/api/ability-matrix/submit',
            data=json.dumps({'code': 'x=1'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

    def test_submit_empty_data_returns_400(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        resp = self.client.post(
            '/api/ability-matrix/submit',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

    def test_history_unauthenticated_returns_401(self):
        resp = self.client.get('/api/ability-matrix/history')
        self.assertEqual(resp.status_code, 401)

    def test_recommendations_unauthenticated_returns_401(self):
        resp = self.client.get('/api/ability-matrix/recommendations')
        self.assertEqual(resp.status_code, 401)


class TestProfileRoutes(unittest.TestCase):
    """profile_routes.py 路由测试"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import profile_bp
        self.app.register_blueprint(profile_bp)
        self.client = self.app.test_client()

    def test_profile_unauthenticated_returns_401(self):
        resp = self.client.get('/profile')
        self.assertEqual(resp.status_code, 401)

    @patch('app.api.profile_routes.get_user_profile')
    def test_profile_authenticated(self, mock_get):
        mock_get.return_value = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        resp = self.client.get('/profile')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 200)
        self.assertEqual(data['user']['username'], 'testuser')


class TestUserApiRoutes(unittest.TestCase):
    """user_api.py 路由测试"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import user_api_bp
        self.app.register_blueprint(user_api_bp)
        self.client = self.app.test_client()

    @patch('app.api.user_api.QuestionService')
    def test_get_questions(self, mock_qs):
        mock_qs.get_all_questions.return_value = {
            "questions": [{"id": 1, "title": "Test"}]
        }
        resp = self.client.get('/api/questions')
        self.assertEqual(resp.status_code, 200)

    @patch('app.api.user_api.QuestionService')
    def test_get_questions_error(self, mock_qs):
        mock_qs.get_all_questions.return_value = {"error": "DB error"}
        resp = self.client.get('/api/questions')
        self.assertEqual(resp.status_code, 500)

    def test_favorites_unauthenticated_returns_401(self):
        resp = self.client.get('/api/user/favorites')
        self.assertEqual(resp.status_code, 401)

    @patch('app.api.user_api.FavoriteService')
    def test_favorites_authenticated(self, mock_fs):
        mock_fs.get_favorites_without_question.return_value = {
            "favorites": [{"id": 1}]
        }
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        resp = self.client.get('/api/user/favorites')
        self.assertEqual(resp.status_code, 200)

    def test_post_favorites_unauthenticated_returns_401(self):
        resp = self.client.post(
            '/api/user/favorites',
            data=json.dumps({"questionId": "1", "action": "add", "title": "t"}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 401)

    def test_post_favorites_invalid_action_returns_400(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        resp = self.client.post(
            '/api/user/favorites',
            data=json.dumps({"questionId": "1", "action": "invalid", "title": "t"}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

    def test_history_unauthenticated_returns_401(self):
        resp = self.client.get('/api/user/history')
        self.assertEqual(resp.status_code, 401)

    def test_process_code_no_data_returns_400(self):
        """空表单数据 - 无代码文件也无粘贴代码"""
        resp = self.client.post('/process_code', data={'paste_code': ''})
        self.assertEqual(resp.status_code, 400)

    def test_process_algorithm_code_empty(self):
        resp = self.client.post(
            '/api/process_algorithm_code',
            data=json.dumps({"code": "", "language": "python", "question_id": "1"}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)

    @patch('app.api.user_api.get_algorithm_review_result')
    def test_ai_review_status(self, mock_get):
        mock_get.return_value = {"status": "processing", "task_id": "test-123"}
        resp = self.client.get('/api/ai_review_status/test-123')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'processing')


class TestOtherPageRoutes(unittest.TestCase):
    """其他页面路由测试"""

    def test_answer_page(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import answer_bp
        self.app.register_blueprint(answer_bp)
        client = self.app.test_client()
        resp = client.get('/answerpad')
        self.assertEqual(resp.status_code, 200)

    def test_code_review_page(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import code_review_bp
        self.app.register_blueprint(code_review_bp)
        client = self.app.test_client()
        resp = client.get('/code-review')
        self.assertEqual(resp.status_code, 200)

    def test_quizbank_page(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import quizbank_bp
        self.app.register_blueprint(quizbank_bp)
        client = self.app.test_client()
        resp = client.get('/quizbank')
        self.assertEqual(resp.status_code, 200)

    def test_favorites_page(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import favorites_history_bp
        self.app.register_blueprint(favorites_history_bp)
        client = self.app.test_client()
        resp = client.get('/favorites')
        self.assertEqual(resp.status_code, 200)

    def test_history_page(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import favorites_history_bp
        self.app.register_blueprint(favorites_history_bp)
        client = self.app.test_client()
        resp = client.get('/history')
        self.assertEqual(resp.status_code, 200)

    def test_ai_question_page(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import ai_question_bp
        self.app.register_blueprint(ai_question_bp)
        client = self.app.test_client()
        resp = client.get('/ai-question')
        self.assertEqual(resp.status_code, 200)


class TestErrorPaths(unittest.TestCase):
    """错误路径集成测试"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

    def test_require_auth_returns_401_with_correct_format(self):
        from app.utils.auth import require_auth
        from flask import jsonify

        @self.app.route('/protected')
        @require_auth
        def protected():
            return jsonify({"data": "secret"})

        client = self.app.test_client()
        resp = client.get('/protected')
        self.assertEqual(resp.status_code, 401)
        data = resp.get_json()
        self.assertEqual(data['status'], 401)
        self.assertIn('message', data)

    def test_401_response_body(self):
        from app.utils.auth import require_auth
        from flask import jsonify

        @self.app.route('/api/data')
        @require_auth
        def api_data():
            return jsonify({"data": "test"})

        client = self.app.test_client()
        resp = client.get('/api/data')
        data = resp.get_json()
        self.assertIn('请先登录', data['message'])

    def test_unauthenticated_post_favorites(self):
        from app.api import user_api_bp
        self.app.register_blueprint(user_api_bp)
        client = self.app.test_client()
        resp = client.post(
            '/api/user/favorites',
            data=json.dumps({"questionId": "1", "action": "add"}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 401)

    def test_unauthenticated_get_history(self):
        from app.api import user_api_bp
        self.app.register_blueprint(user_api_bp)
        client = self.app.test_client()
        resp = client.get('/api/user/history')
        self.assertEqual(resp.status_code, 401)

    def test_invalid_json_body(self):
        from app.api import user_api_bp
        self.app.register_blueprint(user_api_bp)
        client = self.app.test_client()
        with client.session_transaction() as sess:
            sess['user_id'] = 'testuser'
        resp = client.post(
            '/api/user/favorites',
            data='not valid json',
            content_type='application/json'
        )
        self.assertIn(resp.status_code, (400, 500))


class TestAuthFlowIntegration(unittest.TestCase):
    """认证流程集成测试（模拟登录→访问→登出）"""

    def setUp(self):
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        from app.api import auth_bp, main_bp, ability_matrix_bp, user_api_bp
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(ability_matrix_bp)
        self.app.register_blueprint(user_api_bp)
        self.client = self.app.test_client()

    @patch('app.api.ability_matrix_routes.AbilityMatrixService')
    @patch('app.api.user_api.FavoriteService')
    def test_full_auth_flow(self, mock_fs, mock_am):
        # 1. 初始状态：未登录
        resp = self.client.get('/auth/status')
        data = resp.get_json()
        self.assertFalse(data.get('isAuthenticated', True))

        # 2. 设置 session 模拟登录
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'integration_test_user'

        # 3. 验证状态为已登录
        resp = self.client.get('/auth/status')
        data = resp.get_json()
        self.assertTrue(data.get('isAuthenticated'))

        # 4. 访问受保护的能力矩阵 API
        mock_am.init_user_matrix.return_value = None
        mock_am.get_user_matrix.return_value = ({"scores": {}}, 200)

        resp = self.client.get('/api/ability-matrix')
        self.assertEqual(resp.status_code, 200)

        # 5. 访问用户收藏
        mock_fs.get_favorites_without_question.return_value = {"favorites": []}

        resp = self.client.get('/api/user/favorites')
        self.assertEqual(resp.status_code, 200)

        # 6. 登出
        resp = self.client.get('/logout')
        self.assertIn(resp.status_code, (200, 302))

        # 7. 登出后状态：未登录
        resp = self.client.get('/auth/status')
        data = resp.get_json()
        self.assertFalse(data.get('isAuthenticated', True))

        # 8. 受保护 API 返回 401
        resp = self.client.get('/api/ability-matrix')
        self.assertEqual(resp.status_code, 401)

    @patch('app.api.user_api.FavoriteService')
    def test_post_favorites_flow(self, mock_fs):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'flow_test_user'

        mock_fs.add_favorite.return_value = {"status": 200}

        resp = self.client.post(
            '/api/user/favorites',
            data=json.dumps({
                "questionId": "q1",
                "action": "add",
                "title": "Two Sum",
                "content": "两数之和",
                "difficulty": "简单",
                "tags": ["数组"]
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

    @patch('app.api.user_api.FavoriteService')
    def test_remove_favorites_flow(self, mock_fs):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'flow_test_user'

        mock_fs.delete_favorite.return_value = {"status": 200}

        resp = self.client.post(
            '/api/user/favorites',
            data=json.dumps({
                "questionId": "1",
                "action": "remove",
                "title": "test"
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main()