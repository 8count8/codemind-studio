"""
维度→题库标签映射 + 难度自适应（纯函数模块）

本模块实现文档 §10.2.1 维度→标签映射 和 §10.2.2 难度自适应 的设计：
1. 将能力矩阵 5 维度映射到 problems.tags 中的真实标签关键词
2. 根据用户当前维度的分数自适应推荐难度

设计原则：
1. 不导入任何 app.models / app.service 模块
2. 所有函数均为无副作用的纯函数
3. 便于单元测试和独立复用

对应文档：能力矩阵.md §10.2.1 / §10.2.2
"""

# 能力维度 → problems.tags 关键词映射
# 用于将薄弱维度诊断结果映射到真实题库查询
DIMENSION_TAG_MAP = {
    'syntax_score': [
        '基础语法', '变量', '数据类型', 'PEP8', '函数定义',
        '语法', '规范', '入门', '基础'
    ],
    'algorithm_score': [
        '排序', '查找', '动态规划', '递归', '贪心', '图论',
        '算法', '二分', '回溯', '分治', 'DP'
    ],
    'project_score': [
        '面向对象', '设计模式', '模块化', '类', '封装',
        '继承', '多态', '结构', '工程'
    ],
    'debug_score': [
        '异常处理', '调试', '错误处理', 'try', '日志',
        '断点', '排查', 'exception'
    ],
    'security_score': [
        '安全', 'SQL注入', 'XSS', '输入验证', '加密',
        '防护', '注入', '校验', 'hash'
    ]
}


def map_score_to_difficulty(score):
    """
    分数 → 推荐难度（难度自适应）

    规则（对应文档 §10.2.1）：
        score < 30  → '简单'（初学者，回退基础题）
        30 ≤ score < 60 → '中等'（最近发展区，维持中等难度）
        score ≥ 60  → '困难'（掌握度高，挑战难题）

    参数:
        score (int/float): 用户在某维度的当前得分
    返回:
        str: 难度等级（'简单' / '中等' / '困难'）
    """
    try:
        s = float(score or 0)
    except (TypeError, ValueError):
        s = 0.0

    if s < 30:
        return '简单'
    if s < 60:
        return '中等'
    return '困难'


def get_tags_for_dimension(dimension):
    """
    获取某维度对应的题库标签关键词列表

    参数:
        dimension (str): 能力维度字段名，如 'algorithm_score'
    返回:
        list[str]: 标签关键词列表，未知维度返回空列表
    """
    return DIMENSION_TAG_MAP.get(dimension, [])


def build_tag_regex(dimension):
    """
    构建某维度对应的 MySQL REGEXP 正则表达式

    用于 SQL: WHERE tags REGEXP %s
    例如: '排序|查找|动态规划|递归|...'

    参数:
        dimension (str): 能力维度字段名
    返回:
        str: 正则表达式字符串，未知维度返回空串
    """
    tags = get_tags_for_dimension(dimension)
    return '|'.join(tags) if tags else ''
