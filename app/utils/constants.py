"""
项目常量定义

集中管理 HTTP 状态码、业务阈值等魔法值，
避免在代码中散落硬编码数字。
"""


class HTTPStatus:
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


class LevelThresholds:
    EXPERT = 90
    ADVANCED = 75
    INTERMEDIATE = 50
    BEGINNER = 25


LEVEL_LABELS = {
    '专家': '专家',
    '高级': '高级',
    '中级': '中级',
    '初级': '初级',
    '初学者': '初学者',
}
