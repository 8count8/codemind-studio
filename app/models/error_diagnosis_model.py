"""
错题诊断引擎

实现文档 §1 项目需求文档 中列出的"错题诊断引擎"核心功能：
1. 自动分析用户的错误模式（哪类题目错得多、错误类型分布）
2. 关联相似题目推荐（按 tags 标签相似度推荐同类强化题）

对应文档：1.项目需求文档.md §2.1 错题诊断引擎
设计文档：能力矩阵.md §10.3.2 错题标签聚类驱动推荐

数据来源：answer_records 表（is_correct=0 的记录为错题）
"""

import logging
from app.models.db import get_db_connection, fetch_dict


def diagnose_error_patterns(user_id, limit=50):
    """
    自动分析用户的错误模式

    分析维度：
    1. 错题标签聚类：统计错题中 tags 出现频次，找出高频错误知识点
    2. 错误类型分布：按 is_correct=0 的题目分布统计
    3. 错题率：错题数 / 总答题数

    参数:
        user_id (int): 用户ID
        limit (int): 分析最近多少条记录，默认 50
    返回:
        dict: 错误模式分析结果
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 统计总答题数与错题数
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) AS wrong_count
            FROM answer_records
            WHERE user_id = %s
        """, (user_id,))
        row = fetch_dict(cursor)
        total = int(row[0].get('total', 0)) if row else 0
        wrong_count = int(row[0].get('wrong_count', 0)) if row else 0
        error_rate = round(wrong_count / total, 4) if total > 0 else 0.0

        # 2. 错题标签聚类：联表 problems 获取 tags，统计高频错误知识点
        cursor.execute("""
            SELECT p.tags, COUNT(*) AS cnt
            FROM answer_records ar
            LEFT JOIN problems p ON CAST(ar.question_id AS UNSIGNED) = p.id
            WHERE ar.user_id = %s AND ar.is_correct = 0
              AND p.tags IS NOT NULL AND p.tags != ''
            GROUP BY p.tags
            ORDER BY cnt DESC
            LIMIT %s
        """, (user_id, limit))
        tag_rows = fetch_dict(cursor)

        # 解析 tags（tags 字段可能是逗号分隔或 JSON 数组字符串）
        tag_counter = {}
        for r in tag_rows:
            tags_str = r.get('tags', '') or ''
            cnt = int(r.get('cnt', 0))
            # 尝试解析为 JSON 数组，失败则按逗号分隔
            parsed_tags = _parse_tags(tags_str)
            for tag in parsed_tags:
                tag = tag.strip()
                if tag:
                    tag_counter[tag] = tag_counter.get(tag, 0) + cnt

        # 按错误频次排序
        sorted_tags = sorted(tag_counter.items(), key=lambda x: x[1], reverse=True)
        weak_tags = [{'tag': t, 'error_count': c} for t, c in sorted_tags[:10]]

        # 3. 按题目难度的错误分布
        cursor.execute("""
            SELECT p.difficulty, COUNT(*) AS cnt
            FROM answer_records ar
            LEFT JOIN problems p ON CAST(ar.question_id AS UNSIGNED) = p.id
            WHERE ar.user_id = %s AND ar.is_correct = 0
              AND p.difficulty IS NOT NULL
            GROUP BY p.difficulty
            ORDER BY cnt DESC
        """, (user_id,))
        diff_rows = fetch_dict(cursor)
        difficulty_distribution = [
            {'difficulty': r.get('difficulty', '未知'), 'count': int(r.get('cnt', 0))}
            for r in diff_rows
        ]

        return {
            'total_submissions': total,
            'wrong_count': wrong_count,
            'error_rate': error_rate,
            'weak_tags': weak_tags,
            'difficulty_distribution': difficulty_distribution,
            'analysis_note': '基于错题 tags 聚类，高频错误知识点为薄弱项'
        }, 200

    except Exception as e:
        logging.error(f"diagnose_error_patterns 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def recommend_similar_questions(user_id, limit=5):
    """
    基于错题标签聚类推荐相似题目（对应文档 §10.3.2）

    算法：
    1. 获取用户错题的高频 tags
    2. 从 problems 表查询 tags 相似但用户未做过的题
    3. 按标签命中数排序

    参数:
        user_id (int): 用户ID
        limit (int): 返回题目数量
    返回:
        dict: 相似题目推荐结果
    """
    # 先获取用户高频错题标签
    error_result, status = diagnose_error_patterns(user_id, limit=50)
    if status != 200:
        return error_result, status

    weak_tags = [item['tag'] for item in error_result.get('weak_tags', [])]
    if not weak_tags:
        return {
            'recommendations': [],
            'count': 0,
            'note': '暂无错题记录或错题无标签，无法推荐相似题目'
        }, 200

    # 构建 tags 正则
    tag_regex = '|'.join(weak_tags[:5])  # 取前5个高频标签

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询用户已做题 ID（用于去重）
        cursor.execute("""
            SELECT DISTINCT CAST(question_id AS UNSIGNED) AS qid
            FROM answer_records
            WHERE user_id = %s AND question_id REGEXP '^[0-9]+$'
        """, (user_id,))
        done_rows = fetch_dict(cursor)
        done_ids = [int(r.get('qid', 0)) for r in done_rows if r.get('qid')]

        done_filter = ""
        params = []
        if done_ids:
            placeholders = ','.join(['%s'] * len(done_ids))
            done_filter = f" AND p.id NOT IN ({placeholders})"
            params.extend(done_ids)

        # 查询标签相似的新题
        sql = """
            SELECT p.id, p.title, p.difficulty, p.tags
            FROM problems p
            WHERE (p.tags REGEXP %s)
        """ + done_filter + " ORDER BY p.id LIMIT %s"

        cursor.execute(sql, [tag_regex] + params + [limit])
        rows = fetch_dict(cursor)

        recommendations = []
        for r in rows:
            # 计算标签命中数（用于排序参考）
            question_tags = _parse_tags(r.get('tags', '') or '')
            hit_count = sum(1 for t in question_tags if t in weak_tags)
            recommendations.append({
                'question_id': str(r.get('id', '')),
                'title': r.get('title', ''),
                'difficulty': r.get('difficulty', '未知'),
                'tags': r.get('tags', ''),
                'tag_hits': hit_count,
                'reason': f'与你错题高频知识点（{",".join(weak_tags[:3])}）相关'
            })

        # 按标签命中数降序
        recommendations.sort(key=lambda x: x['tag_hits'], reverse=True)

        return {
            'recommendations': recommendations,
            'count': len(recommendations),
            'weak_tags_used': weak_tags[:5],
            'note': '基于错题标签聚类推荐相似强化题'
        }, 200

    except Exception as e:
        logging.error(f"recommend_similar_questions 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _parse_tags(tags_str):
    """
    解析 tags 字段（兼容 JSON 数组字符串和逗号分隔字符串）

    参数:
        tags_str (str): tags 字段值
    返回:
        list[str]: 标签列表
    """
    if not tags_str:
        return []

    # 尝试 JSON 解析
    if tags_str.strip().startswith('['):
        try:
            import json
            parsed = json.loads(tags_str)
            if isinstance(parsed, list):
                return [str(t) for t in parsed]
        except (json.JSONDecodeError, ValueError):
            pass

    # 退回逗号分隔
    return [t.strip() for t in tags_str.split(',') if t.strip()]
