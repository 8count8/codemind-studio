"""
api 模块

该模块用于组织和管理与 API 相关的路由和视图函数，包含以下子模块：
1. __init__.py: 定义蓝图 (auth_bp 和 main_bp)。
2. app_auth.py: 处理用户认证相关功能（登录、注销、注册）。
3. main_routes.py: 处理主页面相关功能（首页、仪表盘）。
"""

from flask import Blueprint

""" 蓝图 """
auth_bp = Blueprint('auth', __name__)  # 创建用户认证蓝图
main_bp = Blueprint('main', __name__)  # 创建主页面蓝图
answer_bp = Blueprint('answer', __name__)  # 答题系统
code_review_bp = Blueprint('code_review', __name__)  # 代码审核
quizbank_bp = Blueprint('quizbank', __name__)  # 试题库
favorites_history_bp = Blueprint('favorites_history', __name__)  # 收藏夹

user_api_bp = Blueprint('user_api', __name__)
ai_question_bp = Blueprint('ai_question', __name__)
profile_bp = Blueprint('profile', __name__)
ability_matrix_bp = Blueprint('ability_matrix', __name__)  # 能力矩阵
ollama_bp = Blueprint('ollama', __name__)  # Ollama 运行状态 + 拉模型
admin_bp = Blueprint('admin', __name__)    # 管理员后台：用户/题目/操作记录

# 导入路由和视图函数
from . import (
    main_routes,
    app_auth,
    answer_routes,
    code_review_routes,
    quizbank_routes,
    favorites_history_routes,
    user_api,
    ai_question_routes,
    profile_routes,
    ability_matrix_routes,
    ollama_routes,
    admin_routes,
)
