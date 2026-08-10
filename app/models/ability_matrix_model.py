"""
能力矩阵数据模型层

该模块负责与 MySQL 数据库交互，处理用户能力矩阵和提交记录的数据操作。
包含以下功能：
1. 用户能力矩阵的增删改查
2. 能力评估提交记录的存储和查询
3. 能力趋势数据的统计分析
"""

import json
import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# MySQL 数据库配置
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# 能力维度定义
ABILITY_DIMENSIONS = ['syntax_score', 'algorithm_score', 'project_score', 'debug_score', 'security_score']

# 维度中文名称映射
DIMENSION_LABELS = {
    'syntax_score': '语法基础',
    'algorithm_score': '算法思维',
    'project_score': '项目实践',
    'debug_score': '调试能力',
    'security_score': '安全意识'
}


def create_mysql_connection():
    """
    创建到 MySQL 数据库的连接。
    :return: 如果成功返回连接对象，否则返回 None
    """
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        return connection
    except Error as e:
        logging.error(f"连接 MySQL 失败: {e}")
        return None


def init_ability_matrix(user_id):
    """
    为用户初始化能力矩阵记录（如果不存在则插入默认值）。
    :param user_id: 用户ID
    :return: 操作结果字典
    """
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "数据库连接失败"}, 500

    try:
        cursor = connection.cursor()
        # 使用 INSERT IGNORE 避免重复插入
        insert_query = """
            INSERT IGNORE INTO user_ability_matrix (user_id)
            VALUES (%s)
        """
        cursor.execute(insert_query, (user_id,))
        connection.commit()

        if cursor.rowcount > 0:
            logging.info(f"为用户 {user_id} 初始化能力矩阵成功")
        else:
            logging.info(f"用户 {user_id} 的能力矩阵已存在，无需初始化")

        cursor.close()
        connection.close()
        return {"message": "初始化成功"}, 200

    except Error as e:
        logging.error(f"初始化能力矩阵失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_ability_matrix(user_id):
    """
    获取指定用户的能力矩阵数据。
    :param user_id: 用户ID
    :return: 能力矩阵数据字典，包含五个维度的得分和等级
    """
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "数据库连接失败"}, 500

    try:
        cursor = connection.cursor(dictionary=True)
        select_query = """
            SELECT
                user_id,
                syntax_score,
                algorithm_score,
                project_score,
                debug_score,
                security_score,
                total_submissions,
                level,
                updated_at,
                created_at
            FROM user_ability_matrix
            WHERE user_id = %s
        """
        cursor.execute(select_query, (user_id,))
        result = cursor.fetchone()

        if result:
            # 将 datetime 转换为字符串以便 JSON 序列化
            if result.get('updated_at'):
                result['updated_at'] = result['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            if result.get('created_at'):
                result['created_at'] = result['created_at'].strftime('%Y-%m-%d %H:%M:%S')

            # 添加维度标签映射
            result['dimensions'] = {
                key: {
                    'label': DIMENSION_LABELS[key],
                    'score': round(result.get(key, 0), 2)
                }
                for key in ABILITY_DIMENSIONS
            }

            return {"matrix": result}, 200
        else:
            # 用户没有能力矩阵记录，返回默认值
            default_matrix = {
                'user_id': user_id,
                'syntax_score': 0,
                'algorithm_score': 0,
                'project_score': 0,
                'debug_score': 0,
                'security_score': 0,
                'total_submissions': 0,
                'level': '初学者',
                'dimensions': {
                    key: {'label': DIMENSION_LABELS[key], 'score': 0}
                    for key in ABILITY_DIMENSIONS
                }
            }
            return {"matrix": default_matrix}, 200

    except Error as e:
        logging.error(f"获取能力矩阵失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def update_ability_matrix(user_id, scores):
    """
    更新用户的能力矩阵（根据新提交的评分重新计算平均值）。
    :param user_id: 用户ID
    :param scores: 新提交的评分字典，包含五个维度的得分
    :return: 更新后的能力矩阵数据
    """
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "数据库连接失败"}, 500

    try:
        cursor = connection.cursor(dictionary=True)

        # 获取当前矩阵数据
        select_query = """
            SELECT syntax_score, algorithm_score, project_score,
                   debug_score, security_score, total_submissions
            FROM user_ability_matrix
            WHERE user_id = %s
        """
        cursor.execute(select_query, (user_id,))
        current = cursor.fetchone()

        if current is None:
            # 用户矩阵不存在，先初始化
            insert_query = """
                INSERT INTO user_ability_matrix
                (user_id, syntax_score, algorithm_score, project_score,
                 debug_score, security_score, total_submissions, level)
                VALUES (%s, %s, %s, %s, %s, %s, 1, %s)
            """
            level = calculate_level(scores)
            cursor.execute(insert_query, (
                user_id,
                scores.get('syntax_score', 0),
                scores.get('algorithm_score', 0),
                scores.get('project_score', 0),
                scores.get('debug_score', 0),
                scores.get('security_score', 0),
                level
            ))
        else:
            # 使用加权平均更新：(旧分数 * 旧次数 + 新分数) / (旧次数 + 1)
            n = current['total_submissions']
            new_scores = {}
            for dim in ABILITY_DIMENSIONS:
                old_score = current[dim]
                new_score = scores.get(dim, 0)
                # 使用增量平均值公式
                new_scores[dim] = round((old_score * n + new_score) / (n + 1), 2)

            level = calculate_level(new_scores)

            update_query = """
                UPDATE user_ability_matrix
                SET syntax_score = %s,
                    algorithm_score = %s,
                    project_score = %s,
                    debug_score = %s,
                    security_score = %s,
                    total_submissions = total_submissions + 1,
                    level = %s
                WHERE user_id = %s
            """
            cursor.execute(update_query, (
                new_scores['syntax_score'],
                new_scores['algorithm_score'],
                new_scores['project_score'],
                new_scores['debug_score'],
                new_scores['security_score'],
                level,
                user_id
            ))

        connection.commit()
        cursor.close()
        connection.close()

        # 返回更新后的矩阵
        return get_ability_matrix(user_id)

    except Error as e:
        logging.error(f"更新能力矩阵失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def save_submission(user_id, source_type, source_id, scores, detail=None):
    """
    保存一次能力评估提交记录。
    :param user_id: 用户ID
    :param source_type: 数据来源类型（code_submit/ai_review/quiz_answer）
    :param source_id: 来源ID（可选）
    :param scores: 评分字典
    :param detail: 评分详情（可选，JSON格式）
    :return: 操作结果
    """
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "数据库连接失败"}, 500

    try:
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO ability_submissions
            (user_id, source_type, source_id,
             syntax_score, algorithm_score, project_score,
             debug_score, security_score, detail)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        detail_json = json.dumps(detail, ensure_ascii=False) if detail else None
        cursor.execute(insert_query, (
            user_id,
            source_type,
            source_id,
            scores.get('syntax_score', 0),
            scores.get('algorithm_score', 0),
            scores.get('project_score', 0),
            scores.get('debug_score', 0),
            scores.get('security_score', 0),
            detail_json
        ))
        connection.commit()

        submission_id = cursor.lastrowid
        logging.info(f"保存能力评估提交记录成功: 用户={user_id}, ID={submission_id}")

        cursor.close()
        connection.close()
        return {"submission_id": submission_id, "message": "提交记录保存成功"}, 200

    except Error as e:
        logging.error(f"保存能力评估提交记录失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_submission_history(user_id, limit=30):
    """
    获取用户的能力评估提交历史记录。
    :param user_id: 用户ID
    :param limit: 返回的记录数量限制（默认30条）
    :return: 提交记录列表
    """
    connection = create_mysql_connection()
    if connection is None:
        return {"error": "数据库连接失败"}, 500

    try:
        cursor = connection.cursor(dictionary=True)
        select_query = """
            SELECT id, source_type, source_id,
                   syntax_score, algorithm_score, project_score,
                   debug_score, security_score, detail, created_at
            FROM ability_submissions
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        cursor.execute(select_query, (user_id, limit))
        results = cursor.fetchall()

        # 处理 datetime 和 detail 字段
        for row in results:
            if row.get('created_at'):
                row['created_at'] = row['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if row.get('detail'):
                try:
                    row['detail'] = json.loads(row['detail'])
                except (json.JSONDecodeError, TypeError):
                    pass

        cursor.close()
        connection.close()
        return {"submissions": results, "total": len(results)}, 200

    except Error as e:
        logging.error(f"获取提交历史记录失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_ability_trend(user_id, dimension, days=30):
    """
    获取用户在指定维度上的能力趋势数据（按日期聚合）。
    :param user_id: 用户ID
    :param dimension: 能力维度（如 syntax_score）
    :param days: 统计最近天数（默认30天）
    :return: 趋势数据列表
    """
    if dimension not in ABILITY_DIMENSIONS:
        return {"error": f"无效的能力维度，可选值: {ABILITY_DIMENSIONS}"}, 400

    connection = create_mysql_connection()
    if connection is None:
        return {"error": "数据库连接失败"}, 500

    try:
        cursor = connection.cursor(dictionary=True)
        select_query = f"""
            SELECT DATE(created_at) AS date,
                   AVG({dimension}) AS avg_score,
                   COUNT(*) AS count
            FROM ability_submissions
            WHERE user_id = %s
              AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        """
        cursor.execute(select_query, (user_id, days))
        results = cursor.fetchall()

        # 处理日期格式
        for row in results:
            if row.get('date'):
                row['date'] = row['date'].strftime('%Y-%m-%d')
            row['avg_score'] = round(float(row['avg_score']), 2) if row.get('avg_score') else 0

        cursor.close()
        connection.close()
        return {"trend": results, "dimension": dimension, "days": days}, 200

    except Error as e:
        logging.error(f"获取能力趋势数据失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def calculate_level(scores):
    """
    根据各项能力得分计算综合等级。
    :param scores: 能力得分字典
    :return: 等级字符串
    """
    # 计算各项能力的平均分
    if not scores:
        return '初学者'

    total = sum(scores.get(dim, 0) for dim in ABILITY_DIMENSIONS)
    avg = total / len(ABILITY_DIMENSIONS)

    # 等级划分
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
    """
    获取用户的薄弱维度（得分低于平均分的维度）。
    :param user_id: 用户ID
    :return: 薄弱维度列表及学习建议
    """
    result, status = get_ability_matrix(user_id)
    if status != 200 or 'matrix' not in result:
        return result, status

    matrix = result['matrix']
    dimensions_data = matrix.get('dimensions', {})

    # 计算平均分
    scores = [d['score'] for d in dimensions_data.values()]
    avg_score = sum(scores) / len(scores) if scores else 0

    # 找出薄弱维度
    weak_dimensions = []
    for key, data in dimensions_data.items():
        if data['score'] < avg_score and data['score'] < 60:
            weak_dimensions.append({
                'dimension': key,
                'label': data['label'],
                'score': data['score'],
                'suggestion': get_dimension_suggestion(key)
            })

    # 按得分升序排列（最弱的排前面）
    weak_dimensions.sort(key=lambda x: x['score'])

    return {"weak_dimensions": weak_dimensions, "average_score": round(avg_score, 2)}, 200


def get_dimension_suggestion(dimension):
    """
    根据薄弱维度返回针对性的学习建议。
    :param dimension: 能力维度键名
    :return: 学习建议字符串
    """
    suggestions = {
        'syntax_score': '建议加强代码规范训练，多练习基础语法，关注代码可读性和PEP8规范。',
        'algorithm_score': '建议练习经典算法题，从排序、搜索等基础算法入手，逐步挑战动态规划和图论问题。',
        'project_score': '建议尝试完整的小项目开发，注重代码模块化设计和功能完整性，学习设计模式。',
        'debug_score': '建议学习调试工具的使用，练习阅读错误日志，培养系统性排查问题的思维。',
        'security_score': '建议学习Web安全基础知识，了解常见漏洞（SQL注入、XSS等）的防御方法。'
    }
    return suggestions.get(dimension, '继续努力，保持学习热情！')
