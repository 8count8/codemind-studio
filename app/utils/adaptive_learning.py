"""
自适应学习路径（对应文档 §10.4.3 强化学习路径 V1.2+）

功能：基于 Anki SM-2 间隔重复算法，动态调整下一题难度。
答对题：间隔指数增长（指数退避）
答错题：间隔重置，近期复现

设计原则：
1. 实现 Anki SM-2 算法的核心逻辑
2. 纯函数，状态通过参数传入
3. 与能力矩阵分数联动调整难度

对应文档：能力矩阵.md §10.4.3
"""


# SM-2 算法默认参数
DEFAULT_EASE_FACTOR = 2.5
MIN_EASE_FACTOR = 1.3
DEFAULT_INTERVAL = 1
DEFAULT_REPETITIONS = 0

# 答题质量等级（SM-2 标准 0-5）
QUALITY_PERFECT = 5      # 完美回忆
QUALITY_CORRECT = 4      # 正确但略有犹豫
QUALITY_CORRECT_HARD = 3 # 正确但很吃力
QUALITY_WRONG_EASY = 2   # 错误但接近正确
QUALITY_WRONG = 1        # 错误
QUALITY_BLACKOUT = 0     # 完全不会


def sm2_update(repetitions, ease_factor, interval, quality):
    """
    Anki SM-2 间隔重复算法核心

    根据答题质量更新间隔、重复次数、难度系数

    参数:
        repetitions (int): 已连续答对次数
        ease_factor (float): 难度系数（≥1.3）
        interval (int): 当前间隔（天）
        quality (int): 答题质量 0-5
    返回:
        dict: {
            'repetitions': int,
            'ease_factor': float,
            'interval': int,
            'next_review_days': int
        }
    """
    # 答题质量 < 3 视为答错，重置重复次数
    if quality < 3:
        new_repetitions = 0
        new_interval = 1
    else:
        new_repetitions = repetitions + 1
        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = round(interval * ease_factor)

    # 更新难度系数
    # EF' = EF + (0.1 - (5 - q) × (0.08 + (5 - q) × 0.02))
    new_ease = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ease = max(MIN_EASE_FACTOR, new_ease)

    return {
        'repetitions': new_repetitions,
        'ease_factor': round(new_ease, 4),
        'interval': new_interval,
        'next_review_days': new_interval,
    }


def quality_from_score(score, is_correct):
    """
    根据评分和答题正确性推断 SM-2 答题质量等级

    参数:
        score (float): 能力评分 0-100
        is_correct (bool): 是否答对
    返回:
        int: 答题质量 0-5
    """
    if not is_correct:
        if score >= 50:
            return QUALITY_WRONG_EASY  # 错误但接近
        elif score >= 25:
            return QUALITY_WRONG
        else:
            return QUALITY_BLACKOUT

    # 答对的情况
    if score >= 90:
        return QUALITY_PERFECT
    elif score >= 75:
        return QUALITY_CORRECT
    else:
        return QUALITY_CORRECT_HARD


def adaptive_difficulty(mastery_probability, current_difficulty=None):
    """
    基于掌握概率动态调整下一题难度

    规则（对应文档 §10.4.3）：
    - 掌握概率 < 0.3：推荐简单题（需基础巩固）
    - 0.3 ≤ 掌握概率 < 0.7：推荐中等题（最近发展区）
    - 掌握概率 ≥ 0.7：推荐困难题（挑战提升）

    参数:
        mastery_probability (float): 知识点掌握概率 [0, 1]
        current_difficulty (str, optional): 当前难度
    返回:
        str: 推荐难度（'简单'/'中等'/'困难'）
    """
    if mastery_probability < 0.3:
        return '简单'
    elif mastery_probability < 0.7:
        return '中等'
    else:
        return '困难'


def get_review_schedule(user_id, limit=10):
    """
    获取用户需要复习的题目列表（基于 SM-2 间隔重复）

    简化实现：基于 answer_records 的答题历史，用 SM-2 计算每题的下次复习时间

    参数:
        user_id (int): 用户ID
        limit (int): 返回题目数量
    返回:
        tuple: (result_dict, status_code)
    """
    from app.models.db import get_db_connection, fetch_dict

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取用户所有答题记录（按题目分组，取最新一次）
        cursor.execute("""
            SELECT ar.question_id, ar.is_correct, ar.created_at,
                   p.title, p.difficulty, p.tags
            FROM answer_records ar
            LEFT JOIN problems p ON CAST(ar.question_id AS UNSIGNED) = p.id
            WHERE ar.user_id = %s AND ar.question_id REGEXP '^[0-9]+$'
            ORDER BY ar.created_at DESC
        """, (user_id,))
        rows = fetch_dict(cursor)

        # 按题目分组，保留最新记录
        latest_by_question = {}
        for r in rows:
            qid = r.get('question_id', '')
            if qid and qid not in latest_by_question:
                latest_by_question[qid] = r

        # 用 SM-2 计算每题复习计划
        review_list = []
        from datetime import datetime, timedelta

        for qid, record in latest_by_question.items():
            is_correct = bool(record.get('is_correct', 0))
            # 简化：假设 score=80 如果答对，score=40 如果答错
            score = 80 if is_correct else 40
            quality = quality_from_score(score, is_correct)

            # 假设初始状态
            sm2_result = sm2_update(0, DEFAULT_EASE_FACTOR, DEFAULT_INTERVAL, quality)

            # 计算下次复习日期
            try:
                created = record.get('created_at')
                if isinstance(created, str):
                    created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                elif isinstance(created, datetime):
                    created_dt = created
                else:
                    created_dt = datetime.now()
            except (ValueError, TypeError):
                created_dt = datetime.now()

            next_review = created_dt + timedelta(days=sm2_result['next_review_days'])
            is_due = next_review <= datetime.now(next_review.tzinfo) if next_review.tzinfo else next_review <= datetime.now()

            review_list.append({
                'question_id': qid,
                'title': record.get('title', ''),
                'difficulty': record.get('difficulty', '未知'),
                'tags': record.get('tags', ''),
                'last_correct': is_correct,
                'next_review_days': sm2_result['next_review_days'],
                'next_review_date': next_review.strftime('%Y-%m-%d'),
                'is_due': is_due,
                'ease_factor': sm2_result['ease_factor'],
                'quality': quality,
            })

        # 优先返回到期需要复习的
        review_list.sort(key=lambda x: (0 if x['is_due'] else 1, x['next_review_days']))
        review_list = review_list[:limit]

        due_count = sum(1 for r in review_list if r['is_due'])

        return {
            "review_schedule": review_list,
            "count": len(review_list),
            "due_count": due_count,
            "note": f"共 {len(review_list)} 题待复习，其中 {due_count} 题已到期"
        }, 200

    except Exception as e:
        import logging
        logging.error(f"get_review_schedule 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()
