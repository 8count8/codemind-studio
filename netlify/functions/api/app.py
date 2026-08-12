"""
Netlify Serverless Function for CodeMind Studio (Flask + Supabase PostgreSQL)

架构: 前端(Vue) + 后端(Flask) 一体化部署到 Netlify
数据库: Supabase PostgreSQL (通过 DATABASE_URL 环境变量连接)

路由重定向:
  netlify.toml 将 /api/*, /login, /register 等路径 rewrite 到 /api/app
  本函数通过 rawPath 获取原始请求路径，正确转发给 Flask 路由

Set-Cookie: 使用 multiValueHeaders 确保多个 Cookie (session + csrf) 正确下发
"""
import os
import sys
import json
import base64
from urllib.parse import urlencode
from io import BytesIO

# 添加项目根目录到路径，使 Function 能导入 app.* 模块
# 当前文件: netlify/functions/api/app.py
# 需要向上 3 级到达项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.environ.setdefault('FLASK_ENV', 'production')


def create_wsgi_environ(event):
    """将 Netlify/AWS Lambda 事件转换为 WSGI environ
    
    关键: 使用 rawPath (而非 path) 获取原始请求路径
    因为 netlify.toml 的 rewrite 会将 /login 等路径内部转发到 /api/app
    rawPath 保留了用户浏览器请求的原始路径
    """
    headers = event.get('headers', {}) or {}
    headers_lower = {k.lower(): v for k, v in headers.items()}

    http_method = event.get('httpMethod', 'GET')
    
    # 获取原始请求路径 (rawPath 优先于 path)
    path = event.get('rawPath') or event.get('path', '/')
    
    # 去除可能的 /api 前缀 (如果 rewrite 添加了)
    # 当 rawPath 不可用时，event.path 可能是 /api/app，需要从其他信息推断
    if path.startswith('/api/') and path != '/api/app':
        # 这是 API 重定向过来的，尝试从 header 或 event 中获取原始路径
        # Netlify 在 rewrite 时会保留 rawPath
        path = event.get('rawPath', path)
    
    query_string = event.get('queryStringParameters', {}) or {}
    
    multi_value_query = event.get('multiValueQueryStringParameters') or None
    if multi_value_query:
        query_string_str = urlencode(
            [(k, v) if isinstance(v, str) else (k, v[0]) for k, v in query_string.items()]
        )
    else:
        query_string_str = urlencode(query_string) if query_string else ''

    body = event.get('body', '') or ''
    if event.get('isBase64Encoded'):
        body = base64.b64decode(body)

    content_length = len(body) if body else 0
    body_data = body if isinstance(body, bytes) else (body.encode('utf-8') if body else b'')

    host = headers_lower.get('host', 'localhost')
    if ':' in host:
        server_name, server_port = host.rsplit(':', 1)
    else:
        server_name, server_port = host, '443'

    environ = {
        'REQUEST_METHOD': http_method,
        'SCRIPT_NAME': '',
        'PATH_INFO': path,
        'QUERY_STRING': query_string_str,
        'SERVER_NAME': server_name,
        'SERVER_PORT': server_port,
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': BytesIO(body_data),
        'wsgi.errors': sys.stderr,
        'wsgi.multiprocess': False,
        'wsgi.multithread': False,
        'wsgi.run_once': False,
        'CONTENT_LENGTH': str(content_length),
        'CONTENT_TYPE': headers_lower.get('content-type', 'application/x-www-form-urlencoded'),
        'HTTP_HOST': host,
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
        # 延迟初始化 Flask 应用（冷启动优化）
        if not hasattr(handler, 'flask_app'):
            import config
            from app import create_app

            app_config = config.ProductionConfig
            flask_app = create_app(config=app_config)

            # 初始化数据库（幂等操作，安全可重复执行）
            try:
                from app.models.db import init_database
                init_database()
            except Exception as e:
                print(f"[WARN] 数据库初始化跳过: {e}")

            handler.flask_app = flask_app

        flask_app = handler.flask_app

        # 创建 WSGI environ
        environ = create_wsgi_environ(event)

        # WSGI 协议: 调用 Flask 应用
        response_started = []
        response_headers = []
        response_status = []

        def start_response(status, headers, exc_info=None):
            response_status.append(status)
            response_headers.extend(headers)
            response_started.append(True)

        result = flask_app(environ, start_response)

        # 读取响应体
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

        # 构建响应头 (Set-Cookie 需要 multiValueHeaders)
        headers_dict = {}
        multi_value_headers = {}

        for key, value in response_headers:
            key_lower = key.lower()
            if key_lower == 'set-cookie':
                if key not in multi_value_headers:
                    multi_value_headers[key] = []
                multi_value_headers[key].append(value)
                headers_dict[key] = value
            else:
                headers_dict[key] = value

        # 编码响应体
        is_base64 = False
        if body:
            try:
                body_str = body.decode('utf-8')
            except UnicodeDecodeError:
                is_base64 = True
                body_str = base64.b64encode(body).decode('utf-8')
        else:
            body_str = ''

        response = {
            'statusCode': status_code,
            'headers': headers_dict,
            'body': body_str,
            'isBase64Encoded': is_base64
        }

        # multiValueHeaders 确保所有 Set-Cookie 都能下发 (session + csrf)
        if multi_value_headers:
            response['multiValueHeaders'] = multi_value_headers

        return response

    except Exception as e:
        import traceback
        print(f"[ERROR] Function 执行失败: {e}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal Server Error', 'message': str(e)})
        }
