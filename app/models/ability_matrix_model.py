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
            INSERT INTO ability_matrix (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
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
    """更新用户的能力矩阵"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT syntax_score, algorithm_score, project_score,
                   debug_score, security_score
            FROM ability_matrix
            WHERE user_id = %s
        """, (user_id,))
        current = fetch_one_dict(cursor)

        if current is None:
            cursor.execute("""
                INSERT INTO ability_matrix
                (user_id, syntax_score, algorithm_score, project_score,
                 debug_score, security_score, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                user_id,
                scores.get('syntax_score', 0),
                scores.get('algorithm_score', 0),
                scores.get('project_score', 0),
                scores.get('debug_score', 0),
                scores.get('security_score', 0)
            ))
        else:
            new_scores = {}
            for dim in ABILITY_DIMENSIONS:
                old_score = current.get(dim, 0) or 0
                new_score = scores.get(dim, 0)
                new_scores[dim] = round((old_score + new_score) / 2, 2)

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
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                source_type VARCHAR(50) NOT NULL,
                source_id VARCHAR(100),
                scores_json TEXT,
                detail_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
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
