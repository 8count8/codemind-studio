"""
Service 层封装了业务逻辑，调用 Model 层的方法。
提供更高层次的接口供控制器或路由层使用。
"""

from app.models.db import VALID_DIFFICULTIES
from app.models.favorites_models_db import FavoriteModel


class FavoriteService:
    @staticmethod
    def add_favorite(user_id, title, question, difficulty, tags):
        """
        添加收藏的业务逻辑。
        :param user_id: 用户 ID
        :param title: 收藏标题
        :param question: 题目内容（Markdown 格式）
        :param difficulty: 难度等级
        :param tags: 标签列表（JSON 格式）
        :return: 操作结果（成功或错误信息）
        """
        # 如果提供了 difficulty 参数，则验证其合法性
        if difficulty not in VALID_DIFFICULTIES:
            return {"error": f"Invalid difficulty. Valid values are: {VALID_DIFFICULTIES}"}, 400

        # 调用 Model 层方法添加收藏
        return FavoriteModel.add_favorite(user_id, title, question, difficulty, tags)

    @staticmethod
    def get_favorites_with_question(user_id):
        """
        获取收藏列表（包含题目具体内容）的业务逻辑。
        :param user_id: 用户 ID
        :return: 收藏列表（成功或错误信息）
        """
        return FavoriteModel.get_favorites_with_question(user_id)

    @staticmethod
    def get_favorites_without_question(user_id):
        """
        获取收藏列表（不包含题目具体内容）的业务逻辑。
        :param user_id: 用户 ID
        :return: 收藏列表（成功或错误信息）
        """
        return FavoriteModel.get_favorites_without_question(user_id)

    @staticmethod
    def search_favorites_by_title(user_id, title=None):
        """
        根据标题搜索收藏的业务逻辑。
        :param user_id: 用户 ID
        :param title: 搜索标题
        :return: 搜索结果（成功或错误信息）
        """
        return FavoriteModel.search_favorites_by_title(user_id, title)

    @staticmethod
    def delete_favorite(user_id, title):
        """
        删除指定用户的收藏题目的业务逻辑。
        :param user_id: 用户 ID
        :param title: 收藏标题
        :return: 操作结果（成功或错误信息）
        """
        return FavoriteModel.delete_favorite(user_id, title)