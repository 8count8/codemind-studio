"""
题目列表Service 层封装了业务逻辑，调用 Model 层的方法。
提供更高层次的接口供控制器或路由层使用。
"""

from app.models.db import VALID_DIFFICULTIES
from app.models.question_model import QuestionModel


class QuestionService:

    @staticmethod
    def add_question(title, difficulty, tags, content=None, favorite=False):
        """
        添加题目的业务逻辑。
        :param title: 题目标题
        :param difficulty: 难度等级
        :param tags: 标签列表（JSON 格式）
        :param content: 题目内容（Markdown 格式，可选）
        :param favorite: 是否收藏（默认为 False）
        :return: 操作结果（成功或错误信息）
        """
        # 如果提供了 difficulty 参数，则验证其合法性
        if difficulty not in VALID_DIFFICULTIES:
            return {"error": f"Invalid difficulty. Valid values are: {VALID_DIFFICULTIES}"}, 400

        # 调用 Model 层方法添加题目
        return QuestionModel.add_question(title, difficulty, tags, content, favorite)

    @staticmethod
    def get_all_questions():
        """
        获取所有题目的业务逻辑。
        :return: 题目列表（成功或错误信息）
        """
        return QuestionModel.get_all_questions()

    @staticmethod
    def get_question_by_id(question_id):
        """
        根据 ID 获取题目详情的业务逻辑。
        :param question_id: 题目 ID
        :return: 题目详情（成功或错误信息）
        """
        return QuestionModel.get_question_by_id(question_id)

    @staticmethod
    def search_questions_by_title(title=None):
        """
        根据标题搜索题目的业务逻辑。
        :param title: 搜索标题
        :return: 搜索结果（成功或错误信息）
        """
        return QuestionModel.search_questions_by_title(title)
