"""
Netlify Serverless Function for Flask App
使用自定义 WSGI 适配器将 Flask 应用适配到 Netlify Functions
"""
import os
import sys
import json
from urllib.parse import urlencode

# 添加项目根目录到路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')


def create_wsgi_environ(event):
    """将 Netlify/AWS Lambda 事件转换为 WSGI environ"""
    headers = event.get('headers', {}) or {}
    # 转为小写键
    headers_lower = {k.lower(): v for k, v in headers.items()}

    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    query_string = event.get('queryStringParameters', {}) or {}
    body = event.get('body', '') or ''

    # 如果有多个查询参数
    multi_value_query = event.get('multiValueQueryStringParameters') or None
    if multi_value_query:
        query_string_str = urlencode(
            [(k, v) if isinstance(v, str) else (k, v[0]) for k, v in query_string.items()]
        )
    else:
        query_string_str = urlencode(query_string) if query_string else ''

    # 处理 body
    if event.get('isBase64Encoded'):
        import base64
        body = base64.b64decode(body)

    content_length = len(body) if body else 0
    if isinstance(body, bytes):
        body_data = body
    else:
        body_data = body.encode('utf-8') if body else b''

    environ = {
        'REQUEST_METHOD': http_method,
        'SCRIPT_NAME': '',
        'PATH_INFO': path,
        'QUERY_STRING': query_string_str,
        'SERVER_NAME': headers_lower.get('host', 'localhost').split(':')[0],
        'SERVER_PORT': headers_lower.get('host', '443').split(':')[-1] if ':' in headers_lower.get('host', '443') else '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': __import__('io').BytesIO(body_data),
        'wsgi.errors': sys.stderr,
        'wsgi.multiprocess': False,
        'wsgi.multithread': False,
        'wsgi.run_once': False,
        'CONTENT_LENGTH': str(content_length),
        'CONTENT_TYPE': headers_lower.get('content-type', 'application/x-www-form-urlencoded'),
        'HTTP_HOST': headers_lower.get('host', 'localhost'),
        'HTTP_USER_AGENT': headers_lower.get('user-agent', ''),
        'HTTP_ACCEPT': headers_lower.get('accept', '*/*'),
    }

    # 添加其他 HTTP 头
    for key, value in headers_lower.items():
        if key not in ('host', 'content-type', 'user-agent', 'accept', 'content-length'):
            wsgi_key = 'HTTP_' + key.upper().replace('-', '_')
            environ[wsgi_key] = value

    return environ


def handler(event, context):
    """Netlify Serverless Function 入口"""
    try:
        # 延迟导入 Flask 应用（冷启动优化）
        if not hasattr(handler, 'flask_app'):
            import config
            from app import create_app

            app_config = config.ProductionConfig
            flask_app = create_app(config=app_config)

            # 初始化数据库
            try:
                from app.models.db import init_database
                init_database()
            except Exception as e:
                print(f"数据库初始化警告: {e}")

            handler.flask_app = flask_app

        flask_app = handler.flask_app

        # 创建 WSGI environ
        environ = create_wsgi_environ(event)

        # 调用 Flask 应用
        from io import BytesIO

        response_started = []
        response_headers = []
        response_status = []

        def start_response(status, headers, exc_info=None):
            response_status.append(status)
            response_headers.extend(headers)
            response_started.append(True)

        # 获取响应
        result = flask_app(environ, start_response)

        # 处理响应
        body = b''
        for chunk in result:
            if chunk:
                if isinstance(chunk, str):
                    body += chunk.encode('utf-8')
                else:
                    body += chunk

        # 解析状态码
        status_code = 200
        if response_status:
            status_str = response_status[0]
            status_code = int(status_str.split(' ')[0])

        # 转换响应头
        headers_dict = {}
        for key, value in response_headers:
            if key.lower() not in ('set-cookie',):
                headers_dict[key] = value

        # 返回 Lambda 响应
        import base64
        is_base64 = False
        if body and not all(32 <= b < 127 or b in (9, 10, 13) for b in body):
            is_base64 = True
            body_str = base64.b64encode(body).decode('utf-8')
        else:
            body_str = body.decode('utf-8') if body else ''

        return {
            'statusCode': status_code,
            'headers': headers_dict,
            'body': body_str,
            'isBase64Encoded': is_base64
        }

    except Exception as e:
        import traceback
        print(f"Error processing request: {e}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal Server Error', 'message': str(e)})
        }