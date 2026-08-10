"""能力矩阵数据模型层 - SQLite 版本"""

import json
import logging
from datetime import datetime

from app.models.sqlite_db import get_db_connection

logging.basicConfig(level=logging.INFO)

ABILITY_DIMENSIONS = ['syntax_score', 'algorithm_score', 'project_score', 'debug_score', 'security_score']

DIMENSION_LABELS = {
    'syntax_score': '语法基础',
    'algorithm_score': '算法思维',
    'project_score': '项目实践',
    'debug_score': '调试能力',
    'security_score': '安全意识'
}


def create_mysql_connection():
    """兼容旧接口"""
    return get_db_connection()


def init_ability_matrix(user_id):
    """为用户初始化能力矩阵记录"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO ability_matrix (user_id)
            VALUES (?)
        """, (user_id,))
        connection.commit()

        if cursor.rowcount > 0:
            logging.info(f"为用户 {user_id} 初始化能力矩阵成功")
        connection.close()
        return {"message": "初始化成功"}, 200
    except Exception as e:
        logging.error(f"初始化能力矩阵失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500


def get_ability_matrix(user_id):
    """获取指定用户的能力矩阵数据"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT user_id, syntax_score, algorithm_score, project_score,
                   debug_score, security_score, updated_at
            FROM ability_matrix
            WHERE user_id = ?
        """, (user_id,))
        result = cursor.fetchone()

        if result:
            result_dict = dict(result)
            result_dict['dimensions'] = {
                key: {
                    'label': DIMENSION_LABELS[key],
                    'score': round(result_dict.get(key, 0) or 0, 2)
                }
                for key in ABILITY_DIMENSIONS
            }
            return {"matrix": result_dict}, 200
        else:
            default_matrix = {
                'user_id': user_id,
                'syntax_score': 0,
                'algorithm_score': 0,
                'project_score': 0,
                'debug_score': 0,
                'security_score': 0,
                'dimensions': {
                    key: {'label': DIMENSION_LABELS[key], 'score': 0}
                    for key in ABILITY_DIMENSIONS
                }
            }
            return {"matrix": default_matrix}, 200
    except Exception as e:
        logging.error(f"获取能力矩阵失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        connection.close()


def update_ability_matrix(user_id, scores):
    """更新用户的能力矩阵"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT syntax_score, algorithm_score, project_score,
                   debug_score, security_score
            FROM ability_matrix
            WHERE user_id = ?
        """, (user_id,))
        current = cursor.fetchone()

        if current is None:
            level = calculate_level(scores)
            cursor.execute("""
                INSERT INTO ability_matrix
                (user_id, syntax_score, algorithm_score, project_score,
                 debug_score, security_score, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
            """, (
                user_id,
                scores.get('syntax_score', 0),
                scores.get('algorithm_score', 0),
                scores.get('project_score', 0),
                scores.get('debug_score', 0),
                scores.get('security_score', 0)
            ))
        else:
            current_dict = dict(current)
            new_scores = {}
            for dim in ABILITY_DIMENSIONS:
                old_score = current_dict.get(dim, 0) or 0
                new_score = scores.get(dim, 0)
                new_scores[dim] = round((old_score + new_score) / 2, 2)

            level = calculate_level(new_scores)
            cursor.execute("""
                UPDATE ability_matrix
                SET syntax_score = ?, algorithm_score = ?, project_score = ?,
                    debug_score = ?, security_score = ?, updated_at = datetime('now', 'localtime')
                WHERE user_id = ?
            """, (
                new_scores['syntax_score'],
                new_scores['algorithm_score'],
                new_scores['project_score'],
                new_scores['debug_score'],
                new_scores['security_score'],
                user_id
            ))

        connection.commit()
        connection.close()
        return get_ability_matrix(user_id)
    except Exception as e:
        logging.error(f"更新能力矩阵失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500


def calculate_level(scores):
    """根据各项能力得分计算综合等级"""
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


def get_weak_dimensions(user_id):
    """获取用户的薄弱维度"""
    result, status = get_ability_matrix(user_id)
    if status != 200 or 'matrix' not in result:
        return result, status

    matrix = result['matrix']
    dimensions_data = matrix.get('dimensions', {})

    scores = [d['score'] for d in dimensions_data.values()]
    avg_score = sum(scores) / len(scores) if scores else 0

    weak_dimensions = []
    for key, data in dimensions_data.items():
        if data['score'] < avg_score and data['score'] < 60:
            weak_dimensions.append({
                'dimension': key,
                'label': data['label'],
                'score': data['score'],
                'suggestion': get_dimension_suggestion(key)
            })

    weak_dimensions.sort(key=lambda x: x['score'])
    return {"weak_dimensions": weak_dimensions, "average_score": round(avg_score, 2)}, 200


def get_dimension_suggestion(dimension):
    """根据薄弱维度返回学习建议"""
    suggestions = {
        'syntax_score': '建议加强代码规范训练，多练习基础语法，关注代码可读性和PEP8规范。',
        'algorithm_score': '建议练习经典算法题，从排序、搜索等基础算法入手，逐步挑战动态规划和图论问题。',
        'project_score': '建议尝试完整的小项目开发，注重代码模块化设计和功能完整性。',
        'debug_score': '建议学习调试工具的使用，练习阅读错误日志，培养系统性排查问题的思维。',
        'security_score': '建议学习Web安全基础知识，了解常见漏洞的防御方法。'
    }
    return suggestions.get(dimension, '继续努力！')