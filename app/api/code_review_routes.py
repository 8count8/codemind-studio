""" code_review_routes.py
     代码审核页面路由（页面由 Vue Router 渲染）
"""

from flask import jsonify
from . import code_review_bp

@code_review_bp.route('/code-review', methods=['GET', 'POST'])
def code_review():
    return jsonify({"status": 200})
