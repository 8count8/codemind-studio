import json
""" answer_routes.py
    答题系统路由
"""
from . import answer_bp
from flask import render_template, request, jsonify
from app.api.flasgger_compat import swag_from

from app.service import QuestionService


@answer_bp.route('/answerpad', methods=['GET', 'POST'])
@swag_from({
    'tags': ['答题系统'],
    'description': '答题板页面',
    'responses': {
        200: {'description': '成功返回答题板页面'}
    }
})
def answerpad():
    question_id = request.args.get('questionId')
    result = QuestionService.get_question_by_id(question_id)[0]
    if not result or 'question' not in result:
        return "题目不存在", 404

    # print(result)
    question_data = result['question']
    return render_template('answerpad.html', question=question_data)
