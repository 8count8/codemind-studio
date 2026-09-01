""" code_review_routes.py
     代码审核页面路由（页面由 Vue Router 渲染）

     注意：代码审核的 API 端点实际定义在 app/api/user_api.py 中：
     - POST /api/code-review/review    代码审查
     - GET  /api/code-review/history   审查历史
     - GET  /api/code-review/{id}      审查详情

     本文件仅提供 /code-review 页面占位路由，前端通过 Vue Router 渲染页面，
     实际 API 调用走 user_api_bp 注册的端点。
"""

from flask import jsonify
from . import code_review_bp

@code_review_bp.route('/code-review', methods=['GET', 'POST'])
def code_review():
    return jsonify({"status": 200})
