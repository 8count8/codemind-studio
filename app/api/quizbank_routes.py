""" 试题库相关路由 4"""
from flask import render_template
from app.api.flasgger_compat import swag_from
from . import quizbank_bp


@quizbank_bp.route('/quizbank', methods=['GET', 'POST'])
@swag_from({
    'summary': '试题库页面',
    'tags': ['试题库'],
    'description': '试题库页面',
    'responses': {
        200: {'description': '成功返回试题库页面'}
    }
})
def quizbank():
    return render_template('quizbank.html')
