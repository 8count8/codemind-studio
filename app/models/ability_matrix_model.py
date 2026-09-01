"""能力矩阵数据模型层 - MySQL"""

# ⚠️ 循环依赖约束（CRITICAL）
# ❌ 禁止: from app.service.xxx import xxx
# 原因: Model 层不应依赖 Service 层，避免循环导入
# 历史: 曾存在 calculate_recommendations() 包装函数导致 Model→Service 反向依赖
#       已移除包装函数，改为直接从 Service 层调用
# 如需业务逻辑: 通过参数传递、事件回调或独立的 Calculator 模块实现

import json
import logging
from datetime import datetime

from app.models.db import get_db_connection, fetch_one_dict, fetch_dict
from app.utils.ability_matrix_calculator import (
    ABILITY_DIMENSIONS,
    DIMENSION_LABELS,
    DIMENSION_WEIGHTS,
    EMA_DELTA_CAP,
    EMA_ALPHA_MAX,
    calculate_level,
    get_dimension_suggestion,
    build_dimensions_dict,
    diagnose_weak_dimensions,
)

logging.basicConfig(level=logging.INFO)

# 向后兼容：从 calculator 重导出常量和函数
# 旧代码仍可通过 from app.models.ability_matrix_model import calculate_level 使用


def init_ability_matrix(user_id):
    """为用户初始化能力矩阵记录"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT IGNORE INTO ability_matrix (user_id)
            VALUES (%s)
        """, (user_id,))
        conn.commit()

        if cursor.rowcount > 0:
            logging.info(f"为用户 {user_id} 初始化能力矩阵成功")
        return {"message": "初始化成功"}, 200
    except Exception as e:
        logging.error(f"初始化能力矩阵失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def get_ability_matrix(user_id):
    """获取指定用户的能力矩阵数据"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT user_id, syntax_score, algorithm_score, project_score,
                   debug_score, security_score, updated_at
            FROM ability_matrix
            WHERE user_id = %s
        """, (user_id,))
        result = fetch_one_dict(cursor)

        # 获取提交总数
        total_submissions = 0
        try:
            _ensure_submission_table()
            cursor.execute("SELECT COUNT(*) AS cnt FROM ability_submissions WHERE user_id = %s", (user_id,))
            count_row = fetch_one_dict(cursor)
            if count_row:
                total_submissions = count_row.get('cnt', 0)
        except Exception:
            pass

        if result:
            result_dict = result
            scores_map = {dim: result_dict.get(dim, 0) or 0 for dim in ABILITY_DIMENSIONS}
            result_dict['level'] = calculate_level(scores_map)
            result_dict['total_submissions'] = total_submissions
            result_dict['dimensions'] = build_dimensions_dict(scores_map)
            return {"matrix": result_dict}, 200
        else:
            default_scores = {dim: 0 for dim in ABILITY_DIMENSIONS}
            default_matrix = {
                'user_id': user_id,
                **default_scores,
                'level': '初学者',
                'total_submissions': total_submissions,
                'dimensions': build_dimensions_dict(default_scores)
            }
            return {"matrix": default_matrix}, 200
    except Exception as e:
        logging.error(f"获取能力矩阵失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if connection:
            connection.close()


def update_ability_matrix(user_id, scores):
    """
    使用 EMA 指数移动平均算法更新用户的能力矩阵

    算法公式（对应文档：能力矩阵.md §3.1）：
        α = min(EMA_ALPHA_MAX, 2 / (N + 1))    # 学习率随提交次数衰减
        new_score = (1 - α) × old_score + α × new_raw × weight
        delta = new_score - old_score，限制在 ±EMA_DELTA_CAP 之间（防作弊）

    参数:
        user_id (int): 用户ID
        scores (dict): 新的 5 维评分，如 {'syntax_score': 80, ...}
    返回:
        tuple: (result_dict, status_code)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 读取旧矩阵
        cursor.execute("""
            SELECT syntax_score, algorithm_score, project_score,
                   debug_score, security_score
            FROM ability_matrix
            WHERE user_id = %s
        """, (user_id,))
        current = fetch_one_dict(cursor)

        # 读取历史提交次数（用于 EMA 学习率衰减）
        submission_count = 0
        try:
            _ensure_submission_table()
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM ability_submissions WHERE user_id = %s",
                (user_id,)
            )
            count_row = fetch_one_dict(cursor)
            if count_row:
                submission_count = int(count_row.get('cnt', 0) or 0)
        except Exception:
            pass

        # EMA 学习率：随提交次数衰减（新用户 α=0.3 快速收敛，老用户 α→0 稳定）
        alpha = min(EMA_ALPHA_MAX, 2.0 / (submission_count + 1))

        if current is None:
            # 首次提交：直接 INSERT（按权重加权初始化）
            init_scores = {}
            for dim in ABILITY_DIMENSIONS:
                raw = float(scores.get(dim, 0) or 0)
                weight = DIMENSION_WEIGHTS.get(dim, 1.0)
                init_scores[dim] = round(min(raw * weight, 100.0), 2)

            cursor.execute("""
                INSERT INTO ability_matrix
                (user_id, syntax_score, algorithm_score, project_score,
                 debug_score, security_score, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                user_id,
                init_scores['syntax_score'],
                init_scores['algorithm_score'],
                init_scores['project_score'],
                init_scores['debug_score'],
                init_scores['security_score']
            ))
        else:
            # 后续提交：EMA 指数移动平均 + ±15 分 cap 防作弊
            new_scores = {}
            for dim in ABILITY_DIMENSIONS:
                old_score = float(current.get(dim, 0) or 0)
                new_raw = float(scores.get(dim, 0) or 0)
                weight = DIMENSION_WEIGHTS.get(dim, 1.0)

                # EMA 公式：(1-α)×old + α×new×weight
                ema_score = (1 - alpha) * old_score + alpha * new_raw * weight

                # 单次更新上限 cap = ±15 分，防止单次异常提交导致矩阵失真
                delta = ema_score - old_score
                delta = max(-EMA_DELTA_CAP, min(EMA_DELTA_CAP, delta))
                final_score = old_score + delta

                # 夹在 0~100 之间
                new_scores[dim] = round(max(0.0, min(100.0, final_score)), 2)

            cursor.execute("""
                UPDATE ability_matrix
                SET syntax_score = %s, algorithm_score = %s, project_score = %s,
                    debug_score = %s, security_score = %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (
                new_scores['syntax_score'],
                new_scores['algorithm_score'],
                new_scores['project_score'],
                new_scores['debug_score'],
                new_scores['security_score'],
                user_id
            ))

        conn.commit()
        return get_ability_matrix(user_id)
    except Exception as e:
        logging.error(f"更新能力矩阵失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def get_weak_dimensions(user_id):
    """获取用户的薄弱维度"""
    result, status = get_ability_matrix(user_id)
    if status != 200 or 'matrix' not in result:
        return result, status

    matrix = result['matrix']
    scores_map = {dim: matrix.get(dim, 0) or 0 for dim in ABILITY_DIMENSIONS}

    weak_dimensions = diagnose_weak_dimensions(scores_map)
    scores = [scores_map.get(dim, 0) for dim in ABILITY_DIMENSIONS]
    avg_score = sum(scores) / len(scores) if scores else 0

    return {"weak_dimensions": weak_dimensions, "average_score": round(avg_score, 2)}, 200


# ============================================================
# 能力矩阵 UPSERT 入口（服务层常用）
# ============================================================
def upsert_ability_matrix(user_id, syntax_score=None, algorithm_score=None,
                          project_score=None, debug_score=None, security_score=None):
    """直接插入或更新能力矩阵（纯数字参数形式，服务层/脚本便捷入口）"""
    scores = {}
    if syntax_score is not None:
        scores["syntax_score"] = syntax_score
    if algorithm_score is not None:
        scores["algorithm_score"] = algorithm_score
    if project_score is not None:
        scores["project_score"] = project_score
    if debug_score is not None:
        scores["debug_score"] = debug_score
    if security_score is not None:
        scores["security_score"] = security_score
    if not scores:
        return {"error": "至少提供一个分数"}, 400
    result, status = update_ability_matrix(user_id, scores)
    # 让调用方直接拿到 dict，不需要 (result, 200) 的 tuple
    if status != 200:
        return None
    matrix = result.get("matrix")
    # 展开为简洁的单层 dict（与 insert 形参一致）
    if matrix:
        flat = {
            "user_id": matrix.get("user_id"),
            "syntax_score": matrix.get("syntax_score"),
            "algorithm_score": matrix.get("algorithm_score"),
            "project_score": matrix.get("project_score"),
            "debug_score": matrix.get("debug_score"),
            "security_score": matrix.get("security_score"),
            "updated_at": matrix.get("updated_at"),
            "dimensions": matrix.get("dimensions"),
        }
        return flat
    return None


# ============================================================
# 提交记录：建表 + save_submission + get_submission_history
# ============================================================
def _ensure_submission_table():
    """创建 ability_submissions 表（首次调用自动执行）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ability_submissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                source_type VARCHAR(50) NOT NULL,
                source_id VARCHAR(100),
                scores_json TEXT,
                detail_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
    except Exception as e:
        logging.warning(f"创建 ability_submissions 表跳过: {e}")
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def save_submission(user_id, source_type, source_id=None, scores=None, detail=None):
    """保存一次能力评估提交记录（Service 层调用入口）"""
    _ensure_submission_table()
    try:
        import json as _json
        conn = get_db_connection()
        cur = conn.cursor()
        scores_str = _json.dumps(scores or {}, ensure_ascii=False)
        detail_str = _json.dumps(detail or {}, ensure_ascii=False)
        cur.execute("""
            INSERT INTO ability_submissions
            (user_id, source_type, source_id, scores_json, detail_json)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, source_type, source_id, scores_str, detail_str))
        conn.commit()
        return {"message": "提交记录已保存"}, 200
    except Exception as e:
        logging.error(f"save_submission 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


# ---- 便捷别名（测试脚本常用） ----
def save_submission_record(user_id, source_type, source_id, scores=None):
    """兼容测试脚本中使用的别名"""
    return save_submission(user_id=user_id, source_type=source_type,
                           source_id=str(source_id) if source_id is not None else None,
                           scores=scores)


def get_submission_history(user_id, limit=30):
    """获取用户能力评估提交历史"""
    _ensure_submission_table()
    import json as _json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_id, source_type, source_id, scores_json, detail_json, created_at
            FROM ability_submissions
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        rows = fetch_dict(cur)
        records = []
        for r in rows:
            try:
                scores = _json.loads(r.get("scores_json") or "{}")
            except Exception:
                scores = {}
            try:
                detail = _json.loads(r.get("detail_json") or "{}")
            except Exception:
                detail = {}
            # 前端期望扁平字段：syntax_score / algorithm_score / ...
            flat = {
                "id": r.get("id"),
                "source_type": r.get("source_type"),
                "source": r.get("source_type"),  # 前端别名
                "source_id": r.get("source_id"),
                "scores": scores,
                "detail": detail,
                "created_at": str(r.get("created_at")) if r.get("created_at") else None,
            }
            for dim in ABILITY_DIMENSIONS:
                flat[dim] = scores.get(dim, 0)
            records.append(flat)
        return {"history": records, "count": len(records)}, 200
    except Exception as e:
        logging.error(f"get_submission_history 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


# ============================================================
# 能力趋势 + 推荐
# ============================================================
def get_ability_trend(user_id, dimension, days=30):
    """基于提交历史拟合用户某维度的能力变化趋势（N=5 个采样点）"""
    if dimension not in ABILITY_DIMENSIONS:
        return {"error": f"未知维度 {dimension}"}, 400
    hist_result, hist_status = get_submission_history(user_id, limit=200)
    if hist_status != 200:
        return hist_result, hist_status
    history = sorted(
        hist_result.get("history", []),
        key=lambda x: x.get("created_at") or ""
    )
    samples = min(5, len(history))
    if samples <= 1:
        # 数据不足，退化用当前能力矩阵的单值
        matrix_result, _ = get_ability_matrix(user_id)
        matrix = matrix_result.get("matrix", {}) if isinstance(matrix_result, dict) else {}
        score = matrix.get(dimension, 0)
        return {"trend": [{"point": i + 1, "score": score} for i in range(max(samples, 1))]}, 200

    # 等间隔采样
    trend = []
    step = len(history) / samples
    for i in range(samples):
        idx = int(i * step)
        item = history[idx]
        score = float((item.get("scores") or {}).get(dimension) or 0)
        trend.append({
            "point": i + 1,
            "score": round(score, 2),
            "created_at": item.get("created_at"),
        })
    return {"trend": trend, "dimension": dimension, "days": days}, 200


# ============================================================
# 真实题库推荐查询（对应文档 §10.2.2）
# 替代 ability_matrix_calculator.get_recommended_tasks 的硬编码列表
# ============================================================
def fetch_recommended_problems(user_id, dimension, score, limit=5):
    """
    从 problems 表按维度标签 + 难度 + 去重查询真实题目

    实现文档 §10.2.2：
    1. 通过 dimension_tag_mapping 映射维度→题库标签
    2. 根据 score 自适应选择难度
    3. 联表 answer_records 过滤已做题（去重）
    4. 降级：标签匹配为空 → 仅按难度过滤；无匹配题 → 回退到 calculator 硬编码

    参数:
        user_id (int): 用户ID
        dimension (str): 能力维度字段名，如 'algorithm_score'
        score (float): 用户在该维度的当前得分
        limit (int): 返回题目数量上限
    返回:
        list[dict]: 推荐题目列表，格式兼容原 get_recommended_tasks
            [{title, type, difficulty, question_id, tags}, ...]
    """
    # 延迟导入避免循环依赖
    from app.utils.dimension_tag_mapping import (
        build_tag_regex, map_score_to_difficulty
    )
    from app.utils.ability_matrix_calculator import get_recommended_tasks

    difficulty = map_score_to_difficulty(score)
    tag_regex = build_tag_regex(dimension)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取用户已做题 ID 集合（用于去重，对应文档 §10.2.2）
        # answer_records.question_id 是 VARCHAR(50)，problems.id 是 INT
        # 用 CAST 转换确保 NOT IN 正确匹配
        try:
            cursor.execute("""
                SELECT DISTINCT CAST(question_id AS UNSIGNED) AS qid
                FROM answer_records
                WHERE user_id = %s
                  AND question_id REGEXP '^[0-9]+$'
            """, (user_id,))
            done_rows = fetch_dict(cursor)
            done_ids = [int(r.get('qid', 0)) for r in done_rows if r.get('qid')]
        except Exception:
            done_ids = []

        # 构建去重 SQL 片段
        done_filter = ""
        params = []
        if done_ids:
            placeholders = ','.join(['%s'] * len(done_ids))
            done_filter = f" AND p.id NOT IN ({placeholders})"
            params.extend(done_ids)

        # 主查询：按难度 + 标签正则匹配
        # 对应文档 §10.2.2 真实题库查询
        base_sql = """
            SELECT p.id, p.title, p.difficulty, p.tags
            FROM problems p
            WHERE p.difficulty = %s
        """
        params_with_diff = [difficulty] + params

        if tag_regex:
            tag_clause = " AND (p.tags REGEXP %s)"
            sql = base_sql + tag_clause + done_filter + " ORDER BY p.id LIMIT %s"
            final_params = params_with_diff + [tag_regex, limit]
        else:
            # 降级：维度无标签映射 → 仅按难度过滤
            sql = base_sql + done_filter + " ORDER BY p.id LIMIT %s"
            final_params = params_with_diff + [limit]

        cursor.execute(sql, final_params)
        rows = fetch_dict(cursor)

        if not rows:
            # 二次降级：目标难度无匹配题 → 放宽难度限制，仅按标签匹配
            if tag_regex:
                sql_fallback = """
                    SELECT p.id, p.title, p.difficulty, p.tags
                    FROM problems p
                    WHERE (p.tags REGEXP %s)
                """ + done_filter + " ORDER BY p.id LIMIT %s"
                cursor.execute(sql_fallback, [tag_regex] + params + [limit])
                rows = fetch_dict(cursor)

        if not rows:
            # 三次降级：题库无匹配题 → 回退到 calculator 硬编码列表（保证可用性）
            return get_recommended_tasks(dimension)[:limit]

        # 转换为兼容原 tasks 格式
        result = []
        for r in rows:
            result.append({
                'title': r.get('title', ''),
                'type': 'practice',
                'difficulty': r.get('difficulty', difficulty),
                'question_id': str(r.get('id', '')),
                'tags': r.get('tags', '')
            })
        return result

    except Exception as e:
        logging.error(f"fetch_recommended_problems 失败，回退到硬编码: {e}")
        # 异常降级：返回硬编码列表，保证推荐功能可用
        return get_recommended_tasks(dimension)[:limit]
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


# ============================================================
# 群体分位对比（对应文档 §6.3 用户群体分位对比）
# 计算用户在所有用户中的百分位排名
# ============================================================
def get_user_percentile(user_id):
    """
    计算用户在所有用户中的能力百分位排名

    对应文档 §6.3：展示"您的算法能力超过 68% 的同阶段用户"
    算法：对每个维度，统计得分低于当前用户的用户数占比

    参数:
        user_id (int): 用户ID
    返回:
        tuple: (result_dict, status_code)
            result_dict 含每个维度的百分位 + 综合百分位 + 总用户数
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取当前用户矩阵
        cursor.execute("""
            SELECT syntax_score, algorithm_score, project_score,
                   debug_score, security_score
            FROM ability_matrix
            WHERE user_id = %s
        """, (user_id,))
        current = fetch_one_dict(cursor)

        if current is None:
            return {"error": "用户能力矩阵不存在"}, 404

        # 获取总用户数
        cursor.execute("SELECT COUNT(*) AS total FROM ability_matrix")
        total_row = fetch_one_dict(cursor)
        total_users = int(total_row.get('total', 0)) if total_row else 0

        if total_users <= 1:
            return {
                "percentiles": {dim: 50.0 for dim in ABILITY_DIMENSIONS},
                "overall_percentile": 50.0,
                "total_users": total_users,
                "note": "用户样本不足，暂无对比数据"
            }, 200

        # 计算每个维度的百分位
        percentiles = {}
        for dim in ABILITY_DIMENSIONS:
            user_score = float(current.get(dim, 0) or 0)
            # 统计得分低于当前用户的用户数
            cursor.execute(f"""
                SELECT COUNT(*) AS below_count
                FROM ability_matrix
                WHERE {dim} < %s
            """, (user_score,))
            row = fetch_one_dict(cursor)
            below_count = int(row.get('below_count', 0)) if row else 0
            # 百分位 = 低于自己的人数 / 总人数 × 100
            percentile = round(below_count / total_users * 100, 1)
            percentiles[dim] = percentile

        # 综合百分位（5 维平均分对应的百分位）
        avg_score = sum(float(current.get(d, 0) or 0) for d in ABILITY_DIMENSIONS) / len(ABILITY_DIMENSIONS)
        cursor.execute("""
            SELECT COUNT(*) AS below_count
            FROM ability_matrix
            WHERE (syntax_score + algorithm_score + project_score + debug_score + security_score) / 5 < %s
        """, (avg_score,))
        overall_row = fetch_one_dict(cursor)
        overall_below = int(overall_row.get('below_count', 0)) if overall_row else 0
        overall_percentile = round(overall_below / total_users * 100, 1)

        return {
            "percentiles": percentiles,
            "overall_percentile": overall_percentile,
            "total_users": total_users,
            "user_scores": {dim: float(current.get(dim, 0) or 0) for dim in ABILITY_DIMENSIONS},
            "note": f"您的综合能力超过 {overall_percentile}% 的用户"
        }, 200

    except Exception as e:
        logging.error(f"get_user_percentile 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


# ============================================================
# 子维度细化（对应文档 §1.2.1 子维度细化设计）
# ============================================================

# 主维度 → 子维度定义（用于前端子雷达图展示）
SUB_DIMENSIONS = {
    'syntax_score': ['变量与类型', '控制流', '函数定义', 'PEP8规范', '注释文档'],
    'algorithm_score': ['排序', '查找', '动态规划', '递归', '贪心'],
    'project_score': ['面向对象', '模块化', '设计模式', '代码结构', '复用性'],
    'debug_score': ['异常捕获', '日志记录', '断点调试', '错误定位', '修复能力'],
    'security_score': ['输入验证', '注入防护', '加密解密', '权限控制', '安全编码'],
}


def get_user_subscores(user_id):
    """
    获取用户各维度的子维度细分分数

    对应文档 §1.2.1：5 主维度 → 子维度拆分，支持子雷达图展示

    参数:
        user_id (int): 用户ID
    返回:
        tuple: (result_dict, status_code)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询用户已保存的子维度分数
        cursor.execute("""
            SELECT dimension, sub_dimension, score
            FROM ability_subscores
            WHERE user_id = %s
        """, (user_id,))
        rows = fetch_dict(cursor)

        # 构建子维度字典 {dimension: {sub_dimension: score}}
        saved = {}
        for r in rows:
            dim = r.get('dimension', '')
            sub = r.get('sub_dimension', '')
            score = float(r.get('score', 0) or 0)
            if dim not in saved:
                saved[dim] = {}
            saved[dim][sub] = score

        # 按主维度组织返回结果，未记录的子维度默认 0
        result = {}
        for dim, sub_list in SUB_DIMENSIONS.items():
            result[dim] = {
                'label': DIMENSION_LABELS.get(dim, dim),
                'sub_dimensions': []
            }
            dim_saved = saved.get(dim, {})
            for sub in sub_list:
                result[dim]['sub_dimensions'].append({
                    'name': sub,
                    'score': dim_saved.get(sub, 0.0)
                })

        return {
            "subscores": result,
            "dimension_labels": {dim: DIMENSION_LABELS.get(dim, dim) for dim in SUB_DIMENSIONS},
            "note": "子维度数据支持前端子雷达图展示"
        }, 200

    except Exception as e:
        logging.error(f"get_user_subscores 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


def save_subscores(user_id, dimension, sub_scores):
    """
    保存用户某维度的子维度分数（UPSERT）

    参数:
        user_id (int): 用户ID
        dimension (str): 主维度字段名
        sub_scores (dict): {子维度名: 分数}
    返回:
        tuple: (result_dict, status_code)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        for sub_name, score in sub_scores.items():
            cursor.execute("""
                INSERT INTO ability_subscores (user_id, dimension, sub_dimension, score)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE score = VALUES(score), updated_at = CURRENT_TIMESTAMP
            """, (user_id, dimension, sub_name, float(score)))

        conn.commit()
        return {"message": f"子维度分数已保存: {dimension}"}, 200

    except Exception as e:
        logging.error(f"save_subscores 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


# ============================================================
# 内容推荐：标签相似度（对应文档 §10.3.1 标签相似度推荐）
# ============================================================
def content_based_recommendations(user_id, limit=5):
    """
    基于内容的推荐：标签相似度

    对应文档 §10.3.1：
    1. 获取用户答对题目的标签集合
    2. 查询标签相似但用户未做过的新题
    3. 按标签命中数排序

    参数:
        user_id (int): 用户ID
        limit (int): 返回题目数量
    返回:
        tuple: (result_dict, status_code)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 获取用户答对题目的标签集合
        cursor.execute("""
            SELECT DISTINCT p.tags
            FROM answer_records ar
            INNER JOIN problems p ON CAST(ar.question_id AS UNSIGNED) = p.id
            WHERE ar.user_id = %s AND ar.is_correct = 1
              AND p.tags IS NOT NULL AND p.tags != ''
        """, (user_id,))
        tag_rows = fetch_dict(cursor)

        # 解析标签
        user_tags = set()
        for r in tag_rows:
            tags_str = r.get('tags', '') or ''
            for t in tags_str.split(','):
                t = t.strip()
                if t:
                    user_tags.add(t)

        if not user_tags:
            return {
                "recommendations": [],
                "count": 0,
                "note": "暂无答对记录，无法生成内容推荐"
            }, 200

        # 2. 获取已做题
        cursor.execute("""
            SELECT DISTINCT CAST(question_id AS UNSIGNED) AS qid
            FROM answer_records
            WHERE user_id = %s AND question_id REGEXP '^[0-9]+$'
        """, (user_id,))
        done_rows = fetch_dict(cursor)
        done_ids = [int(r.get('qid', 0)) for r in done_rows if r.get('qid')]

        # 3. 查询标签相似的新题
        tag_regex = '|'.join(list(user_tags)[:10])
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

        cursor.execute(sql, [tag_regex] + params + [limit * 2])
        rows = fetch_dict(cursor)

        # 4. 计算标签命中数并排序
        recommendations = []
        for r in rows:
            question_tags = [t.strip() for t in (r.get('tags', '') or '').split(',') if t.strip()]
            hit_count = sum(1 for t in question_tags if t in user_tags)
            recommendations.append({
                'question_id': str(r.get('id', '')),
                'title': r.get('title', ''),
                'difficulty': r.get('difficulty', '未知'),
                'tags': r.get('tags', ''),
                'tag_hits': hit_count,
                'reason': f'与你已掌握题目标签相似（命中 {hit_count} 个标签）'
            })

        # 按标签命中数降序
        recommendations.sort(key=lambda x: x['tag_hits'], reverse=True)
        recommendations = recommendations[:limit]

        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "user_tags": list(user_tags)[:10],
            "note": "基于内容推荐，推荐与你已掌握题目标签相似的新题"
        }, 200

    except Exception as e:
        logging.error(f"content_based_recommendations 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()


# ============================================================
# 错题标签聚类加权推荐（对应文档 §10.3.2）
# ============================================================
def error_weighted_recommendations(user_id, limit=5):
    """
    基于错题标签聚类的加权推荐

    对应文档 §10.3.2：
    1. 获取用户错题的高频 tags（错误集中的知识点）
    2. 对错题集中的标签加权提升推荐优先级
    3. 优先推荐错题标签相关的、用户未做过的题

    参数:
        user_id (int): 用户ID
        limit (int): 返回题目数量
    返回:
        tuple: (result_dict, status_code)
    """
    # 延迟导入避免循环依赖
    from app.models.error_diagnosis_model import diagnose_error_patterns

    # 获取错题标签聚类
    error_result, error_status = diagnose_error_patterns(user_id, limit=50)
    if error_status != 200:
        return error_result, error_status

    weak_tags = [item['tag'] for item in error_result.get('weak_tags', [])]
    if not weak_tags:
        return {
            "recommendations": [],
            "count": 0,
            "note": "暂无错题记录或错题无标签"
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

        # 查询错题标签相关的题目
        tag_regex = '|'.join(weak_tags[:5])
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

        cursor.execute(sql, [tag_regex] + params + [limit * 2])
        rows = fetch_dict(cursor)

        # 按错题标签命中数加权排序
        recommendations = []
        weak_tag_set = set(weak_tags[:5])
        for r in rows:
            question_tags = [t.strip() for t in (r.get('tags', '') or '').split(',') if t.strip()]
            # 错题标签命中数（权重更高）
            weak_hits = sum(1 for t in question_tags if t in weak_tag_set)
            recommendations.append({
                'question_id': str(r.get('id', '')),
                'title': r.get('title', ''),
                'difficulty': r.get('difficulty', '未知'),
                'tags': r.get('tags', ''),
                'weak_tag_hits': weak_hits,
                'reason': f'针对你错题高频知识点（{",".join(weak_tags[:3])}）的强化练习'
            })

        # 按错题标签命中数降序
        recommendations.sort(key=lambda x: x['weak_tag_hits'], reverse=True)
        recommendations = recommendations[:limit]

        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "weak_tags": weak_tags[:5],
            "note": "基于错题标签聚类加权，优先推荐薄弱知识点的强化题"
        }, 200

    except Exception as e:
        logging.error(f"error_weighted_recommendations 失败: {e}")
        return {"error": f"数据库错误: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()
