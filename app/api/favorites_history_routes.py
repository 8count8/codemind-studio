""" favorites_history_routes.py
    收藏夹和历史记录页面路由（页面由 Vue Router 渲染）
"""
from flask import jsonify
from . import favorites_history_bp

@favorites_history_bp.route('/favorites', methods=['GET', 'POST'])
def favorites():
    return jsonify({"status": 200})

@favorites_history_bp.route('/history', methods=['GET', 'POST'])
def history():
    return jsonify({"status": 200})