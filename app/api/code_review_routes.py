""" code_review_routes.py
     代码审核页面路由
"""

from flask import render_template
from app.api.flasgger_compat import swag_from
from . import code_review_bp

@code_review_bp.route('/code-review', methods=['GET', 'POST'])
@swag_from({
    'tags': ['代码审核'],
    'description': '代码审核页面',
    'responses': {
        200: {'description': '成功返回代码审核页面'}
    }
})
def code_review():
    return render_template('code review.html')
