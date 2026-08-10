""" favorites_history_routes.py
    收藏夹和历史记录页面路由
"""
from flask import render_template
from app.api.flasgger_compat import swag_from
from . import favorites_history_bp

@favorites_history_bp.route('/favorites', methods=['GET', 'POST'])
@swag_from({
    'tags': ['收藏夹'],
    'description': '收藏夹页面',
    'responses': {
        200: {'description': '成功返回收藏夹页面'}
    }
})
def favorites():
    return render_template('favorites.html')

@favorites_history_bp.route('/history', methods=['GET', 'POST'])
@swag_from({
    'tags': ['历史记录'],
    'description': '历史记录页面',
    'responses': {
        200: {'description': '成功返回历史记录页面'}
    }
})
def history():
    return render_template('history.html')