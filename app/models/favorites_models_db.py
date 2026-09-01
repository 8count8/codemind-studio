"""
Model 层封装了对数据库的操作，调用 favorites_topics 中的函数。
提供更清晰的接口供 Service 层使用。
"""

from app.models.db import VALID_DIFFICULTIES
from app.models.favorites_topics import (
    add_favorite as original_add_favorite,
    get_favorites_with_question as original_get_favorites_with_question,
    get_favorites_without_question as original_get_favorites_without_question,
    search_favorites_by_title as original_search_favorites_by_title,
    delete_favorite as original_delete_favorite,
)


class FavoriteModel:
    @staticmethod
    def add_favorite(user_id, title, question, difficulty, tags):
        """
        添加收藏到数据库。
        :param user_id: 用户 ID
        :param title: 收藏标题
        :param question: 题目内容（Markdown 格式）
        :param difficulty: 难度等级
        :param tags: 标签列表（JSON 格式）
        :return: 操作结果（成功或错误信息）
        """
        # 验证 difficulty 是否合法
        if difficulty not in VALID_DIFFICULTIES:
            return {"error": f"Invalid difficulty. Valid values are: {VALID_DIFFICULTIES}"}, 400

        return original_add_favorite(user_id, title, question, difficulty, tags)

    @staticmethod
    def get_favorites_with_question(user_id):
        """
        获取按时间排序的收藏列表（包含题目具体内容）。
        :param user_id: 用户 ID
        :return: 收藏列表（成功或错误信息）
        """
        return original_get_favorites_with_question(user_id)

    @staticmethod
    def get_favorites_without_question(user_id):
        """
        获取按时间排序的收藏列表（不包含题目具体内容）。
        :param user_id: 用户 ID
        :return: 收藏列表（成功或错误信息）
        """
        return original_get_favorites_without_question(user_id)

    @staticmethod
    def search_favorites_by_title(user_id, title=None):
        """
        根据标题进行高级搜索（支持模糊匹配）。
        :param user_id: 用户 ID
        :param title: 搜索标题
        :return: 搜索结果（成功或错误信息）
        """
        return original_search_favorites_by_title(user_id, title)

    @staticmethod
    def delete_favorite(user_id, question_id):
        """
        删除指定用户的收藏题目。
        :param user_id: 用户 ID
        :param title: 收藏标题
        :return: 操作结果（成功或错误信息）
        """
        return original_delete_favorite(question_id, user_id)
