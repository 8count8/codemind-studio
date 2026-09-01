"""
协同过滤推荐模块（对应文档 §10.4.1 基于用户的协同过滤）

功能：基于 5 维能力向量的余弦相似度，找到与当前用户能力画像相近的 N 个用户，
推荐他们做过但当前用户没做过的题。

设计原则：
1. 用户量 < 100 时降级到 None（样本不足）
2. 纯函数 + 数据库查询分离，便于测试
3. 余弦相似度阈值 ≥ 0.9 才视为"相似用户"

对应文档：能力矩阵.md §10.4.1
"""

import math
import logging
from app.models.db import get_db_connection, fetch_dict


# 协同过滤启用的最小用户数阈值
COLLAB_MIN_USERS = 100
# 相似度阈值
SIMILARITY_THRESHOLD = 0.9
# 相似用户数量上限
MAX_SIMILAR_USERS = 10


def cosine_similarity(vec_a, vec_b):
    """
    计算两个向量的余弦相似度

    参数:
        vec_a (list[float]): 向量 A
        vec_b (list[float]): 向量 B
    返回:
        float: 余弦相似度 [0, 1]
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def find_similar_users(user_id, threshold=SIMILARITY_THRESHOLD, max_users=MAX_SIMILAR_USERS):
    """
    找到与当前用户能力画像相似的 N 个用户

    算法：
    1. 获取当前用户的 5 维能力向量
    2. 遍历所有其他用户，计算余弦相似度
    3. 筛选相似度 ≥ threshold 的用户，按相似度降序排列

    参数:
        user_id (int): 当前用户ID
        threshold (float): 相似度阈值
        max_users (int): 返回用户数量上限
    返回:
        tuple: (result_dict, status_code)
            result_dict 含 similar_users 列表
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查总用户数
        cursor.execute("SELECT COUNT(*) AS total FROM ability_matrix")
        total_row = fetch_dict(cursor)
        total_users = int(total_row[0].get('total', 0)) if total_row else 0

        if total_users < COLLAB_MIN_USERS:
            return {
                "similar_users": [],
                "total_users": total_users,
                "collab_enabled": False,
                "note": f"用户量 {total_users} < {COLLAB_MIN_USERS}，协同过滤未启用，需积累更多用户数据"
            }, 200

        # 获取当前用户能力向量
        cursor.execute("""
            SELECT syntax_score, algorithm_score, project_score,
                   debug_score, security_score, user_id
            FROM ability_matrix
            WHERE user_id = %s
        """, (user_id,))
        current = fetch_dict(cursor)
        if not current:
            return {"error": "用户能力矩阵不存在"}, 404

        current_vec = [
            float(current[0].get('syntax_score', 0)),
            float(current[0].get('algorithm_score', 0)),
            float(current[0].get('project_score', 0)),
            float(current[0].get('debug_score', 0)),
            float(current[0].get('security_score', 0)),
        ]

        # 获取所有其他用户的能力向量
        cursor.execute("""
            SELECT user_id, syntax_score, algorithm_score, project_score,
                   debug_score, security_score
            FROM ability_matrix
            WHERE user_id != %s
        """, (user_id,))
        all_users = fetch_dict(cursor)

        # 计算相似度
        similar = []
        for u in all_users:
            u_vec = [
                float(u.get('syntax_score', 0)),
                float(u.get('algorithm_score', 0)),
                float(u.get('project_score', 0)),
                float(u.get('debug_score', 0)),
                float(u.get('security_score', 0)),
            ]
            sim = cosine_similarity(current_vec, u_vec)
            if sim >= threshold:
                similar.append({
                    'user_id': int(u.get('user_id', 0)),
                    'similarity': round(sim, 4)
                })

        # 按相似度降序
        similar.sort(key=lambda x: x['similarity'], reverse=True)
        similar = similar[:max_users]

        return {
            "similar_users": similar,
            "total_users": total_users,
            "collab_enabled": True,
            "threshold": threshold,
            "note": f"找到 {len(similar)} 位相似用户（相似度≥{threshold}）"
        }, 200

    except Exception as e:
        logging.error(f"find_similar_users 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def collaborative_recommendations(user_id, limit=5):
    """
    基于协同过滤的题目推荐

    算法：
    1. 找到相似用户
    2. 查询相似用户做过但当前用户没做过的题
    3. 按相似用户做题频次排序

    参数:
        user_id (int): 当前用户ID
        limit (int): 返回题目数量
    返回:
        tuple: (result_dict, status_code)
    """
    # 先找相似用户
    sim_result, sim_status = find_similar_users(user_id)
    if sim_status != 200:
        return sim_result, sim_status

    if not sim_result.get('collab_enabled'):
        return {
            "recommendations": [],
            "count": 0,
            "note": sim_result.get('note', '协同过滤未启用'),
            "collab_enabled": False
        }, 200

    similar_users = sim_result.get('similar_users', [])
    if not similar_users:
        return {
            "recommendations": [],
            "count": 0,
            "note": "暂无相似用户，无法生成协同推荐",
            "collab_enabled": True
        }, 200

    similar_user_ids = [u['user_id'] for u in similar_users]

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取当前用户已做题
        cursor.execute("""
            SELECT DISTINCT CAST(question_id AS UNSIGNED) AS qid
            FROM answer_records
            WHERE user_id = %s AND question_id REGEXP '^[0-9]+$'
        """, (user_id,))
        done_rows = fetch_dict(cursor)
        done_ids = [int(r.get('qid', 0)) for r in done_rows if r.get('qid')]

        # 查询相似用户做过、当前用户没做过的题
        placeholders = ','.join(['%s'] * len(similar_user_ids))
        done_filter = ""
        params = list(similar_user_ids)
        if done_ids:
            done_placeholders = ','.join(['%s'] * len(done_ids))
            done_filter = f" AND p.id NOT IN ({done_placeholders})"
            params.extend(done_ids)

        sql = f"""
            SELECT p.id, p.title, p.difficulty, p.tags,
                   COUNT(ar.user_id) AS solve_count
            FROM answer_records ar
            INNER JOIN problems p ON CAST(ar.question_id AS UNSIGNED) = p.id
            WHERE ar.user_id IN ({placeholders})
              AND ar.is_correct = 1
              {done_filter}
            GROUP BY p.id, p.title, p.difficulty, p.tags
            ORDER BY solve_count DESC
            LIMIT %s
        """
        params.append(limit)
        cursor.execute(sql, params)
        rows = fetch_dict(cursor)

        recommendations = []
        for r in rows:
            recommendations.append({
                'question_id': str(r.get('id', '')),
                'title': r.get('title', ''),
                'difficulty': r.get('difficulty', '未知'),
                'tags': r.get('tags', ''),
                'solve_count': int(r.get('solve_count', 0)),
                'reason': f"{r.get('solve_count', 0)} 位能力相近的用户已解此题"
            })

        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "collab_enabled": True,
            "similar_users_count": len(similar_user_ids),
            "note": "基于协同过滤，推荐能力相近用户已解的题目"
        }, 200

    except Exception as e:
        logging.error(f"collaborative_recommendations 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()
