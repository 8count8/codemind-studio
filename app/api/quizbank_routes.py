""" 试题库相关路由 """
from flask import jsonify
from . import quizbank_bp


@quizbank_bp.route('/quizbank', methods=['GET', 'POST'])
def quizbank():
    """试题库页面（页面由 Vue Router 渲染）"""
    return jsonify({"status": 200})
