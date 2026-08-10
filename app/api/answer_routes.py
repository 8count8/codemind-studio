import json
""" answer_routes.py
    答题系统路由（页面由 Vue Router 渲染）
"""
from . import answer_bp
from flask import request, jsonify


@answer_bp.route('/answerpad', methods=['GET', 'POST'])
def answerpad():
    """答题板页面（页面由 Vue Router 渲染）"""
    return jsonify({"status": 200})
