"""
能力矩阵纯计算模块 — 无 DB 依赖

本模块包含能力矩阵的所有纯函数计算逻辑：
- 维度常量定义
- 等级计算
- 薄弱维度诊断
- 学习建议生成
- 推荐任务列表

设计原则：
1. 不导入任何 app.models / app.service 模块
2. 所有函数均为无副作用的纯函数
3. 便于单元测试和独立复用
"""

ABILITY_DIMENSIONS = [
    'syntax_score', 'algorithm_score', 'project_score',
    'debug_score', 'security_score'
]

DIMENSION_LABELS = {
    'syntax_score': '语法基础',
    'algorithm_score': '算法思维',
    'project_score': '项目实践',
    'debug_score': '调试能力',
    'security_score': '安全意识'
}

LEVEL_THRESHOLDS = {
    '专家': 90,
    '高级': 75,
    '中级': 50,
    '初级': 25,
}


def calculate_level(scores):
    """根据各项能力得分计算综合等级（纯函数，无副作用）"""
    if not scores:
        return '初学者'

    total = sum(scores.get(dim, 0) for dim in ABILITY_DIMENSIONS)
    avg = total / len(ABILITY_DIMENSIONS)

    if avg >= 90:
        return '专家'
    elif avg >= 75:
        return '高级'
    elif avg >= 50:
        return '中级'
    elif avg >= 25:
        return '初级'
    else:
        return '初学者'


def get_dimension_suggestion(dimension):
    """根据薄弱维度返回学习建议（纯函数）"""
    suggestions = {
        'syntax_score': '建议加强代码规范训练，多练习基础语法，关注代码可读性和PEP8规范。',
        'algorithm_score': '建议练习经典算法题，从排序、搜索等基础算法入手，逐步挑战动态规划和图论问题。',
        'project_score': '建议尝试完整的小项目开发，注重代码模块化设计和功能完整性。',
        'debug_score': '建议学习调试工具的使用，练习阅读错误日志，培养系统性排查问题的思维。',
        'security_score': '建议学习Web安全基础知识，了解常见漏洞的防御方法。'
    }
    return suggestions.get(dimension, '继续努力！')


def get_recommended_tasks(dimension):
    """根据薄弱维度返回推荐的练习任务（纯函数）"""
    tasks = {
        'syntax_score': [
            {"title": "Python 基础语法练习", "type": "quiz", "difficulty": "简单"},
            {"title": "代码规范改进挑战", "type": "practice", "difficulty": "中等"},
            {"title": "PEP8 规范应用", "type": "reading", "difficulty": "简单"}
        ],
        'algorithm_score': [
            {"title": "排序算法实现", "type": "practice", "difficulty": "中等"},
            {"title": "二分查找专题", "type": "quiz", "difficulty": "中等"},
            {"title": "动态规划入门", "type": "practice", "difficulty": "困难"}
        ],
        'project_score': [
            {"title": "迷你项目：计算器", "type": "project", "difficulty": "简单"},
            {"title": "模块化代码重构", "type": "practice", "difficulty": "中等"},
            {"title": "设计模式实践", "type": "project", "difficulty": "困难"}
        ],
        'debug_score': [
            {"title": "Bug 排查练习", "type": "practice", "difficulty": "中等"},
            {"title": "异常处理综合应用", "type": "quiz", "difficulty": "中等"},
            {"title": "调试工具使用指南", "type": "reading", "difficulty": "简单"}
        ],
        'security_score': [
            {"title": "SQL注入防御实战", "type": "practice", "difficulty": "中等"},
            {"title": "XSS攻击与防御", "type": "quiz", "difficulty": "中等"},
            {"title": "Web安全基础", "type": "reading", "difficulty": "简单"}
        ]
    }
    return tasks.get(dimension, [])


def diagnose_weak_dimensions(scores_by_dimension):
    """
    诊断薄弱维度（纯函数，从 get_weak_dimensions 提取的核心算法）

    :param scores_by_dimension: dict, 如 {'syntax_score': 80, 'algorithm_score': 45, ...}
    :return: list of weak dimension dicts sorted by score ascending
    """
    if not scores_by_dimension:
        return []

    scores = [scores_by_dimension.get(dim, 0) for dim in ABILITY_DIMENSIONS]
    avg_score = sum(scores) / len(scores) if scores else 0

    weak_dimensions = []
    for dim in ABILITY_DIMENSIONS:
        score = scores_by_dimension.get(dim, 0)
        if score < avg_score and score < 60:
            weak_dimensions.append({
                'dimension': dim,
                'label': DIMENSION_LABELS.get(dim, dim),
                'score': score,
                'suggestion': get_dimension_suggestion(dim)
            })

    weak_dimensions.sort(key=lambda x: x['score'])
    return weak_dimensions


def build_dimensions_dict(scores_by_dimension):
    """
    构建前端需要的 dimensions 字典结构（纯函数）

    :param scores_by_dimension: dict, 原始分数
    :return: dict, 如 {'syntax_score': {'label': '语法基础', 'score': 80}, ...}
    """
    return {
        key: {
            'label': DIMENSION_LABELS.get(key, key),
            'score': round(scores_by_dimension.get(key, 0) or 0, 2)
        }
        for key in ABILITY_DIMENSIONS
    }