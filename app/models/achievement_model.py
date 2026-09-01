"""
成就/勋章系统 Model 层

对应文档：能力矩阵.md §十一 成就与勋章系统

功能：
1. get_user_achievements：获取用户成就列表及解锁状态
2. check_and_unlock_achievements：检测并解锁达标的成就

成就类别：
- ability：维度分数达标（如语法达人/算法专家）
- submission：提交次数达标（如初出茅庐/坚持不懈）
- streak：连续打卡（预留）
- special：特殊条件（如全面发展）
"""

import logging
from app.models.db import get_db_connection, fetch_dict, fetch_one_dict


# 成就代码 → 检测维度映射（用于 dimension_score 类成就）
ACHIEVEMENT_DIMENSION_MAP = {
    'syntax_master': 'syntax_score',
    'algorithm_expert': 'algorithm_score',
    'project_architect': 'project_score',
    'debug_master': 'debug_score',
    'security_guard': 'security_score',
}


def get_user_achievements(user_id):
    """
    获取用户成就勋章列表及解锁状态

    返回所有成就定义，并标记当前用户是否已解锁

    参数:
        user_id (int): 用户ID
    返回:
        tuple: (result_dict, status_code)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询所有成就定义
        cursor.execute("""
            SELECT id, code, name, description, icon, category,
                   condition_type, condition_value
            FROM achievements
            ORDER BY category, id
        """)
        all_achievements = fetch_dict(cursor)

        # 查询用户已解锁的成就
        cursor.execute("""
            SELECT achievement_id, unlocked_at
            FROM user_achievements
            WHERE user_id = %s
        """, (user_id,))
        unlocked_rows = fetch_dict(cursor)
        unlocked_map = {
            int(r.get('achievement_id', 0)): r.get('unlocked_at')
            for r in unlocked_rows
        }

        # 组装返回结果
        achievements = []
        unlocked_count = 0
        for ach in all_achievements:
            ach_id = int(ach.get('id', 0))
            is_unlocked = ach_id in unlocked_map
            if is_unlocked:
                unlocked_count += 1
            achievements.append({
                'id': ach_id,
                'code': ach.get('code', ''),
                'name': ach.get('name', ''),
                'description': ach.get('description', ''),
                'icon': ach.get('icon', 'medal'),
                'category': ach.get('category', 'ability'),
                'condition_type': ach.get('condition_type', ''),
                'condition_value': float(ach.get('condition_value', 0) or 0),
                'unlocked': is_unlocked,
                'unlocked_at': unlocked_map.get(ach_id),
            })

        return {
            "achievements": achievements,
            "total": len(achievements),
            "unlocked_count": unlocked_count,
            "locked_count": len(achievements) - unlocked_count,
        }, 200

    except Exception as e:
        logging.error(f"get_user_achievements 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def check_and_unlock_achievements(user_id):
    """
    检测用户是否满足成就解锁条件，自动解锁达标的成就

    应在以下场景调用：
    1. 能力矩阵更新后（update_ability_matrix）
    2. 提交评估后（submit_evaluation）

    参数:
        user_id (int): 用户ID
    返回:
        tuple: (result_dict, status_code)
            result_dict 含 newly_unlocked 列表
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 获取用户当前能力矩阵
        cursor.execute("""
            SELECT syntax_score, algorithm_score, project_score,
                   debug_score, security_score
            FROM ability_matrix
            WHERE user_id = %s
        """, (user_id,))
        matrix = fetch_one_dict(cursor)

        # 2. 获取用户提交次数
        submission_count = 0
        try:
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM ability_submissions WHERE user_id = %s",
                (user_id,)
            )
            cnt_row = fetch_one_dict(cursor)
            if cnt_row:
                submission_count = int(cnt_row.get('cnt', 0) or 0)
        except Exception:
            pass

        # 3. 获取所有成就定义
        cursor.execute("""
            SELECT id, code, name, condition_type, condition_value
            FROM achievements
        """)
        all_achievements = fetch_dict(cursor)

        # 4. 获取用户已解锁的成就 ID
        cursor.execute("""
            SELECT achievement_id FROM user_achievements WHERE user_id = %s
        """, (user_id,))
        unlocked_rows = fetch_dict(cursor)
        unlocked_ids = {int(r.get('achievement_id', 0)) for r in unlocked_rows}

        # 5. 检测并解锁新成就
        newly_unlocked = []
        for ach in all_achievements:
            ach_id = int(ach.get('id', 0))
            if ach_id in unlocked_ids:
                continue

            code = ach.get('code', '')
            cond_type = ach.get('condition_type', '')
            cond_value = float(ach.get('condition_value', 0) or 0)
            should_unlock = False

            if cond_type == 'dimension_score' and matrix:
                # 维度分数达标检测
                dim_field = ACHIEVEMENT_DIMENSION_MAP.get(code)
                if dim_field:
                    dim_score = float(matrix.get(dim_field, 0) or 0)
                    if dim_score >= cond_value:
                        should_unlock = True

            elif cond_type == 'all_dimensions_60' and matrix:
                # 所有维度均达标检测
                all_pass = all(
                    float(matrix.get(d, 0) or 0) >= cond_value
                    for d in ['syntax_score', 'algorithm_score', 'project_score',
                              'debug_score', 'security_score']
                )
                if all_pass:
                    should_unlock = True

            elif cond_type == 'submission_count':
                # 提交次数达标检测
                if submission_count >= int(cond_value):
                    should_unlock = True

            if should_unlock:
                cursor.execute("""
                    INSERT IGNORE INTO user_achievements (user_id, achievement_id)
                    VALUES (%s, %s)
                """, (user_id, ach_id))
                newly_unlocked.append({
                    'id': ach_id,
                    'code': code,
                    'name': ach.get('name', ''),
                })

        conn.commit()

        return {
            "newly_unlocked": newly_unlocked,
            "newly_unlocked_count": len(newly_unlocked),
            "message": f"恭喜解锁 {len(newly_unlocked)} 个新成就！" if newly_unlocked else "暂无新成就解锁"
        }, 200

    except Exception as e:
        logging.error(f"check_and_unlock_achievements 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()
