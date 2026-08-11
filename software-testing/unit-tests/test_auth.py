"""
单元测试: app/utils/auth.py 统一认证模块

覆盖:
- get_current_user_id: 当前用户 ID 获取
- is_authenticated: 登录状态判断
- get_authenticated_user_id: 认证用户获取 + 错误响应
- require_auth: 路由装饰器
- set_user_session / clear_session: 会话管理
"""
import unittest
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.utils.auth import (
    get_current_user_id,
    is_authenticated,
    get_authenticated_user_id,
    require_auth,
    set_user_session,
    clear_session,
)
from app.utils.constants import HTTPStatus


class TestGetCurrentUserId(unittest.TestCase):
    """get_current_user_id 获取当前用户 ID"""

    def test_no_session_returns_none(self):
        from flask import Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        with app.test_request_context():
            result = get_current_user_id()
            self.assertIsNone(result)

    def test_with_user_id_returns_value(self):
        from flask import Flask, session
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        with app.test_request_context():
            session['user_id'] = 'alice'
            result = get_current_user_id()
            self.assertEqual(result, 'alice')

    def test_empty_string_user_id(self):
        from flask import Flask, session
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        with app.test_request_context():
            session['user_id'] = ''
            result = get_current_user_id()
            self.assertEqual(result, '')


class TestIsAuthenticated(unittest.TestCase):
    """is_authenticated 登录状态判断"""

    def test_not_logged_in(self):
        from flask import Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        with app.test_request_context():
            result = is_authenticated()
            self.assertFalse(result)

    def test_logged_in(self):
        from flask import Flask, session
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        with app.test_request_context():
            session['user_id'] = 'bob'
            result = is_authenticated()
            self.assertTrue(result)


class TestGetAuthenticatedUserId(unittest.TestCase):
    """get_authenticated_user_id 认证用户获取 + 错误响应"""

    def test_not_logged_in_returns_error(self):
        from flask import Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        with app.test_request_context():
            user_id, err = get_authenticated_user_id()
            self.assertIsNone(user_id)
            self.assertIsNotNone(err)
            self.assertEqual(err[1], HTTPStatus.UNAUTHORIZED)

    def test_logged_in_returns_user_id(self):
        from flask import Flask, session
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        with app.test_request_context():
            session['user_id'] = 'charlie'
            user_id, err = get_authenticated_user_id()
            self.assertEqual(user_id, 'charlie')
            self.assertIsNone(err)


class TestRequireAuthDecorator(unittest.TestCase):
    """require_auth 路由装饰器"""

    def test_unauthenticated_returns_401(self):
        from flask import Flask, jsonify
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'

        @app.route('/test')
        @require_auth
        def test_view():
            return jsonify({"status": 200})

        with app.test_client() as client:
            resp = client.get('/test')
            self.assertEqual(resp.status_code, HTTPStatus.UNAUTHORIZED)
            data = resp.get_json()
            self.assertEqual(data['status'], HTTPStatus.UNAUTHORIZED)
            self.assertIn('message', data)

    def test_authenticated_passes_through(self):
        from flask import Flask, jsonify, session
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'

        @app.route('/test')
        @require_auth
        def test_view():
            return jsonify({"status": 200})

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'dave'
            resp = client.get('/test')
            self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_decorator_preserves_function_name(self):
        from flask import Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'

        @app.route('/test')
        @require_auth
        def my_special_view():
            pass

        self.assertEqual(my_special_view.__name__, 'my_special_view')


class TestSessionManagement(unittest.TestCase):
    """set_user_session / clear_session 会话管理"""

    def test_set_user_session(self):
        from flask import Flask, session
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        with app.test_request_context():
            set_user_session('eve')
            self.assertEqual(session['user_id'], 'eve')

    def test_clear_session(self):
        from flask import Flask, session
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        with app.test_request_context():
            session['user_id'] = 'frank'
            clear_session()
            self.assertNotIn('user_id', session)

    def test_clear_session_when_not_logged_in(self):
        from flask import Flask, session
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        with app.test_request_context():
            clear_session()
            self.assertNotIn('user_id', session)


class TestHttpStatusConstants(unittest.TestCase):
    """HTTPStatus 常量正确性"""

    def test_unauthorized_is_401(self):
        self.assertEqual(HTTPStatus.UNAUTHORIZED, 401)

    def test_ok_is_200(self):
        self.assertEqual(HTTPStatus.OK, 200)

    def test_bad_request_is_400(self):
        self.assertEqual(HTTPStatus.BAD_REQUEST, 400)

    def test_not_found_is_404(self):
        self.assertEqual(HTTPStatus.NOT_FOUND, 404)

    def test_internal_error_is_500(self):
        self.assertEqual(HTTPStatus.INTERNAL_ERROR, 500)


if __name__ == '__main__':
    unittest.main()