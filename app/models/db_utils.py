"""
数据库工具模块 — 游标转换与时间戳

负责:
- fetch_dict(): 将游标结果转为字典列表
- fetch_one_dict(): 获取单条结果为字典
- get_current_timestamp(): 获取格式化时间戳
"""

from datetime import datetime


def fetch_dict(cursor):
    """将查询结果转换为字典列表"""
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_one_dict(cursor):
    """获取单条查询结果为字典"""
    row = cursor.fetchone()
    if row:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    return None


def get_current_timestamp():
    """获取当前时间戳字符串"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
