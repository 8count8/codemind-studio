"""
题目列表Model层封装了对数据库的操作，调用底层函数。
提供更清晰的接口供 Service 层使用。
"""

from .question_db import (
    get_all_questions as original_get_all_questions,
    get_question_by_id as original_get_question_by_id,
    search_questions_by_title as original_search_questions_by_title,
    update_question as original_update_question,
    insert_question as original_insert_question,
)
from app.models.db import dict_to_markdown, VALID_DIFFICULTIES


class QuestionModel:
    @staticmethod
    def add_question(title, difficulty, tags, content=None, favorite=False):
        """Insert a question; ``favorite`` is retained for API compatibility."""
        del favorite
        return original_insert_question(title, content or "", difficulty, tags)

    @staticmethod
    def get_all_questions():
        """
       获取所有题目的列表。
       :return: 题目列表（成功或错误信息）
       """
        result = original_get_all_questions()
        if isinstance(result, tuple):  # 如果 result 是元组
            result = result[0]  # 假设第一个元素是字典
        if "error" in result:
            return result

        # 转换 content 字段为 Markdown 格式
        for question in result.get("questions", []):
            if "content" in question and isinstance(question["content"], dict):
                question["content"] = dict_to_markdown(question["content"])

        return result

    @staticmethod
    def get_question_by_id(question_id):
        """
        根据 ID 获取题目详情。
        :param question_id: 题目 ID
        :return: 题目详情（成功或错误信息）
        """
        result = original_get_question_by_id(question_id)
        if isinstance(result, tuple):
            result = result[0]
        if "error" in result:
            return result

        # 转换 content 字段为 Markdown 格式
        if "content" in result and isinstance(result["content"], dict):
            result["content"] = dict_to_markdown(result["content"])

        return result

    @staticmethod
    def search_questions_by_title(title=None):
        """
        根据标题搜索题目（支持模糊匹配）。
        :param title: 搜索标题
        :return: 搜索结果（成功或错误信息）
        """
        result = original_search_questions_by_title(title)
        if isinstance(result, tuple):
            result = result[0]
        if "error" in result:
            return result

        # 转换 content 字段为 Markdown 格式
        for question in result.get("questions", []):
            if "content" in question and isinstance(question["content"], dict):
                question["content"] = dict_to_markdown(question["content"])

        return result

    @staticmethod
    def update_question(question_id, title=None, difficulty=None, tags=None, content=None):
        """
        更新指定题目的信息。
        :param question_id: 题目 ID
        :param title: 新的标题（可选）
        :param difficulty: 新的难度（可选）
        :param tags: 新的标签列表（可选）
        :param content: 新的题目内容（Markdown 格式，可选）
        :return: 操作结果（成功或错误信息）
        """
        # 如果提供了 difficulty 参数，则验证其合法性
        if difficulty and difficulty not in VALID_DIFFICULTIES:
            return {"error": f"Invalid difficulty. Valid values are: {VALID_DIFFICULTIES}"}, 400

        # 调用底层函数更新题目信息AlgorithmProblemGenerator
        return original_update_question(question_id, title, difficulty, tags, content)
