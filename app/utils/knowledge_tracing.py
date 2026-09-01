"""
知识追踪模型（对应文档 §10.4.2 知识追踪模型 V1.2+）

功能：追踪每个用户对每个知识点的掌握概率，优先推荐掌握概率在 0.3~0.7 区间（最近发展区）的题目。

设计决策：
1. 采用贝叶斯知识追踪（BKT）而非深度学习 DKT，无需 PyTorch 依赖
2. 每个知识点维护 4 个参数：P(已知)、P(转移)、P(猜测)、P(失误)
3. 基于答题历史更新掌握概率

对应文档：能力矩阵.md §10.4.2
"""

import logging
from app.models.db import get_db_connection, fetch_dict, fetch_one_dict


# BKT 默认参数
DEFAULT_P_KNOWN = 0.1      # 初始掌握概率
DEFAULT_P_TRANSIT = 0.3    # 学习后从未知→已知的转移概率
DEFAULT_P_SLIP = 0.1       # 已知但答错的失误概率
DEFAULT_P_GUESS = 0.25     # 未知但答对的猜测概率

# 最近发展区区间（掌握概率在此区间内的知识点优先推荐）
ZPD_MIN = 0.3
ZPD_MAX = 0.7


def update_mastery(p_known, is_correct, p_transit=DEFAULT_P_TRANSIT,
                   p_slip=DEFAULT_P_SLIP, p_guess=DEFAULT_P_GUESS):
    """
    贝叶斯知识追踪：根据答题结果更新掌握概率

    公式：
    P(已知|答对) = P(答对|已知)×P(已知) / P(答对)
    P(答对) = P(已知)×(1-P(失误)) + (1-P(已知))×P(猜测)
    转移：P(已知)' = P(已知|答题) + (1-P(已知|答题))×P(转移)

    参数:
        p_known (float): 答题前的掌握概率 [0, 1]
        is_correct (bool): 是否答对
        p_transit (float): 转移概率
        p_slip (float): 失误概率
        p_guess (float): 猜测概率
    返回:
        float: 答题后的掌握概率 [0, 1]
    """
    if is_correct:
        # P(已知|答对) = (1-slip)×P(已知) / [(1-slip)×P(已知) + guess×(1-P(已知))]
        numerator = (1 - p_slip) * p_known
        denominator = (1 - p_slip) * p_known + p_guess * (1 - p_known)
    else:
        # P(已知|答错) = slip×P(已知) / [slip×P(已知) + (1-guess)×(1-P(已知))]
        numerator = p_slip * p_known
        denominator = p_slip * p_known + (1 - p_guess) * (1 - p_known)

    if denominator == 0:
        p_posterior = p_known
    else:
        p_posterior = numerator / denominator

    # 转移：学习后可能从未知→已知
    p_known_new = p_posterior + (1 - p_posterior) * p_transit

    return max(0.0, min(1.0, p_known_new))


def get_user_mastery(user_id, tag=None):
    """
    获取用户各知识点的掌握概率

    数据来源：基于 answer_records 聚合每个 tags 的答题正确率，
    用 BKT 算法计算掌握概率

    参数:
        user_id (int): 用户ID
        tag (str, optional): 指定知识点，None 则返回所有
    返回:
        tuple: (result_dict, status_code)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 按题目标签聚合答题历史
        tag_filter = "AND p.tags LIKE %s" if tag else ""
        params = [user_id]
        if tag:
            params.append(f'%{tag}%')

        cursor.execute(f"""
            SELECT p.tags,
                   COUNT(*) AS total,
                   SUM(CASE WHEN ar.is_correct = 1 THEN 1 ELSE 0 END) AS correct_count
            FROM answer_records ar
            LEFT JOIN problems p ON CAST(ar.question_id AS UNSIGNED) = p.id
            WHERE ar.user_id = %s AND p.tags IS NOT NULL AND p.tags != ''
                  {tag_filter}
            GROUP BY p.tags
        """, params)
        rows = fetch_dict(cursor)

        mastery_list = []
        for r in rows:
            tags_str = r.get('tags', '') or ''
            total = int(r.get('total', 0))
            correct = int(r.get('correct_count', 0))

            if total == 0:
                continue

            # 用 BKT 迭代更新掌握概率
            p_known = DEFAULT_P_KNOWN
            # 按答题顺序模拟更新（简化：用正确率迭代）
            for _ in range(correct):
                p_known = update_mastery(p_known, True)
            for _ in range(total - correct):
                p_known = update_mastery(p_known, False)

            # 判断是否在最近发展区
            in_zpd = ZPD_MIN <= p_known <= ZPD_MAX

            mastery_list.append({
                'tag': tags_str,
                'total_attempts': total,
                'correct_count': correct,
                'accuracy': round(correct / total, 4) if total > 0 else 0,
                'mastery_probability': round(p_known, 4),
                'in_zpd': in_zpd,
                'zpd_label': '最近发展区' if in_zpd else ('已掌握' if p_known > ZPD_MAX else '需基础学习')
            })

        # 按掌握概率排序（最近发展区优先）
        mastery_list.sort(key=lambda x: (
            0 if x['in_zpd'] else (1 if x['mastery_probability'] > ZPD_MAX else 2),
            -x['mastery_probability']
        ))

        return {
            "mastery": mastery_list,
            "count": len(mastery_list),
            "zpd_count": sum(1 for m in mastery_list if m['in_zpd']),
            "note": f"共追踪 {len(mastery_list)} 个知识点，其中 {sum(1 for m in mastery_list if m['in_zpd'])} 个在最近发展区"
        }, 200

    except Exception as e:
        logging.error(f"get_user_mastery 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def recommend_by_mastery(user_id, limit=5):
    """
    基于知识追踪的推荐：优先推荐最近发展区的题目

    算法：
    1. 获取用户各知识点掌握概率
    2. 筛选掌握概率在 0.3~0.7（最近发展区）的知识点
    3. 查询这些知识点对应的、用户未做过的题目

    参数:
        user_id (int): 用户ID
        limit (int): 返回题目数量
    返回:
        tuple: (result_dict, status_code)
    """
    mastery_result, status = get_user_mastery(user_id)
    if status != 200:
        return mastery_result, status

    zpd_tags = [m['tag'] for m in mastery_result.get('mastery', []) if m.get('in_zpd')]

    if not zpd_tags:
        return {
            "recommendations": [],
            "count": 0,
            "note": "暂无最近发展区知识点，建议先完成基础练习"
        }, 200

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取已做题
        cursor.execute("""
            SELECT DISTINCT CAST(question_id AS UNSIGNED) AS qid
            FROM answer_records
            WHERE user_id = %s AND question_id REGEXP '^[0-9]+$'
        """, (user_id,))
        done_rows = fetch_dict(cursor)
        done_ids = [int(r.get('qid', 0)) for r in done_rows if r.get('qid')]

        # 构建 ZPD 标签正则
        tag_regex = '|'.join(zpd_tags[:5])

        done_filter = ""
        params = []
        if done_ids:
            placeholders = ','.join(['%s'] * len(done_ids))
            done_filter = f" AND p.id NOT IN ({placeholders})"
            params.extend(done_ids)

        sql = """
            SELECT p.id, p.title, p.difficulty, p.tags
            FROM problems p
            WHERE (p.tags REGEXP %s)
        """ + done_filter + " ORDER BY p.id LIMIT %s"

        cursor.execute(sql, [tag_regex] + params + [limit])
        rows = fetch_dict(cursor)

        recommendations = []
        for r in rows:
            recommendations.append({
                'question_id': str(r.get('id', '')),
                'title': r.get('title', ''),
                'difficulty': r.get('difficulty', '未知'),
                'tags': r.get('tags', ''),
                'reason': '该题涉及你正在学习中的知识点（最近发展区）'
            })

        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "zpd_tags": zpd_tags[:5],
            "note": "基于知识追踪，优先推荐最近发展区的题目"
        }, 200

    except Exception as e:
        logging.error(f"recommend_by_mastery 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()
